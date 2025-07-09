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

import perceval as pcvl
import pytest
import torch
import torch.nn as nn

import merlin as ml
from merlin import QuantumLayer


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_load_model_on_cuda():
    circuit = pcvl.components.GenericInterferometer(
        4,
        pcvl.components.catalog["mzi phase last"].generate,
        shape=pcvl.InterferometerShape.RECTANGLE,
    )

    layer = QuantumLayer(
        input_size=2,
        output_size=1,
        circuit=circuit,
        input_state=[1, 1, 0, 0],
        trainable_parameters=["phi"],
        device=torch.device("cuda"),
    )
    assert layer.device == torch.device("cuda")
    if len(layer.thetas) > 0:
        assert layer.thetas[0].device == torch.device("cuda", index=0)
    assert layer.computation_process.converter.device == torch.device("cuda")
    assert layer.computation_process.simulation_graph.device == torch.device("cuda")
    assert layer.computation_process.converter.list_rct[0][1].device == torch.device(
        "cuda", index=0
    )
    assert layer.computation_process.simulation_graph.vectorized_operations[-1][
        0
    ].device == torch.device("cuda", index=0)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_switch_model_to_cuda():
    circuit = pcvl.components.GenericInterferometer(
        4,
        pcvl.components.catalog["mzi phase last"].generate,
        shape=pcvl.InterferometerShape.RECTANGLE,
    )
    layer = QuantumLayer(
        input_size=2,
        output_size=1,
        circuit=circuit,
        input_state=[1, 1, 0, 0],
        trainable_parameters=["phi"],
        device=torch.device("cpu"),
    )
    assert layer.device == torch.device("cpu")
    layer = layer.to(torch.device("cuda"))
    assert layer.device == torch.device("cuda")
    if len(layer.thetas) > 0:
        assert layer.thetas[0].device == torch.device("cuda", index=0)
    assert layer.computation_process.converter.device == torch.device("cuda")
    assert layer.computation_process.simulation_graph.device == torch.device("cuda")
    assert layer.computation_process.converter.list_rct[0][1].device == torch.device(
        "cuda", index=0
    )
    assert layer.computation_process.simulation_graph.vectorized_operations[-1][
        0
    ].device == torch.device("cuda", index=0)


