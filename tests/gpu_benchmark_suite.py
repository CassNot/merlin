# MIT License
#
# Copyright (c) 2025 Quandela
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
GPU benchmark suite for MerLin's ``QuantumLayer``.

This is a from-scratch replacement for the ad-hoc ``tests/memory_benchmark.py``
script referenced from ``docs/source/performance/performance.rst``. That script
produces numbers that are not trustworthy for a few concrete reasons that this
suite fixes:

- CUDA kernels are launched asynchronously. Timing a call with ``time.time()``
  without a ``torch.cuda.synchronize()`` around it mostly measures kernel
  *launch* overhead, not the actual GPU compute time. Every timed section here
  is synchronized.
- GPU memory was read from whole-device ``nvidia-smi``/``pynvml`` snapshots,
  which include every other process sharing the GPU (common on shared/cloud
  boxes) and are only point-in-time samples, not the peak usage of the run.
  Here we use ``torch.cuda.max_memory_allocated`` / ``max_memory_reserved``
  (reset per configuration) which report the actual peak footprint of this
  process for that configuration.
- The old script had a hard, undeclared dependency on ``pynvml``/
  ``pynvml_utils`` (neither is in ``pyproject.toml``) and crashed on import if
  unavailable. Here, GPU-native ``torch.cuda`` stats are the primary metric;
  ``pynvml`` is only used opportunistically for an informational whole-device
  reading and is never required.
- ``--type`` was declared with ``default=torch.float32`` but ``type=str``, so
  passing a dtype on the CLI produced a plain string that was later fed
  straight into ``torch.rand(..., dtype=...)``, raising immediately. Dtypes
  are now parsed through an explicit string -> ``torch.dtype`` map.
- The first iteration of any new configuration pays for CUDA context/allocator
  warm-up. That cost was folded into the reported averages. Here a
  configurable number of warm-up iterations run before timing/memory starts.

What is benchmarked
--------------------
For a ``GenericInterferometer`` with ``m`` modes (``2*m*(m-1)`` trainable
angles split into ``theta``/``phase`` prefixes), we train a batch of
independently-parameterized copies of the interferometer to match a fixed
target distribution -- this is deliberately the heaviest workload for the
underlying batched permanent/SLOS computation, since every batch row uses a
distinct unitary (as opposed to a classical NN pattern where only a small
classical input varies while circuit weights are shared across the batch).

Three sweeps are available:

- ``batch``:   memory + time vs. batch size, for ``m`` modes / ``m // 2``
  photons (mirrors ``SW-BS.png`` / ``SW-times.png``).
