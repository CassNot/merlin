import warnings

import perceval as pcvl
import pytest

from merlin.algorithms.layer import QuantumLayer
from merlin.core.computation_space import ComputationSpace
from merlin.measurement.strategies import MeasurementStrategy


def test_init_defaults_to_unbunched():
    """QuantumLayer.__init__ defaults to UNBUNCHED computation space."""
    circuit = pcvl.Circuit(2)
    # Provide an explicit input_state so the layer can initialize from the custom circuit
    layer = QuantumLayer(circuit=circuit, input_state=[1, 0])
    assert layer.computation_space is ComputationSpace.UNBUNCHED


def test_simple_defaults_to_unbunched():
    """QuantumLayer.simple defaults to UNBUNCHED computation space."""
    model = QuantumLayer.simple(input_size=2)
    assert model.quantum_layer.computation_space is ComputationSpace.UNBUNCHED


def test_init_accepts_measurement_strategy_fock():
    circuit = pcvl.Circuit(2)
    layer = QuantumLayer(
        circuit=circuit,
        input_state=[1, 0],
        measurement_strategy=MeasurementStrategy.probs(
            computation_space=ComputationSpace.FOCK
        ),
    )
    assert layer.computation_space is ComputationSpace.FOCK


def test_simple_rejects_removed_n_params():
    """n_params was removed in 0.4; it must fail through normal signature validation."""
    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        with pytest.raises(TypeError, match=r"unexpected keyword argument 'n_params'"):
            QuantumLayer.simple(input_size=2, n_params=95)
    assert not any(
        issubclass(warning.category, DeprecationWarning) for warning in warning_list
    )


def test_simple_rejects_unknown_kwarg():
    """Unknown kwargs must still fail through normal Python signature validation."""
    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        with pytest.raises(
            TypeError, match=r"unexpected keyword argument 'not_a_real_kwarg'"
        ):
            QuantumLayer.simple(input_size=2, not_a_real_kwarg=True)
    assert not any(
        issubclass(warning.category, DeprecationWarning) for warning in warning_list
    )
