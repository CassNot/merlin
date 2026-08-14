.. _user_guide_migration_guide:

=================
Migration guide
=================

Migration guide (v0.3 to v.0.4)
===============================

Migrating dependency versions for MerLin 0.4
--------------------------------------------

MerLin 0.4 requires Perceval ``>=1.2.1``. Previous MerLin versions supported
Perceval ``<=1.1``.

MerLin 0.4 also supports PyTorch ``2.11`` and ``2.12``. See
:doc:`/user_guide/compatibility` for the supported MerLin, Perceval, PyTorch,
and Python version combinations.

Migrating from removed ``computation_space`` argument in the ``QuantumLayer``
-------------------------------------------------------------------------------

.. warning::
   *Deprecated since version 0.4:* The use of the ``computation_space`` argument in the QuantumLayer's constructor is no longer supported as 0.4.0.
   Use the ``computation_space`` flag inside ``measurement_strategy`` instead. For example, ``MeasurementStrategy.probs(computation_space=...)``.

To define the ``computation_space`` of a :class:`~merlin.algorithms.layer.QuantumLayer`, a measurement strategy factory method must be used. For example, to use the probabilities measurement strategy with the Fock space computation space:

.. code-block:: python

   # Deprecated (legacy enum + separate computation_space)
   # QuantumLayer(..., measurement_strategy=MeasurementStrategy.PROBABILITIES,
   #             computation_space=ComputationSpace.FOCK)

   # Recommended
   QuantumLayer(..., measurement_strategy=MeasurementStrategy.probs(ComputationSpace.FOCK))

Migrating removed simple-factory arguments
------------------------------------------

The following arguments were removed from the ``simple`` factory methods in
MerLin 0.4. Passing them now raises Python's normal ``TypeError`` for an
unexpected keyword argument:

* ``QuantumLayer.simple``: ``n_params``
* ``FeatureMap.simple``: ``n_photons`` and ``trainable``
* ``FidelityKernel.simple``: ``n_photons``, ``trainable``, and ``input_state``

The simple factories now infer their parameter allocation, photon count, and
input state from ``input_size`` and the generated circuit. For a custom
architecture, use :class:`~merlin.builder.circuit_builder.CircuitBuilder` and
pass the resulting builder to :class:`~merlin.algorithms.layer.QuantumLayer`
or :class:`~merlin.algorithms.kernels.FeatureMap`. For kernels, provide a
custom ``input_state`` to the :class:`~merlin.algorithms.kernels.FidelityKernel`
constructor when a specific occupation pattern is required.

For example, replace the removed ``FeatureMap.simple`` arguments:

.. code-block:: python

   # Removed in 0.4
   # FeatureMap.simple(input_size=2, n_photons=2, trainable=True)

   # Recommended: use the inferred defaults
   FeatureMap.simple(input_size=2)

The ``n_photons`` and ``input_state`` arguments remain supported on the
general ``QuantumLayer`` and ``FidelityKernel`` constructors where they are
part of the explicit circuit/input-state configuration.

Migrating from ``no_bunching`` (deprecated)
-------------------------------------------

Migrating from removed ``amplitude_encoding`` flag in the ``QuantumLayer``
-------------------------------------------------------------------------------

.. warning::
   The ``amplitude_encoding=True`` constructor parameter was removed in
   **0.4**. Pass a :class:`~merlin.core.state_vector.StateVector` or a complex
   ``torch.Tensor`` to ``forward()`` instead.

To use amplitude encoding in a :class:`~merlin.algorithms.layer.QuantumLayer`,
pass a :class:`~merlin.core.state_vector.StateVector` or a complex
``torch.Tensor`` at the forward call. The constructor no longer needs an
amplitude-encoding flag.

.. code-block:: python

  import torch
  from merlin import CircuitBuilder, QuantumLayer, MeasurementStrategy, ComputationSpace
  from merlin.core import EncodingSpace, StateVector

  builder = CircuitBuilder(n_modes=4)
  builder.add_entangling_layer()

  layer = QuantumLayer(
      input_size=0,
      builder=builder,
      n_photons=2,
      measurement_strategy=MeasurementStrategy.probs(
          computation_space=ComputationSpace.FOCK
      ),
  )

  # Option 1: StateVector input
  input_state = StateVector.from_tensor(
      tensor=torch.rand(1, 10),
      n_modes=4,
      n_photons=2,
      encoding=EncodingSpace.FOCK,
  )
  layer(input_state)

  # Option 2: complex tensor
  input_state = torch.rand(1, layer.output_size, dtype=torch.complex64)
  layer(input_state)

If you previously built full Fock-sized tensors manually, prefer a logical
encoding when the data has one. For example, a two-qubit dual-rail state can be
passed as four logical amplitudes instead of a ten-entry full-Fock vector:

