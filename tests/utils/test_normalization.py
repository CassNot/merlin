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

"""Unit tests for normalization helpers."""

import torch

from merlin.core.computation_space import ComputationSpace
from merlin.utils.normalization import (
    normalize_probabilities,
    normalize_probabilities_and_amplitudes,
    probabilities_from_amplitudes,
)


def test_probabilities_from_amplitudes():
    amplitudes = torch.tensor([1 + 2j, 2 - 1j], dtype=torch.complex64)
    probs = probabilities_from_amplitudes(amplitudes)
    expected = torch.tensor([5.0, 5.0], dtype=torch.float32)
    assert torch.allclose(probs, expected)


def test_normalize_probabilities_noop_for_fock():
    probs = torch.tensor([[0.2, 0.2, 0.2]], dtype=torch.float32)
    normalized = normalize_probabilities(probs, ComputationSpace.FOCK)
    assert torch.allclose(normalized, probs)


def test_normalize_probabilities_unbunched():
    probs = torch.tensor([[2.0, 2.0], [0.0, 3.0]], dtype=torch.float32)
    normalized = normalize_probabilities(probs, ComputationSpace.UNBUNCHED)
    expected = torch.tensor([[0.5, 0.5], [0.0, 1.0]], dtype=torch.float32)
    assert torch.allclose(normalized, expected)


def test_normalize_probabilities_and_amplitudes_unbunched():
    amplitudes = torch.tensor([1 + 0j, 2 + 0j], dtype=torch.complex64)
    probs, renorm = normalize_probabilities_and_amplitudes(
        amplitudes, ComputationSpace.UNBUNCHED
    )
    expected_probs = torch.tensor([0.2, 0.8], dtype=torch.float32)
    assert torch.allclose(probs, expected_probs)
    assert torch.allclose(probabilities_from_amplitudes(renorm), expected_probs)


def test_normalize_probabilities_and_amplitudes_zero_sum():
    amplitudes = torch.zeros(3, dtype=torch.complex64)
    probs, renorm = normalize_probabilities_and_amplitudes(
        amplitudes, ComputationSpace.DUAL_RAIL
    )
    assert torch.allclose(probs, torch.zeros(3, dtype=torch.float32))
    assert torch.allclose(renorm, amplitudes)
