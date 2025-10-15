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
Behavioural regression tests for feed-forward quantum layers and pooling blocks.

These tests focus on the branching logic, probabilistic consistency, and integration
with Perceval simulators to ensure refactors preserve semantics.
"""

import math
from collections import defaultdict

import pytest
import torch

from merlin.algorithms.feed_forward import (
    FeedForwardBlock,
    PoolingFeedForward,
    define_layer_no_input,
)


class TestFeedForwardBlock:
    """Comprehensive test suite for FeedForwardBlock."""

    def test_init_single_mode(self):
        """Test initialization with single conditional mode."""
        ff = FeedForwardBlock(input_size=6, m=6, n=2, depth=3, conditional_modes=[0])
        assert ff.m == 6
        assert ff.n_photons == 2
        assert ff.conditional_modes == [0]
        assert ff.depth == 3
        assert isinstance(ff.layers, dict)

    def test_init_multi_mode(self):
        """Test initialization with multiple conditional modes."""
        ff = FeedForwardBlock(input_size=6, m=6, n=2, depth=2, conditional_modes=[0, 1])
        assert ff.n_cond == 2
        assert all(isinstance(k, tuple) for k in ff.layers.keys())

    def test_generate_possible_tuples(self):
        """Ensure generated tuples are non-empty and valid."""
        ff = FeedForwardBlock(input_size=4, n=2, m=4, conditional_modes=[0, 1])
        tuples = ff.generate_possible_tuples()
        assert isinstance(tuples, list)
        assert len(tuples) > 0
        assert all(isinstance(t, tuple) for t in tuples)

    def test_generate_possible_tuples_respect_constraints(self):
        """No tuple should violate photon/empty-mode constraints."""
        ff = FeedForwardBlock(input_size=1, n=1, m=3, conditional_modes=[0])
        tuples = ff.generate_possible_tuples()
        # For a single photon and one conditional mode the generator should not
        # explore outcomes that would consume the only photon or empty mode twice.
        assert set(tuples) == {(), (0,)}
        for tup in tuples:
            assert tup.count(1) <= ff.n_photons - 1
            assert tup.count(0) <= ff.m - ff.n_photons - 1

    def test_parameters_method(self):
        """Check that parameters() returns a non-empty iterable."""
        ff = FeedForwardBlock(input_size=4, n=2, m=4, depth=2, conditional_modes=[0])
        params = list(ff.parameters())
        assert all(isinstance(p, torch.Tensor) for p in params)

    def test_forward_output_shape_and_sum(self):
        """Check forward pass produces valid probabilities summing to 1."""
        ff = FeedForwardBlock(input_size=4, n=2, m=4, depth=2, conditional_modes=[0])
        x = torch.rand(3, 4)  # batch of 3
        output = ff(x)
        assert isinstance(output, torch.Tensor)
        assert output.ndim == 2  # (batch_size, n_outputs)
        # Each row should sum approximately to 1
        probs_sum = output.sum(dim=1)
        assert torch.allclose(probs_sum, torch.ones_like(probs_sum), atol=1e-3)

    def test_forward_multi_mode(self):
        """Test forward with multiple conditional modes and output normalization."""
        ff = FeedForwardBlock(input_size=3, n=2, m=4, depth=2, conditional_modes=[0, 1])
        x = torch.rand(2, 3)
        output = ff(x)
        assert output.shape[0] == 2  # batch size preserved
        assert output.shape[1] > 0
        assert torch.allclose(output.sum(dim=1), torch.ones(2), atol=1e-3)

    def test_get_output_size_matches_forward(self):
        """get_output_size should agree with an explicit forward pass."""
        ff = FeedForwardBlock(input_size=3, n=2, m=4, depth=2, conditional_modes=[0])
        out_size = ff.get_output_size()
        sample = torch.rand(1, ff.input_size)
        # A real forward pass should expose the same number of output branches.
        output = ff(sample)
        assert out_size == output.shape[1]

    def test_backward_pass(self):
        """Ensure gradients propagate correctly through the quantum layers."""
        ff = FeedForwardBlock(input_size=4, n=2, m=4, depth=2, conditional_modes=[0])
        x = torch.rand(1, 4, requires_grad=True)
        output = ff(x)
        loss = output.sum()
        loss.backward()
        assert x.grad is not None
        assert not torch.isnan(x.grad).any()

    def test_input_segments_cover_input_space(self):
        """Input segments should form a contiguous partition of the input features."""
        ff = FeedForwardBlock(input_size=5, n=2, m=6, depth=2, conditional_modes=[0])
        spans = list(ff.input_segments.values())
        # Sum of all local slices must match the total number of classical inputs.
        total = sum(end - start for start, end in spans)
        assert total == ff.input_size
        assert min(start for start, _ in spans) == 0
        assert max(end for _, end in spans) == ff.input_size

    def test_size_ff_layer_counts_depth_branches(self):
        """size_ff_layer should count the number of tuples at each depth."""
        ff = FeedForwardBlock(input_size=2, n=2, m=4, depth=2, conditional_modes=[0])
        # Root depth contains only the empty tuple, first depth splits into binary
        # outcomes, second depth should track two viable continuations.
        assert ff.size_ff_layer(0) == 1  # root tuple
        assert ff.size_ff_layer(1) == 2  # (0,), (1,)
        assert ff.size_ff_layer(2) == 2  # (0,1), (1,0)

    def test_define_ff_layer_replaces_layers(self):
        """define_ff_layer must swap in the provided QuantumLayer instances."""
        ff = FeedForwardBlock(input_size=2, n=2, m=4, depth=2, conditional_modes=[0])
        depth = 1
        target_tuples = sorted(
            [tup for tup in ff.tuples if len(tup) == depth * ff.n_cond]
        )
        original_layers = [ff.layers[tup] for tup in target_tuples]
        replacements = []
        for tup in target_tuples:
            remaining_modes = ff.m - len(tup)
            remaining_photons = ff.n_photons - sum(tup)
            # Replacement layers mirror the remaining physical resources in each branch.
            replacements.append(define_layer_no_input(remaining_modes, remaining_photons))
        ff.define_ff_layer(depth, replacements)
        for tup, original, replacement in zip(
            target_tuples, original_layers, replacements
        ):
            assert ff.layers[tup] is replacement
            assert ff.layers[tup] is not original

    def test_indices_by_values_and_match_indices(self):
        """Test low-level index mapping helpers."""
        ff = FeedForwardBlock(input_size=2, n=2, m=4, depth=2, conditional_modes=[0, 1])
        keys = [(0, 1, 0), (1, 0, 1), (0, 0, 1)]
        idx_dict = ff._indices_by_values(keys, [0, 1])
        assert all(isinstance(v, torch.Tensor) for v in idx_dict.values())

        data_out = [(1, 0), (0, 1)]
        idx = ff._match_indices_multi(keys, data_out, [0, 1], (0, 1))
        assert isinstance(idx, torch.Tensor)

    def test_integration_with_optimizer(self):
        """Ensure block integrates cleanly with PyTorch optimizers."""
        ff = FeedForwardBlock(input_size=4, n=2, m=4, depth=2, conditional_modes=[0])
        x = torch.rand(1, 4)
        optimizer = torch.optim.Adam(ff.parameters(), lr=1e-3)

        output = ff(x)
        loss = output.pow(2).sum()
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        assert True  # No runtime errors

    def test_output_keys_consistency(self):
        """Ensure output keys are consistent after forward pass."""
        ff = FeedForwardBlock(input_size=3, n=2, m=3, depth=2, conditional_modes=[0])
        _ = ff(torch.rand(1, 3))
        keys = ff.get_output_keys()
        print(keys)
        assert isinstance(keys, list)
        assert len(keys) > 0

    def test_feed_forward_matches_perceval_ffsimulator(
        self, monkeypatch, tmp_path
    ):
        """Compare FeedForwardBlock output against Perceval FFSimulator on a controlled setup."""
        # Perceval stores persistent data relative to $HOME -> redirect it to a temporary,
        # Step 0 – sandbox Perceval's persistent data so the test stays hermetic
        # (important for CI runners with restricted $HOME).
        monkeypatch.setenv("HOME", str(tmp_path))

        import perceval as pcvl
        from perceval.backends import SLOSBackend
        from perceval.components import Detector, FFCircuitProvider, Unitary
        from perceval.utils import BasicState

        # Step 1 – instantiate the FeedForwardBlock we want to validate. Keeping the
        # RNG seed fixed ensures the layer construction is deterministic.
        torch.manual_seed(0)
        block = FeedForwardBlock(
            input_size=1,
            n=2,
            m=4,
            depth=1,
            conditional_modes=[0],
        )

        # The quantum layers are initialised with random trainable parameters. We force
        # them to zero so that no-bunching remains exact (QuantumLayer.forward renormalises
        # after discarding bunched states), which keeps both simulators in the same regime.
        with torch.no_grad():
            for param in block.parameters():
                param.zero_()

        # Step 2 – run the frozen block once to obtain its output distribution.
        x = torch.zeros(1, 1)
        model_output = block(x).detach().cpu().numpy()[0]
        output_keys = list(block.output_keys)

        def layer_unitary(layer, params):
            """Return the numeric Perceval unitary matching a QuantumLayer."""
            # Each QuantumLayer wraps a symbolic Perceval circuit. We copy the circuit
            # and assign the numerical parameters extracted from PyTorch so we can reuse
            # it on the Perceval side.
            circuit = layer.circuit.copy()
            mapping = layer.computation_process.converter.param_mapping
            assignments = {}
            for name, (tensor_idx, param_idx) in mapping.items():
                tensor = params[tensor_idx]
                if isinstance(tensor, torch.Tensor):
                    detached = tensor.detach()
                    if detached.dim() > 1:
                        detached = detached[0]
                    value = detached[param_idx].item()
                else:
                    value = tensor[param_idx]
                assignments[name] = float(value)
            circuit.assign(assignments)
            return circuit.compute_unitary()

        # Step 3 – pull out the parameters for every branch of the feed-forward tree.
        # Root layer: tuple `()`. Children conditioned on measuring 0 or 1 photon:
        # tuples `(0,)` and `(1,)`. We will reconstruct each branch as a Perceval unitary.
        root_params = block.layers[()].prepare_parameters([x])
        child_zero_params = block.layers[(0,)].prepare_parameters([])
        child_one_params = block.layers[(1,)].prepare_parameters([])

        root_unitary = layer_unitary(block.layers[()], root_params)
        zero_unitary = layer_unitary(block.layers[(0,)], child_zero_params)
        one_unitary = layer_unitary(block.layers[(1,)], child_one_params)

        # Step 4 – rebuild the feed-forward logic with Perceval primitives:
        #   1. apply the root unitary,
        #   2. measure the conditional mode with a PNR detector,
        #   3. feed-forward the appropriate child circuit.
        backend = SLOSBackend()
        processor = pcvl.Processor(backend, 4)
        processor.add(0, Unitary(root_unitary))
        processor.add(0, Detector.pnr())

        provider = FFCircuitProvider(
            m=1,
            offset=0,
            default_circuit=Unitary(zero_unitary),
        )
        provider.add_configuration((0,), Unitary(zero_unitary))
        provider.add_configuration((1,), Unitary(one_unitary))
        processor.add((0,), provider)
        processor.with_input(BasicState([1, 1, 0, 0]))

        simulator_result = processor.probs()["results"]

        conditional_modes = [0]
        ffs_probs = defaultdict(float)
        for state, probability in simulator_result.items():
            reduced_state = tuple(
                value
                for idx, value in enumerate(state)
                if idx not in conditional_modes
            )
            # QuantumLayer.forward renormalises after dropping bunched states; mirror
            # that behaviour by ignoring outcomes where two photons share one mode.
            if any(v > 1 for v in reduced_state):
                continue
            ffs_probs[reduced_state] += probability

        # Step 5 – normalise and compare Perceval vs FeedForwardBlock distributions.
        total_prob = sum(ffs_probs.values())
        assert not math.isclose(total_prob, 0.0), "FFSimulator returned zero probability mass"
        for key in ffs_probs:
            ffs_probs[key] /= total_prob
        
        sim_keys = set(ffs_probs.keys())
        expected_keys = set(output_keys)
        assert sim_keys.issubset(expected_keys), (
            f"Simulator produced unexpected keys {sorted(sim_keys - expected_keys)}"
        )

        # The FeedForwardBlock output is ordered according to block.output_keys.
        # We compare the probability assigned to each key against the simulator result.
        for key, expected in zip(output_keys, model_output):
            print(f"Key {key}: model {expected:.6f} vs sim {ffs_probs.get(key, 0.0):.6f}")
            assert ffs_probs.get(key, 0.0) == pytest.approx(
                float(expected), abs=1e-6
            )

@pytest.mark.skipif(
    not torch.cuda.is_available(), reason="CUDA not available for GPU tests"
)
class TestFeedForwardBlockGPU:
    """GPU-only tests for FeedForwardBlock forward/backward behavior."""

    def test_forward_on_gpu(self):
        """Ensure forward pass works on GPU and outputs valid probabilities."""
        device = torch.device("cuda")
        ff = FeedForwardBlock(
            input_size=4, n=2, m=4, depth=2, conditional_modes=[0]
        ).to(device)
        x = torch.rand(8, 4, device=device)
        output = ff(x)
        assert output.device.type == "cuda"
        assert torch.allclose(
            output.sum(dim=1), torch.ones(8, device=device), atol=1e-3
        )

    def test_backward_on_gpu(self):
        """Ensure gradients flow correctly on GPU."""
        device = torch.device("cuda")
        ff = FeedForwardBlock(
            input_size=4, n=2, m=4, depth=2, conditional_modes=[0]
        ).to(device)
        x = torch.rand(4, 4, device=device, requires_grad=True)
        output = ff(x)
        loss = output.sum()
        loss.backward()

        # Verify gradients computed and reside on GPU
        assert x.grad is not None
        assert x.grad.device.type == "cuda"
        assert not torch.isnan(x.grad).any()

    def test_forward_backward_multi_mode_gpu(self):
        """Test feedforward & gradient with multiple conditional modes on GPU."""
        device = torch.device("cuda")
        ff = FeedForwardBlock(
            input_size=6, n=3, m=6, depth=2, conditional_modes=[0, 1]
        ).to(device)
        x = torch.rand(2, 6, device=device, requires_grad=True)

        output = ff(x)
        assert output.device.type == "cuda"
        assert output.shape[0] == 2
        assert torch.allclose(
            output.sum(dim=1), torch.ones(2, device=device), atol=1e-3
        )

        loss = output.mean()
        loss.backward()
        assert x.grad is not None
        assert x.grad.device.type == "cuda"

    def test_gpu_optimizer_step(self):
        """Ensure GPU-based optimization loop runs correctly."""
        device = torch.device("cuda")
        ff = FeedForwardBlock(
            input_size=4, n=2, m=4, depth=2, conditional_modes=[0]
        ).to(device)
        x = torch.rand(2, 4, device=device)
        optimizer = torch.optim.Adam(ff.parameters(), lr=1e-3)

        # Forward, backward, and optimizer step
        output = ff(x)
        loss = output.pow(2).sum()
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        # Ensure no NaNs or device mismatch
        assert not torch.isnan(loss).any()
        assert all(p.device.type == "cuda" for p in ff.parameters())


class TestPoolingFeedForward:
    """Test suite for PoolingFeedForward class."""

    def test_init_default_pooling(self):
        """Test PoolingFeedForward initialization with default pooling modes."""
        pff = PoolingFeedForward(n_modes=16, n_photons=2, n_output_modes=8)
        assert pff.n_modes == 16
        assert isinstance(pff.match_indices, torch.Tensor)
        assert isinstance(pff.exclude_indices, torch.Tensor)
        assert isinstance(pff.keys_out, list)

    def test_init_custom_pooling(self):
        """Test PoolingFeedForward initialization with custom pooling modes."""
        pooling_modes = [[0, 1], [2, 3], [4, 5], [6, 7]]
        pff = PoolingFeedForward(
            n_modes=8, n_photons=2, n_output_modes=4, pooling_modes=pooling_modes
        )
        assert pff.n_modes == 8
        assert isinstance(pff.match_indices, torch.Tensor)
        assert isinstance(pff.exclude_indices, torch.Tensor)

    def test_init_with_bunching(self):
        """Test PoolingFeedForward initialization with bunching allowed."""
        pff = PoolingFeedForward(
            n_modes=8, n_photons=2, n_output_modes=4, no_bunching=False
        )
        assert pff.n_modes == 8
        assert isinstance(pff.match_indices, torch.Tensor)

    def test_forward_pass_shape(self):
        """Test forward pass output shape."""
        pff = PoolingFeedForward(n_modes=16, n_photons=2, n_output_modes=8)
        batch_size = 4
        n_input_states = len(pff.match_indices) + len(pff.exclude_indices)
        amplitudes = torch.rand(batch_size, n_input_states)
        output = pff(amplitudes)

        assert isinstance(output, torch.Tensor)
        assert output.shape[0] == batch_size
        assert output.shape[1] == len(pff.keys_out)

    def test_forward_pass_dtype_preservation(self):
        """Test that forward pass preserves dtype."""
        pff = PoolingFeedForward(n_modes=8, n_photons=2, n_output_modes=4)
        n_input_states = len(pff.match_indices) + len(pff.exclude_indices)

        # Test float32
        amplitudes_f32 = torch.rand(2, n_input_states, dtype=torch.float32)
        output_f32 = pff(amplitudes_f32)
        assert output_f32.dtype == torch.float32

        # Test float64
        amplitudes_f64 = torch.rand(2, n_input_states, dtype=torch.float64)
        output_f64 = pff(amplitudes_f64)
        assert output_f64.dtype == torch.float64

    def test_forward_pass_device_preservation(self):
        """Test that forward pass preserves device."""
        pff = PoolingFeedForward(n_modes=8, n_photons=2, n_output_modes=4)
        n_input_states = len(pff.match_indices) + len(pff.exclude_indices)
        amplitudes = torch.rand(2, n_input_states)
        output = pff(amplitudes)
        assert output.device == amplitudes.device

    def test_forward_matches_manual_pooling(self):
        """Manual pooling computation should agree with module output."""
        pooling_modes = [[0, 1], [2, 3]]
        pff = PoolingFeedForward(
            n_modes=4, n_photons=2, n_output_modes=2, pooling_modes=pooling_modes
        )
        total_states = pff.match_indices.numel() + pff.exclude_indices.numel()
        # Deterministic amplitudes make it easy to verify the scatter logic.
        amplitudes = torch.arange(
            1, total_states + 1, dtype=torch.float32
        ).unsqueeze(0)
        output = pff(amplitudes)
        assert pff.match_indices.numel() > 0

        mask = torch.ones(total_states, dtype=torch.bool)
        if pff.exclude_indices.numel():
            mask[pff.exclude_indices.long()] = False
        filtered = amplitudes[:, mask]

        manual = torch.zeros(1, len(pff.keys_out), dtype=amplitudes.dtype)
        for col, target in enumerate(pff.match_indices.tolist()):
            # Recreate scatter_add manually to assert exact binning behaviour.
            manual[0, target] += filtered[0, col]

        norm = manual.abs().pow(2).sum(dim=-1, keepdim=True).sqrt()
        expected = manual / norm
        assert torch.allclose(output, expected, atol=1e-6)
        probs = output.abs().pow(2).sum(dim=-1)
        assert torch.allclose(probs, torch.ones_like(probs), atol=1e-6)

    def test_match_tuples_method(self):
        """Test match_tuples method."""
        pff = PoolingFeedForward(n_modes=8, n_photons=2, n_output_modes=4)
        keys_in = [(0, 0, 1, 1, 0, 0, 0, 0), (1, 0, 1, 0, 0, 0, 0, 0)]
        keys_out = [(0, 1, 0, 0), (1, 1, 0, 0)]
        pooling_modes = [[0, 1], [2, 3], [4, 5], [6, 7]]
        match_indices, exclude_indices = pff.match_tuples(
            keys_in, keys_out, pooling_modes
        )
        # Only the second input collapses to a valid output state; the first is dropped.
        assert match_indices == [1]
        assert exclude_indices == [0]

    def test_backward_pass_integration(self):
        """Test backward pass through PoolingFeedForward."""
        pff = PoolingFeedForward(n_modes=8, n_photons=2, n_output_modes=4)
        n_input_states = len(pff.match_indices) + len(pff.exclude_indices)
        amplitudes = torch.rand(2, n_input_states, requires_grad=True)
        output = pff(amplitudes)
        loss = output.sum()
        loss.backward()
        assert amplitudes.grad is not None

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_forward_pass_on_cuda(self):
        """Test that forward pass runs correctly on CUDA."""
        device = torch.device("cuda")
        pff = PoolingFeedForward(n_modes=16, n_photons=2, n_output_modes=8).to(device)
        n_input_states = len(pff.match_indices) + len(pff.exclude_indices)
        amplitudes = torch.rand(4, n_input_states, device=device)
        output = pff(amplitudes)
        assert output.is_cuda
        assert output.shape[0] == 4
        assert output.shape[1] == len(pff.keys_out)

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_backward_pass_on_cuda(self):
        """Test backward pass with CUDA tensors."""
        device = torch.device("cuda")
        pff = PoolingFeedForward(n_modes=8, n_photons=2, n_output_modes=4).to(device)
        n_input_states = len(pff.match_indices) + len(pff.exclude_indices)
        amplitudes = torch.rand(2, n_input_states, requires_grad=True, device=device)
        output = pff(amplitudes)
        loss = output.pow(2).sum()
        loss.backward()
        assert amplitudes.grad is not None
        assert amplitudes.grad.is_cuda

    def test_integration_with_quantum_layer(self):
        """Test integration with quantum layers (as in the main script)."""
        pff = PoolingFeedForward(n_modes=16, n_photons=2, n_output_modes=8)
        pre_layer = define_layer_no_input(16, 2)
        post_layer = define_layer_no_input(8, 2)
        _, amplitudes = pre_layer(return_amplitudes=True)
        amplitudes = pff(amplitudes)
        post_layer.set_input_state(amplitudes)
        res = post_layer()
        assert isinstance(res, torch.Tensor)
        assert res.requires_grad

    def test_optimization_with_layers(self):
        """Test optimization loop with PoolingFeedForward between layers."""
        from itertools import chain

        pff = PoolingFeedForward(n_modes=8, n_photons=2, n_output_modes=4)
        pre_layer = define_layer_no_input(8, 2)
        post_layer = define_layer_no_input(4, 2)
        params = chain(pre_layer.parameters(), post_layer.parameters())
        optimizer = torch.optim.Adam(params)

        for _ in range(3):
            _, amplitudes = pre_layer(return_amplitudes=True)
            amplitudes = pff(amplitudes)
            post_layer.set_input_state(amplitudes)
            res = post_layer().pow(2).sum()
            res.backward()
            optimizer.step()
            optimizer.zero_grad()
        assert True

    def test_different_pooling_ratios(self):
        """Test various pooling ratios."""
        test_cases = [(16, 8), (16, 4), (12, 6), (9, 3)]
        for n_modes, n_output_modes in test_cases:
            pff = PoolingFeedForward(
                n_modes=n_modes, n_photons=2, n_output_modes=n_output_modes
            )
            n_input_states = len(pff.match_indices) + len(pff.exclude_indices)
            amplitudes = torch.rand(2, n_input_states)
            output = pff(amplitudes)
            assert output.shape[1] == len(pff.keys_out)

    def test_single_photon_case(self):
        """Test PoolingFeedForward with a single photon."""
        pff = PoolingFeedForward(n_modes=8, n_photons=1, n_output_modes=4)
        n_input_states = len(pff.match_indices) + len(pff.exclude_indices)
        amplitudes = torch.rand(2, n_input_states)
        output = pff(amplitudes)
        assert isinstance(output, torch.Tensor)
        assert output.shape[0] == 2

    def test_batch_size_one(self):
        """Test PoolingFeedForward with batch size of 1."""
        pff = PoolingFeedForward(n_modes=8, n_photons=2, n_output_modes=4)
        n_input_states = len(pff.match_indices) + len(pff.exclude_indices)
        amplitudes = torch.rand(1, n_input_states)
        output = pff(amplitudes)
        assert output.shape[0] == 1

    def test_large_batch_size(self):
        """Test PoolingFeedForward with large batch size."""
        pff = PoolingFeedForward(n_modes=8, n_photons=2, n_output_modes=4)
        n_input_states = len(pff.match_indices) + len(pff.exclude_indices)
        batch_size = 32
        amplitudes = torch.rand(batch_size, n_input_states)
        output = pff(amplitudes)
        assert output.shape[0] == batch_size


if __name__ == "__main__":
    pytest.main([__file__])
