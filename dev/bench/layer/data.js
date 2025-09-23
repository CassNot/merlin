window.BENCHMARK_DATA = {
  "lastUpdate": 1758620173282,
  "repoUrl": "https://github.com/CassNot/merlin",
  "entries": {
    "Benchmark": [
      {
        "commit": {
          "author": {
            "email": "jean.senellart@quandela.com",
            "name": "Jean Senellart",
            "username": "jsenellart"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f633667e9a8d1abb576c1b38466dffb8b0e81969",
          "message": "Merge branch 'release-0.2' into main",
          "timestamp": "2025-09-23T11:34:19+02:00",
          "tree_id": "eb050fbd0dce2ff9b229dd851916958e70623f02",
          "url": "https://github.com/CassNot/merlin/commit/f633667e9a8d1abb576c1b38466dffb8b0e81969"
        },
        "date": 1758620172812,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/benchmark_layer.py::test_quantum_layer_forward_benchmark[cpu-config0]",
            "value": 147.93859296445262,
            "unit": "iter/sec",
            "range": "stddev: 0.0001408812013091902",
            "extra": "mean: 6.759561382608828 msec\nrounds: 115"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_quantum_layer_forward_benchmark[cpu-config1]",
            "value": 42.26125463874709,
            "unit": "iter/sec",
            "range": "stddev: 0.00033968401308968334",
            "extra": "mean: 23.662335833332154 msec\nrounds: 36"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_quantum_layer_forward_benchmark[cpu-config2]",
            "value": 17.329940554112238,
            "unit": "iter/sec",
            "range": "stddev: 0.0003737990360753594",
            "extra": "mean: 57.703602437499946 msec\nrounds: 16"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_quantum_layer_forward_benchmark[cpu-config3]",
            "value": 8.374317864312035,
            "unit": "iter/sec",
            "range": "stddev: 0.002348182627271146",
            "extra": "mean: 119.41271112499763 msec\nrounds: 8"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-8-config0]",
            "value": 227.76146813450706,
            "unit": "iter/sec",
            "range": "stddev: 0.00013068046748092354",
            "extra": "mean: 4.39055828095312 msec\nrounds: 210"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-8-config1]",
            "value": 109.12882186089188,
            "unit": "iter/sec",
            "range": "stddev: 0.00022569660814721144",
            "extra": "mean: 9.163482047618134 msec\nrounds: 105"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-8-config2]",
            "value": 62.863973279872724,
            "unit": "iter/sec",
            "range": "stddev: 0.0004685437776792509",
            "extra": "mean: 15.907362322581223 msec\nrounds: 62"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-8-config3]",
            "value": 39.92854461669191,
            "unit": "iter/sec",
            "range": "stddev: 0.0004881525162846331",
            "extra": "mean: 25.04473953658595 msec\nrounds: 41"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-16-config0]",
            "value": 215.74256948148442,
            "unit": "iter/sec",
            "range": "stddev: 0.00018022129760673902",
            "extra": "mean: 4.635153842857251 msec\nrounds: 210"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-16-config1]",
            "value": 105.9657866495083,
            "unit": "iter/sec",
            "range": "stddev: 0.0004704132132045872",
            "extra": "mean: 9.43700822330129 msec\nrounds: 103"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-16-config2]",
            "value": 60.85641109132829,
            "unit": "iter/sec",
            "range": "stddev: 0.0005145265337793554",
            "extra": "mean: 16.432122467742676 msec\nrounds: 62"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-16-config3]",
            "value": 38.18350956710337,
            "unit": "iter/sec",
            "range": "stddev: 0.00042281993241093997",
            "extra": "mean: 26.189316051281473 msec\nrounds: 39"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-32-config0]",
            "value": 212.37297904785612,
            "unit": "iter/sec",
            "range": "stddev: 0.00014908607526321218",
            "extra": "mean: 4.7086969560975085 msec\nrounds: 205"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-32-config1]",
            "value": 105.14749543059706,
            "unit": "iter/sec",
            "range": "stddev: 0.00032894521828228166",
            "extra": "mean: 9.510450019801501 msec\nrounds: 101"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-32-config2]",
            "value": 58.16517653560393,
            "unit": "iter/sec",
            "range": "stddev: 0.0005467639803804628",
            "extra": "mean: 17.192417517857653 msec\nrounds: 56"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-32-config3]",
            "value": 35.85727327142977,
            "unit": "iter/sec",
            "range": "stddev: 0.00037106376038677913",
            "extra": "mean: 27.888344783784113 msec\nrounds: 37"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-64-config0]",
            "value": 204.49869455431948,
            "unit": "iter/sec",
            "range": "stddev: 0.00018545217745657758",
            "extra": "mean: 4.890006765957019 msec\nrounds: 188"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-64-config1]",
            "value": 99.5475464466569,
            "unit": "iter/sec",
            "range": "stddev: 0.00035171180030277435",
            "extra": "mean: 10.045450999998836 msec\nrounds: 96"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-64-config2]",
            "value": 54.36180477423118,
            "unit": "iter/sec",
            "range": "stddev: 0.0005235087111425461",
            "extra": "mean: 18.3952685925914 msec\nrounds: 54"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_batched_computation_benchmark[cpu-64-config3]",
            "value": 32.65535339704408,
            "unit": "iter/sec",
            "range": "stddev: 0.0006415259639994051",
            "extra": "mean: 30.622850343751562 msec\nrounds: 32"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_gradient_computation_benchmark[cpu-config0]",
            "value": 64.42641355248668,
            "unit": "iter/sec",
            "range": "stddev: 0.00017330925714486147",
            "extra": "mean: 15.521584158728992 msec\nrounds: 63"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_gradient_computation_benchmark[cpu-config1]",
            "value": 18.110530799926053,
            "unit": "iter/sec",
            "range": "stddev: 0.0045899369578227935",
            "extra": "mean: 55.21649315789701 msec\nrounds: 19"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_multiple_circuit_types_benchmark[cpu-config0]",
            "value": 11.708917607956087,
            "unit": "iter/sec",
            "range": "stddev: 0.0036675195366035677",
            "extra": "mean: 85.40499074999985 msec\nrounds: 12"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_multiple_circuit_types_benchmark[cpu-config1]",
            "value": 3.5320872301951787,
            "unit": "iter/sec",
            "range": "stddev: 0.002366763587054436",
            "extra": "mean: 283.1187155999942 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_output_mapping_strategies_benchmark[cpu-config0]",
            "value": 10.407272841440143,
            "unit": "iter/sec",
            "range": "stddev: 0.0025535328602654746",
            "extra": "mean: 96.08665163635908 msec\nrounds: 11"
          },
          {
            "name": "benchmarks/benchmark_layer.py::test_output_mapping_strategies_benchmark[cpu-config1]",
            "value": 2.5681045309475294,
            "unit": "iter/sec",
            "range": "stddev: 0.07299693262516578",
            "extra": "mean: 389.3922494000037 msec\nrounds: 5"
          }
        ]
      }
    ]
  }
}