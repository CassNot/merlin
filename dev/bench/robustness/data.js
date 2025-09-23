window.BENCHMARK_DATA = {
  "lastUpdate": 1758620202649,
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
        "date": 1758620201589,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/benchmark_robustness.py::test_large_batch_robustness_benchmark[cpu-64-config0]",
            "value": 42.756851846554625,
            "unit": "iter/sec",
            "range": "stddev: 0.0001821502961430834",
            "extra": "mean: 23.388064294087652 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_large_batch_robustness_benchmark[cpu-64-config1]",
            "value": 16.67381710344315,
            "unit": "iter/sec",
            "range": "stddev: 0.001129701715048945",
            "extra": "mean: 59.97426946667777 msec\nrounds: 15"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_large_batch_robustness_benchmark[cpu-64-config2]",
            "value": 7.975139440754263,
            "unit": "iter/sec",
            "range": "stddev: 0.0016021938058248834",
            "extra": "mean: 125.38965712496974 msec\nrounds: 8"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_large_batch_robustness_benchmark[cpu-128-config0]",
            "value": 38.191588711927054,
            "unit": "iter/sec",
            "range": "stddev: 0.0016136214925311489",
            "extra": "mean: 26.18377589743222 msec\nrounds: 39"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_large_batch_robustness_benchmark[cpu-128-config1]",
            "value": 14.825114013692861,
            "unit": "iter/sec",
            "range": "stddev: 0.0011766677521279115",
            "extra": "mean: 67.45310687502126 msec\nrounds: 16"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_large_batch_robustness_benchmark[cpu-128-config2]",
            "value": 6.95347494581149,
            "unit": "iter/sec",
            "range": "stddev: 0.0035411009655639796",
            "extra": "mean: 143.8129867142704 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_large_batch_robustness_benchmark[cpu-256-config0]",
            "value": 33.10582990794537,
            "unit": "iter/sec",
            "range": "stddev: 0.0003802020311568328",
            "extra": "mean: 30.20616014703806 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_large_batch_robustness_benchmark[cpu-256-config1]",
            "value": 12.0559644547187,
            "unit": "iter/sec",
            "range": "stddev: 0.0016881546508099015",
            "extra": "mean: 82.94649538458124 msec\nrounds: 13"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_large_batch_robustness_benchmark[cpu-256-config2]",
            "value": 5.514429466508362,
            "unit": "iter/sec",
            "range": "stddev: 0.004824344813745707",
            "extra": "mean: 181.34242283330573 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_large_batch_robustness_benchmark[cpu-512-config0]",
            "value": 26.282318045073325,
            "unit": "iter/sec",
            "range": "stddev: 0.0002674231644714411",
            "extra": "mean: 38.04839429631102 msec\nrounds: 27"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_large_batch_robustness_benchmark[cpu-512-config1]",
            "value": 8.865023897833062,
            "unit": "iter/sec",
            "range": "stddev: 0.007068229719478497",
            "extra": "mean: 112.80285440002444 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_large_batch_robustness_benchmark[cpu-512-config2]",
            "value": 4.094790800335384,
            "unit": "iter/sec",
            "range": "stddev: 0.002140533898673339",
            "extra": "mean: 244.21272020003926 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_extreme_values_robustness_benchmark[cpu-config0]",
            "value": 17.975248855273392,
            "unit": "iter/sec",
            "range": "stddev: 0.0007786664351628548",
            "extra": "mean: 55.632053166631415 msec\nrounds: 18"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_extreme_values_robustness_benchmark[cpu-config1]",
            "value": 10.147927716909964,
            "unit": "iter/sec",
            "range": "stddev: 0.008507438868275643",
            "extra": "mean: 98.54228645456881 msec\nrounds: 11"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_extreme_values_robustness_benchmark[cpu-config2]",
            "value": 6.549814207268904,
            "unit": "iter/sec",
            "range": "stddev: 0.00216954416056683",
            "extra": "mean: 152.6760864285604 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_numerical_stability_benchmark[cpu-config0]",
            "value": 3.7080685425999094,
            "unit": "iter/sec",
            "range": "stddev: 0.00026162030115681125",
            "extra": "mean: 269.68217779999577 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_numerical_stability_benchmark[cpu-config1]",
            "value": 1.4598984918446756,
            "unit": "iter/sec",
            "range": "stddev: 0.008736544173725004",
            "extra": "mean: 684.9791308000022 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_memory_efficiency_benchmark[cpu-config0]",
            "value": 0.6840666186523601,
            "unit": "iter/sec",
            "range": "stddev: 0.002416098550235455",
            "extra": "mean: 1.4618459266000172 sec\nrounds: 5"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_memory_efficiency_benchmark[cpu-config1]",
            "value": 0.2817320034907591,
            "unit": "iter/sec",
            "range": "stddev: 0.006795106645835042",
            "extra": "mean: 3.5494725044000917 sec\nrounds: 5"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_hybrid_model_stress_benchmark[cpu-config0]",
            "value": 7.07790834735542,
            "unit": "iter/sec",
            "range": "stddev: 0.0008040075659616754",
            "extra": "mean: 141.28467774997944 msec\nrounds: 8"
          },
          {
            "name": "benchmarks/benchmark_robustness.py::test_hybrid_model_stress_benchmark[cpu-config1]",
            "value": 2.634328061422377,
            "unit": "iter/sec",
            "range": "stddev: 0.057097036684982914",
            "extra": "mean: 379.6034422000048 msec\nrounds: 5"
          }
        ]
      }
    ]
  }
}