.. code-block:: python

  import torch
  from merlin.core import EncodingSpace, StateVector

  logical = torch.tensor([1.0, 0.0, 0.0, 1.0], dtype=torch.complex64)
  input_state = StateVector.from_tensor(
      logical,
      encoding=EncodingSpace.DUAL_RAIL,
  )

``StateVector`` normalizes lazily when a normalized dense view or layer
execution needs it, so explicit pre-normalization is not required for this
construction.

See :doc:`/user_guide/encoding_space` for Fock, unbunched, dual-rail,
partitioned, and QLOQ examples.

Migrating from tensor ``input_state`` values
--------------------------------------------

.. warning::
   Passing a ``torch.Tensor`` as an ``input_state`` value is removed in
   **0.4**. Build a :class:`~merlin.core.state_vector.StateVector` with
   :meth:`~merlin.core.state_vector.StateVector.from_tensor` and pass that
   object instead.

Tensor-valued ``input_state`` arguments used to represent amplitude data. That
state metadata now belongs in :class:`~merlin.core.state_vector.StateVector`,
which carries the tensor together with its mode, photon, and encoding-space
information. This applies to constructors and mutators such as
``QuantumLayer.set_input_state()``.

.. code-block:: python

  import torch
  from merlin import QuantumLayer, MeasurementStrategy, ComputationSpace
  from merlin.core import EncodingSpace, StateVector

  amplitudes = torch.rand(1, 10, dtype=torch.complex64)
  input_state = StateVector.from_tensor(
      amplitudes,
      n_modes=4,
      n_photons=2,
      encoding=EncodingSpace.FOCK,
  )

  layer = QuantumLayer(
      circuit=circuit,
      input_state=input_state,
      measurement_strategy=MeasurementStrategy.probs(
          computation_space=ComputationSpace.FOCK
      ),
  )

For :class:`~merlin.algorithms.kernels.FidelityKernel`,
``input_state`` remains a Fock occupation list such as ``[1, 0, 1, 0]``.
Tensor amplitude states are not valid kernel input states; use a
:class:`~merlin.algorithms.layer.QuantumLayer` with ``StateVector`` for those
workflows. The same rule applies to feed-forward blocks: use a Fock occupation
list, ``pcvl.BasicState``, ``pcvl.StateVector``, or
:class:`~merlin.core.state_vector.StateVector`, not a raw tensor.


v.0.3 deprecations are now errors
--------------------------------------

Deprecations in the next section are now errors. Please consult the following section for other migration notes.



Migration guide (v0.2 to v.0.3)
===============================

Migrating from removed ``no_bunching``
--------------------------------------

.. warning:: *Removed in version 0.4:*
   ``no_bunching`` is removed in version 0.4. Use explicit
   ``computation_space`` configuration instead.

The ``no_bunching`` flag is removed.

If you are using a ``QuantumLayer`` and you need to control how Fock states are
truncated or encoded, define the ``computation_space`` inside the ``measurement_strategy``
instead. 

If you are using a Kernel, define the encoding or truncation of the Fock states in the
``computation_space`` parameter.


Map the legacy intent as follows:

- ``no_bunching=False`` → ``computation_space=ComputationSpace.FOCK`` (full Fock space)
- ``no_bunching=True`` → ``computation_space=ComputationSpace.UNBUNCHED`` (one photon per mode)
- Dual-rail encodings → ``computation_space=ComputationSpace.DUAL_RAIL``

This keeps measurement strategy selection orthogonal to simulation space configuration.

Migrating from legacy ``MeasurementStrategy``
---------------------------------------------

.. warning:: *Deprecated since version 0.3:*
   Enum-style and string access is deprecated and will be removed from `MeasurementStrategy` in v0.4.
   Use the new factory methods instead: ``MeasurementStrategy.probs(computation_space=...)``, ``MeasurementStrategy.mode_expectations(computation_space=...)``, ``MeasurementStrategy.amplitudes(computation_space=...)``.
   See this migration section for the mapping.

Old to new mappings
^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Deprecated
     - Recommended replacement
   * - ``MeasurementStrategy.PROBABILITIES``
     - ``MeasurementStrategy.probs(computation_space=...)``
   * - ``MeasurementStrategy.MODE_EXPECTATIONS``
     - ``MeasurementStrategy.mode_expectations(computation_space=...)``
   * - ``MeasurementStrategy.AMPLITUDES``
     - ``MeasurementStrategy.amplitudes(computation_space=...)``
   * - ``MeasurementStrategy.NONE``
     - ``MeasurementStrategy.amplitudes(computation_space=...)``
   * - ``"PROBABILITIES"`` (string)
     - ``MeasurementStrategy.probs(computation_space=...)``

Computation space now lives inside the strategy.

.. code-block:: python

   # Deprecated (legacy enum + separate computation_space)
   # QuantumLayer(..., measurement_strategy=MeasurementStrategy.PROBABILITIES,
   #             computation_space=ComputationSpace.FOCK)

   # Recommended
   QuantumLayer(..., measurement_strategy=MeasurementStrategy.probs(ComputationSpace.FOCK))