class QuantumClassifier_withAnsatz(nn.Module):
    def __init__(
        self, input_dim, hidden_dim=100, modes=10, num_classes=2, input_state=None, device = 'cpu',
    ):
        super().__init__()

        # This layer downscales the inputs to fit in the QLayer
        self.downscaling_layer = nn.Linear(input_dim, hidden_dim, device = device)

        # Building the QLayer with Merlin
        experiment = ml.PhotonicBackend(
            circuit_type=ml.CircuitType.SERIES,
            n_modes=modes,
            n_photons=sum(input_state) if input_state else modes // 2,
            state_pattern=ml.StatePattern.PERIODIC,
        )

        # PNR (Photon Number Resolving) output size
        # output_size_slos = math.comb(modes + photons_count - 1, photons_count)

        # Create ansatz for the quantum layer
        ansatz = ml.AnsatzFactory.create(
            PhotonicBackend=experiment,
            input_size=hidden_dim,
            # output_size=output_size_slos,
            output_mapping_strategy=ml.OutputMappingStrategy.NONE,
        )

        # Build the QLayer using Merlin
        self.q_circuit = ml.QuantumLayer(input_size=hidden_dim, ansatz=ansatz, device = device)

        # Linear output layer as in the original paper
        self.output_layer = nn.Linear(self.q_circuit.output_size, num_classes, device = device)

    def forward(self, x):
        # Forward pass through the quantum-classical hybrid
        print("\n=== checking device after each step ===")
        print(f" - Input is on device: {x.device}")
        x = self.downscaling_layer(x)
        print(f" - Downscaled input is on device: {x.device}")
        x = torch.sigmoid(x)  # Normalize for quantum layer
        print(f" - After sigmoid: device = {x.device}")
        x = self.q_circuit(x)
        print(f" - After q_circuit: device = {x.device}")
        out = self.output_layer(x)
        print(f" - Out on device: {out.device}")
        return out


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_QuantumClassifier_withAnsatz():
    """Test QuantumClassifier_withAnsatz functionality on GPU"""

    device = torch.device("cuda")
    print(f"Testing on device: {device}")

    # Test parameters
    batch_size = 4
    input_dim = 768
    hidden_dim = 100
    modes = 8
    num_classes = 2
    input_state = [1, 0, 1, 0, 1, 0, 0, 0]  # 3 photons in first 3 modes

    print("Test configuration:")
    print(f"- Input dimension: {input_dim}")
    print(f"- Hidden dimension: {hidden_dim}")
    print(f"- Modes: {modes}")
    print(f"- Number of classes: {num_classes}")
    print(f"- Input state: {input_state}")
    print(f"- Batch size: {batch_size}")

    # Create the quantum classifier
    print("\nCreating QuantumClassifier_withAnsatz...")
    model = QuantumClassifier_withAnsatz(
        input_dim=input_dim,
        hidden_dim=hidden_dim,
        modes=modes,
        num_classes=num_classes,
        input_state=input_state,
        device = device,
    )

    # Move model to GPU
    model = model.to(device)
    print("Model successfully moved to GPU")

    # Create sample input data
    print("\nCreating sample input data...")
    sample_input = torch.randn(batch_size, input_dim, device=device)
    print(f"Sample input shape: {sample_input.shape}")

    # Test forward pass
    print("\nTesting forward pass...")
    model.eval()
    with torch.no_grad():
        output = model(sample_input)
        print(f"Output shape: {output.shape}")
        print(f"Output: {output}")

    # Test with different batch sizes
    print("\nTesting with different batch sizes...")
    for test_batch_size in [1, 2, 8]:
        test_input = torch.randn(test_batch_size, input_dim, device=device)
        with torch.no_grad():
            test_output = model(test_input)
            print(f"Batch size {test_batch_size}: Input {test_input.shape} -> Output {test_output.shape}")

    # Test training mode
    print("\nTesting in training mode...")
    model.train()

    # Create dummy labels
    labels = torch.randint(0, num_classes, (batch_size,), device=device)

    # Test with gradient computation
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = torch.nn.CrossEntropyLoss()

    # Single training step
    optimizer.zero_grad()
    output = model(sample_input)
    loss = criterion(output, labels)
    loss.backward()
    optimizer.step()

    print(f"Training step completed. Loss: {loss.item():.4f}")

    # Test parameter count
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print("\nModel parameters:")
    print(f"- Total parameters: {total_params:,}")
    print(f"- Trainable parameters: {trainable_params:,}")

    # Test memory usage
    print("\nGPU memory usage:")
    print(f"- Allocated: {torch.cuda.memory_allocated(device) / 1024**2:.2f} MB")
    print(f"- Cached: {torch.cuda.memory_reserved(device) / 1024**2:.2f} MB")

    print("\n✅ All tests passed successfully!")

    # Assertions for pytest
    assert output.shape == torch.Size([batch_size, num_classes])
    assert output.device.type == device.type
    assert total_params > 0
    assert trainable_params > 0


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_different_configurations():
    """Test different model configurations"""

    device = torch.device("cuda")
    print("\nTesting different configurations...")

    # Test configurations
    configs = [
        {"modes": 4, "hidden_dim": 50, "input_state": [1, 0, 1, 0]},
        {"modes": 6, "hidden_dim": 100, "input_state": [1, 0, 1, 0, 1, 0]},
        {"modes": 10, "hidden_dim": 150, "input_state": [1, 0, 1, 0, 1, 0, 0, 0, 0, 0]},
    ]

    for i, config in enumerate(configs):
        print(f"\n--- Configuration {i+1} ---")
        print(f"Modes: {config['modes']}, Hidden dim: {config['hidden_dim']}")
        print(f"Input state: {config['input_state']}")

        model = QuantumClassifier_withAnsatz(
            input_dim=768,
            hidden_dim=config['hidden_dim'],
            modes=config['modes'],
            num_classes=2,
            input_state=config['input_state'],
            device=device
        ).to(device)

        # Test with sample input
        sample_input = torch.randn(2, 768, device=device)
        with torch.no_grad():
            output = model(sample_input)
            print(f"✅ Success: Output shape {output.shape}")

        # Assertions for pytest
        assert output.shape == torch.Size([2, 2])
        assert output.device.type == device.type