- ``photons``: memory + time vs. number of photons (1 to ``m // 2``), for a
  handful of representative mode counts, at batch size 1 (mirrors
  ``SW-photons.png`` / ``SW-layer-photons.png`` / ``SW-times-photons.png``).
- ``noise``:   the same workload with vs. without a ``perceval.NoiseModel``
  (brightness + transmittance) attached via ``perceval.Experiment``, to
  measure the memory/time overhead introduced by photon-loss simulation.

Per the task constraints, sweeps never exceed 24 modes or 12 photons, and
never use more than ``m // 2`` photons for ``m`` modes.

Usage
-----
.. code-block:: bash

    # Quick single-configuration smoke test
    python tests/gpu_benchmark_suite.py --sweep single --modes 8 --photons 4 --bs 32

    # Full memory-vs-batch-size sweep (m=2..24 step 2, m//2 photons)
    python tests/gpu_benchmark_suite.py --sweep batch

    # Memory/time-vs-photon-count sweep, batch size 1
    python tests/gpu_benchmark_suite.py --sweep photons

    # NoiseModel overhead sweep
    python tests/gpu_benchmark_suite.py --sweep noise

    # Everything (batch + photons + noise)
    python tests/gpu_benchmark_suite.py --sweep all
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import time
from dataclasses import asdict, dataclass

import pandas as pd
import perceval as pcvl
import torch

import merlin as ML

MAX_MODES = 24
MAX_PHOTONS = 12

DTYPE_MAP = {
    "float32": torch.float32,
    "float64": torch.float64,
    "complex64": torch.complex64,
    "complex128": torch.complex128,
}


def parse_dtype(value: str) -> torch.dtype:
    """Parse a CLI dtype string (e.g. ``float64`` or ``torch.float64``)."""
    key = value.replace("torch.", "").strip().lower()
    if key not in DTYPE_MAP:
        raise argparse.ArgumentTypeError(
            f"Unsupported dtype '{value}'. Choose from: {sorted(DTYPE_MAP)}"
        )
    return DTYPE_MAP[key]


def parse_int_list(value: str) -> list[int]:
    return [int(v) for v in value.split(",") if v.strip()]


def validate_modes_photons(n_modes: int, n_photons: int) -> None:
    """Enforce this suite's hard caps: <=24 modes, <=12 photons, photons <= m//2."""
    if n_modes < 2:
        raise ValueError("n_modes must be >= 2")
    if n_modes > MAX_MODES:
        raise ValueError(f"n_modes={n_modes} exceeds the maximum of {MAX_MODES}")
    if n_photons < 1:
        raise ValueError("n_photons must be >= 1")
    if n_photons > MAX_PHOTONS:
        raise ValueError(f"n_photons={n_photons} exceeds the maximum of {MAX_PHOTONS}")
    if n_photons > n_modes // 2:
        raise ValueError(
            f"n_photons={n_photons} exceeds n_modes // 2 = {n_modes // 2} "
            f"for n_modes={n_modes}"
        )


def build_interferometer_circuit(n_modes: int) -> pcvl.Circuit:
    """Generic interferometer with independently-named theta/phase prefixes."""
    return pcvl.GenericInterferometer(
        n_modes,
        lambda i: (
            pcvl.BS(theta=pcvl.P(f"theta_1_{i}"))
            .add(0, pcvl.PS(pcvl.P(f"phase_1_{i}")))
            .add(0, pcvl.BS(theta=pcvl.P(f"theta_2_{i}")))
            .add(0, pcvl.PS(pcvl.P(f"phase_2_{i}")))
        ),
    )


def build_input_state(n_modes: int, n_photons: int) -> list[int]:
    """Evenly-spaced input state, e.g. [1,0,1,0,...] for n_photons photons."""
    state = [0] * n_modes
    for k in range(n_photons):
        state[2 * k] = 1
    return state


def count_params_by_prefix(circuit: pcvl.Circuit, prefix: str) -> int:
    return len([p.name for p in circuit.get_parameters() if p.name.startswith(prefix)])


@dataclass
class BenchmarkResult:
    n_modes: int
    n_photons: int
    batch_size: int
    dtype: str
    noisy: bool
    device: str
    n_parameters: int
    graph_build_time_s: float | None = None
    forward_time_mean_s: float | None = None
    forward_time_std_s: float | None = None
    backward_time_mean_s: float | None = None
    backward_time_std_s: float | None = None
    peak_allocated_mb: float | None = None
    peak_reserved_mb: float | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _mean_std(values: list[float]) -> tuple[float, float]:
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return mean, var**0.5


def build_layer(
    n_modes: int,
    n_photons: int,
    dtype: torch.dtype,
    device: torch.device,
    noisy: bool,
    noise_brightness: float,
    noise_transmittance: float,
) -> tuple[ML.QuantumLayer, int, int]:
    """Build the QuantumLayer under test. Returns (layer, n_phase_params, n_theta_params)."""
    circuit = build_interferometer_circuit(n_modes)
    input_state = build_input_state(n_modes, n_photons)
    n_phase = count_params_by_prefix(circuit, "phase")
    n_theta = count_params_by_prefix(circuit, "theta")

    # Photon loss can change the photon number, so the full Fock space is
    # required once noise is present; the noiseless baseline uses the same
    # computation space in the noise sweep so the comparison isolates the
    # noise overhead rather than an unrelated computation-space effect.
    computation_space = ML.ComputationSpace.FOCK if noisy else ML.ComputationSpace.UNBUNCHED

    common_kwargs = {
        "input_size": n_phase + n_theta,
        "input_state": input_state,
        "trainable_parameters": [],
        "input_parameters": ["phase", "theta"],
        "measurement_strategy": ML.MeasurementStrategy.probs(
            computation_space=computation_space
        ),
        "device": device,
        "dtype": dtype,
    }

    if noisy:
        experiment = pcvl.Experiment(circuit)
        experiment.noise = pcvl.NoiseModel(
            brightness=noise_brightness, transmittance=noise_transmittance
        )
        layer = ML.QuantumLayer(experiment=experiment, **common_kwargs)
    else:
        layer = ML.QuantumLayer(circuit=circuit, **common_kwargs)

    return layer, n_phase, n_theta


def run_config(
    n_modes: int,
    n_photons: int,
    batch_size: int,
    dtype: torch.dtype,
    device: torch.device,
    n_epochs: int = 5,
    n_warmup: int = 2,
    noisy: bool = False,
    noise_brightness: float = 0.9,
    noise_transmittance: float = 0.9,
) -> BenchmarkResult:
    """Run one (modes, photons, batch_size) configuration and collect metrics."""
    validate_modes_photons(n_modes, n_photons)
    is_cuda = device.type == "cuda"

    result = BenchmarkResult(
        n_modes=n_modes,
        n_photons=n_photons,
        batch_size=batch_size,
        dtype=str(dtype).replace("torch.", ""),
        noisy=noisy,
        device=str(device),
        n_parameters=0,
    )

    try:
        if is_cuda:
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats(device)

        t0 = time.perf_counter()
        layer, n_phase, n_theta = build_layer(
            n_modes, n_photons, dtype, device, noisy, noise_brightness, noise_transmittance
        )
        if is_cuda:
            torch.cuda.synchronize(device)
        result.graph_build_time_s = time.perf_counter() - t0
        result.n_parameters = n_phase + n_theta

        with torch.no_grad():
            target_phases = 2 * torch.pi * torch.rand(
                (batch_size, n_phase), dtype=dtype, device=device
            )
            target_thetas = torch.rand((batch_size, n_theta), dtype=dtype, device=device)
            target_distribution = layer(target_phases, target_thetas)

        phases = torch.rand(
            (batch_size, n_phase), dtype=dtype, device=device, requires_grad=True
        )
        thetas = torch.rand(
            (batch_size, n_theta), dtype=dtype, device=device, requires_grad=True
        )
        optimizer = torch.optim.Adam([phases, thetas], lr=0.001)
        criterion = torch.nn.MSELoss(reduction="sum")

        def step():
            optimizer.zero_grad()

            if is_cuda:
                torch.cuda.synchronize(device)
            t_fwd0 = time.perf_counter()
            probs = layer(phases, thetas)
            if is_cuda:
                torch.cuda.synchronize(device)
            fwd_time = time.perf_counter() - t_fwd0

            loss = criterion(probs, target_distribution)

            t_bwd0 = time.perf_counter()
            loss.backward()
            if is_cuda:
                torch.cuda.synchronize(device)
            bwd_time = time.perf_counter() - t_bwd0

            optimizer.step()
            return fwd_time, bwd_time

        for _ in range(n_warmup):
            step()

        if is_cuda:
            torch.cuda.synchronize(device)
            torch.cuda.reset_peak_memory_stats(device)

        fwd_times, bwd_times = [], []
        for _ in range(n_epochs):
            fwd_time, bwd_time = step()
            fwd_times.append(fwd_time)
            bwd_times.append(bwd_time)

        result.forward_time_mean_s, result.forward_time_std_s = _mean_std(fwd_times)
        result.backward_time_mean_s, result.backward_time_std_s = _mean_std(bwd_times)

        if is_cuda:
            result.peak_allocated_mb = torch.cuda.max_memory_allocated(device) / (1024**2)
            result.peak_reserved_mb = torch.cuda.max_memory_reserved(device) / (1024**2)

    except torch.cuda.OutOfMemoryError as exc:
        # Record and keep sweeping instead of aborting the whole run.
        result.error = f"OutOfMemoryError: {exc}"
        if is_cuda:
            torch.cuda.empty_cache()
    except Exception as exc:  # noqa: BLE001 - surface any failure and keep sweeping
        result.error = f"{type(exc).__name__}: {exc}"
    finally:
        gc.collect()
        if is_cuda:
            torch.cuda.empty_cache()

    return result


def print_config_result(result: BenchmarkResult) -> None:
    if result.error:
        print(
            f"  m={result.n_modes:>3} photons={result.n_photons:>2} bs={result.batch_size:>5} "
            f"noisy={result.noisy}  -> FAILED: {result.error}"
        )
        return
    mem = (
        f"peak_alloc={result.peak_allocated_mb:8.2f}MB"
        if result.peak_allocated_mb is not None
        else "peak_alloc=   n/a"
    )
    print(
        f"  m={result.n_modes:>3} photons={result.n_photons:>2} bs={result.batch_size:>5} "
        f"noisy={result.noisy!s:<5} graph_build={result.graph_build_time_s * 1000:8.2f}ms "
        f"fwd={result.forward_time_mean_s * 1000:8.2f}ms "
        f"bwd={result.backward_time_mean_s * 1000:8.2f}ms  {mem}"
    )


def sweep_batch(
    device: torch.device,
    dtype: torch.dtype,
    max_modes: int,
    mode_step: int,
    batch_sizes: list[int],
    n_epochs: int,
    n_warmup: int,
) -> list[BenchmarkResult]:
    """Memory + time vs. batch size, for m modes / m//2 photons."""
    print("\n=== Sweep: memory & time vs. batch size (n_photons = n_modes // 2) ===")
    results = []
    for n_modes in range(2, max_modes + 1, mode_step):
        n_photons = min(n_modes // 2, MAX_PHOTONS)
        for batch_size in batch_sizes:
            result = run_config(
                n_modes,
                n_photons,
                batch_size,
                dtype,
                device,
                n_epochs=n_epochs,
                n_warmup=n_warmup,
            )
            print_config_result(result)
            results.append(result)
    return results


def sweep_photons(
    device: torch.device,
    dtype: torch.dtype,
    mode_list: list[int],
    n_epochs: int,
    n_warmup: int,
) -> list[BenchmarkResult]:
    """Memory + time vs. number of photons (1..m//2), at batch_size=1."""
    print("\n=== Sweep: memory & time vs. number of photons (batch_size=1) ===")
    results = []
    for n_modes in mode_list:
        max_photons = min(n_modes // 2, MAX_PHOTONS)
        for n_photons in range(1, max_photons + 1):
            result = run_config(
                n_modes,
                n_photons,
                batch_size=1,
                dtype=dtype,
                device=device,
                n_epochs=n_epochs,
                n_warmup=n_warmup,
            )
            print_config_result(result)
            results.append(result)
    return results


def sweep_noise(
    device: torch.device,
    dtype: torch.dtype,
    noise_modes: list[int],
    noise_batch_sizes: list[int],
    noise_brightness: float,
    noise_transmittance: float,
    n_epochs: int,
    n_warmup: int,
) -> list[BenchmarkResult]:
    """Noiseless vs. NoiseModel-attached overhead, across modes and batch sizes."""
    print(
        f"\n=== Sweep: NoiseModel overhead "
        f"(brightness={noise_brightness}, transmittance={noise_transmittance}) ==="
    )
    results = []

    fixed_batch = noise_batch_sizes[0]
    print(f"-- varying modes, batch_size={fixed_batch} --")
    for n_modes in noise_modes:
        n_photons = min(n_modes // 2, MAX_PHOTONS)
        for noisy in (False, True):
            result = run_config(
                n_modes,
                n_photons,
                fixed_batch,
                dtype,
                device,
                n_epochs=n_epochs,
                n_warmup=n_warmup,
                noisy=noisy,
                noise_brightness=noise_brightness,
                noise_transmittance=noise_transmittance,
            )
            print_config_result(result)
            results.append(result)

    fixed_modes = noise_modes[len(noise_modes) // 2]
    fixed_photons = min(fixed_modes // 2, MAX_PHOTONS)
    print(f"-- varying batch size, n_modes={fixed_modes}, n_photons={fixed_photons} --")
    for batch_size in noise_batch_sizes:
        for noisy in (False, True):
            result = run_config(
                fixed_modes,
                fixed_photons,
                batch_size,
                dtype,
                device,
                n_epochs=n_epochs,
                n_warmup=n_warmup,
                noisy=noisy,
                noise_brightness=noise_brightness,
                noise_transmittance=noise_transmittance,
            )
            print_config_result(result)
            results.append(result)

    return results


def print_noise_overhead_summary(results: list[BenchmarkResult]) -> None:
    df = pd.DataFrame([r.to_dict() for r in results])
    df = df[df["error"].isna()]
    if df.empty:
        print("\nNo successful noise-sweep runs to summarize.")
        return

    group_cols = ["n_modes", "n_photons", "batch_size"]
    pivot = df.pivot_table(
        index=group_cols,
        columns="noisy",
        values=["peak_allocated_mb", "forward_time_mean_s", "backward_time_mean_s"],
    )
    print("\n--- NoiseModel overhead (True=with NoiseModel, False=baseline) ---")
    print(pivot.to_string())


def save_results(results: list[BenchmarkResult], output_dir: str, name: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    records = [r.to_dict() for r in results]

    json_path = os.path.join(output_dir, f"{name}.json")
    with open(json_path, "w") as f:
        json.dump(records, f, indent=2)

    csv_path = os.path.join(output_dir, f"{name}.csv")
    pd.DataFrame(records).to_csv(csv_path, index=False)

    print(f"\nSaved {len(records)} results to {json_path} and {csv_path}")


def maybe_plot(results: list[BenchmarkResult], output_dir: str, name: str) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping plots (pip install matplotlib).")
        return

    df = pd.DataFrame([r.to_dict() for r in results])
    df = df[df["error"].isna()]
    if df.empty:
        return
    os.makedirs(output_dir, exist_ok=True)

    def _lineplot(x, y, group, ylabel, filename, logy=False):
        if x not in df.columns or df[x].nunique() < 2:
            return
        fig, ax = plt.subplots(figsize=(7, 5))
        for key, sub in df.groupby(group):
            sub = sub.sort_values(x)
            ax.plot(sub[x], sub[y], marker="o", label=f"{group}={key}")
        ax.set_xlabel(x)
        ax.set_ylabel(ylabel)
        if logy:
            ax.set_yscale("log")
        ax.legend(fontsize="small")
        ax.set_title(f"{ylabel} vs {x}")
        fig.tight_layout()
        fig.savefig(os.path.join(output_dir, filename), dpi=150)
        plt.close(fig)

    if not df["noisy"].any():
        _lineplot(
            "batch_size", "peak_allocated_mb", "n_modes",
            "Peak allocated memory (MB)", f"{name}_memory_vs_batch.png", logy=True,
        )
        _lineplot(
            "n_photons", "peak_allocated_mb", "n_modes",
            "Peak allocated memory (MB)", f"{name}_memory_vs_photons.png", logy=True,
        )
        _lineplot(
            "n_photons", "graph_build_time_s", "n_modes",
            "Graph build time (s)", f"{name}_graph_build_time_vs_photons.png",
        )
        _lineplot(
            "batch_size", "forward_time_mean_s", "n_modes",
            "Forward time (s)", f"{name}_forward_time_vs_batch.png", logy=True,
        )
        _lineplot(
            "batch_size", "backward_time_mean_s", "n_modes",
            "Backward time (s)", f"{name}_backward_time_vs_batch.png", logy=True,
        )
    print(f"Saved plots to {output_dir}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "GPU benchmark suite for MerLin's QuantumLayer: memory and timing "
            "(graph build / forward / backward) across modes, photon counts, "
            "batch sizes, plus a NoiseModel overhead sweep."
        )
    )
    parser.add_argument(
        "--sweep",
        choices=["single", "batch", "photons", "noise", "all"],
        default="all",
        help="Which sweep to run.",
    )
    parser.add_argument("--modes", type=int, default=8, help="[single] number of modes")
    parser.add_argument(
        "--photons", type=int, default=None, help="[single] number of photons (default: modes // 2)"
    )
    parser.add_argument("--bs", type=int, default=32, help="[single] batch size")

    parser.add_argument(
        "--batch-sizes",
        type=parse_int_list,
        default="1,2,4,8,16,32,64,128,256,512,1024,2048",
        help="[batch sweep] comma-separated batch sizes",
    )
    parser.add_argument(
        "--max-modes", type=int, default=MAX_MODES, help="[batch sweep] largest mode count (<=24)"
    )
    parser.add_argument(
        "--mode-step", type=int, default=2, help="[batch sweep] step between mode counts"
    )
    parser.add_argument(
        "--mode-list",
        type=parse_int_list,
        default=None,
        help="[photons sweep] comma-separated mode counts (default: 4,8,...,max-modes)",
    )

    parser.add_argument(
        "--noise-modes",
        type=parse_int_list,
        default=None,
        help="[noise sweep] comma-separated mode counts (default: every other mode-step value)",
    )
    parser.add_argument(
        "--noise-batch-sizes",
        type=parse_int_list,
        default="1,16,64,256",
        help="[noise sweep] comma-separated batch sizes",
    )
    parser.add_argument("--noise-brightness", type=float, default=0.9)
    parser.add_argument("--noise-transmittance", type=float, default=0.9)

    parser.add_argument("--epochs", type=int, default=5, help="Timed iterations per configuration")
    parser.add_argument(
        "--warmup", type=int, default=2, help="Untimed warm-up iterations per configuration"
    )
    parser.add_argument("--dtype", type=parse_dtype, default=torch.float32)
    parser.add_argument("--device", type=str, default=None, help="Override device, e.g. 'cuda:1'")
    parser.add_argument("--output-dir", type=str, default="./results")
    parser.add_argument("--plot", action="store_true", help="Also save PNG plots (needs matplotlib)")
    return parser


def resolve_device(device_arg: str | None) -> torch.device:
    if device_arg:
        return torch.device(device_arg)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def main() -> None:
    args = build_arg_parser().parse_args()
    device = resolve_device(args.device)

    print(f"Device: {device}")
    if device.type != "cuda":
        print(
            "WARNING: no CUDA device in use -- memory metrics will be unavailable "
            "(this suite targets GPU benchmarking, see docs/source/performance/performance.rst)."
        )

    if args.max_modes > MAX_MODES:
        raise ValueError(f"--max-modes cannot exceed {MAX_MODES}")

    if args.sweep in ("single",):
        n_photons = args.photons if args.photons is not None else args.modes // 2
        result = run_config(
            args.modes,
            n_photons,
            args.bs,
            args.dtype,
            device,
            n_epochs=args.epochs,
            n_warmup=args.warmup,
        )
        print_config_result(result)
        save_results([result], args.output_dir, "gpu_benchmark_single")
        return

    if args.sweep in ("batch", "all"):
        results = sweep_batch(
            device,
            args.dtype,
            args.max_modes,
            args.mode_step,
            args.batch_sizes,
            args.epochs,
            args.warmup,
        )
        save_results(results, args.output_dir, "gpu_benchmark_batch_sweep")
        if args.plot:
            maybe_plot(results, args.output_dir, "gpu_benchmark_batch_sweep")

    if args.sweep in ("photons", "all"):
        mode_list = args.mode_list or list(range(4, args.max_modes + 1, 2 * args.mode_step))
        mode_list = [m for m in mode_list if m <= args.max_modes]
        results = sweep_photons(device, args.dtype, mode_list, args.epochs, args.warmup)
        save_results(results, args.output_dir, "gpu_benchmark_photon_sweep")
        if args.plot:
            maybe_plot(results, args.output_dir, "gpu_benchmark_photon_sweep")

    if args.sweep in ("noise", "all"):
        noise_modes = args.noise_modes or list(
            range(4, args.max_modes + 1, 2 * args.mode_step)
        )
        noise_modes = [m for m in noise_modes if m <= args.max_modes]
        results = sweep_noise(
            device,
            args.dtype,
            noise_modes,
            args.noise_batch_sizes,
            args.noise_brightness,
            args.noise_transmittance,
            args.epochs,
            args.warmup,
        )
        save_results(results, args.output_dir, "gpu_benchmark_noise_sweep")
        print_noise_overhead_summary(results)


if __name__ == "__main__":
    main()
