window.BENCHMARK_DATA = {
  "lastUpdate": 1758620158268,
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
        "date": 1758620157902,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/benchmark_slos_core.py::test_build_graph_benchmark[dtype_pair0-cpu-config0]",
            "value": 19460.699869486973,
            "unit": "iter/sec",
            "range": "stddev: 0.000033228623153081966",
            "extra": "mean: 51.38561340067376 usec\nrounds: 2985"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_build_graph_benchmark[dtype_pair0-cpu-config1]",
            "value": 7900.139513664565,
            "unit": "iter/sec",
            "range": "stddev: 0.000044993722379697714",
            "extra": "mean: 126.58004308282642 usec\nrounds: 5826"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_build_graph_benchmark[dtype_pair0-cpu-config2]",
            "value": 2110.123817671391,
            "unit": "iter/sec",
            "range": "stddev: 0.00009602431922372876",
            "extra": "mean: 473.9058398495029 usec\nrounds: 1330"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_build_graph_benchmark[dtype_pair0-cpu-config3]",
            "value": 391.65413194425685,
            "unit": "iter/sec",
            "range": "stddev: 0.006631024382143878",
            "extra": "mean: 2.5532732031595864 msec\nrounds: 443"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_build_graph_benchmark[dtype_pair1-cpu-config0]",
            "value": 19507.4030760687,
            "unit": "iter/sec",
            "range": "stddev: 0.000028856825969886023",
            "extra": "mean: 51.26258969994733 usec\nrounds: 7631"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_build_graph_benchmark[dtype_pair1-cpu-config1]",
            "value": 7852.10529041946,
            "unit": "iter/sec",
            "range": "stddev: 0.000045445288394920943",
            "extra": "mean: 127.35437987823771 usec\nrounds: 2793"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_build_graph_benchmark[dtype_pair1-cpu-config2]",
            "value": 2143.675210306638,
            "unit": "iter/sec",
            "range": "stddev: 0.00006181636772992608",
            "extra": "mean: 466.4885777435272 usec\nrounds: 1312"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_build_graph_benchmark[dtype_pair1-cpu-config3]",
            "value": 353.3973576366524,
            "unit": "iter/sec",
            "range": "stddev: 0.008574750202282773",
            "extra": "mean: 2.8296759395359037 msec\nrounds: 430"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_benchmark[dtype_pair0-cpu-config0]",
            "value": 8088.165627259468,
            "unit": "iter/sec",
            "range": "stddev: 0.000011084019685069993",
            "extra": "mean: 123.63742856967585 usec\nrounds: 1610"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_benchmark[dtype_pair0-cpu-config1]",
            "value": 5718.87848389732,
            "unit": "iter/sec",
            "range": "stddev: 0.000011888331011173082",
            "extra": "mean: 174.85945938800867 usec\nrounds: 3792"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_benchmark[dtype_pair0-cpu-config2]",
            "value": 3663.8909406539274,
            "unit": "iter/sec",
            "range": "stddev: 0.00004786522623171955",
            "extra": "mean: 272.93388809807783 usec\nrounds: 2949"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_benchmark[dtype_pair0-cpu-config3]",
            "value": 1916.5006075050312,
            "unit": "iter/sec",
            "range": "stddev: 0.00001670211754867463",
            "extra": "mean: 521.78433760156 usec\nrounds: 1718"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_benchmark[dtype_pair1-cpu-config0]",
            "value": 8098.959495690032,
            "unit": "iter/sec",
            "range": "stddev: 0.00001013293365482878",
            "extra": "mean: 123.47265108958295 usec\nrounds: 5093"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_benchmark[dtype_pair1-cpu-config1]",
            "value": 5595.286825336103,
            "unit": "iter/sec",
            "range": "stddev: 0.000010467985009469375",
            "extra": "mean: 178.7218477293934 usec\nrounds: 4295"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_benchmark[dtype_pair1-cpu-config2]",
            "value": 3591.6858343389213,
            "unit": "iter/sec",
            "range": "stddev: 0.00001552557804805872",
            "extra": "mean: 278.4207879317646 usec\nrounds: 2867"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_benchmark[dtype_pair1-cpu-config3]",
            "value": 1716.192137462713,
            "unit": "iter/sec",
            "range": "stddev: 0.000016096347716943976",
            "extra": "mean: 582.6853405111389 usec\nrounds: 1486"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[8-dtype_pair0-cpu-config0]",
            "value": 8271.094048753692,
            "unit": "iter/sec",
            "range": "stddev: 0.000014960801225726313",
            "extra": "mean: 120.90298987117457 usec\nrounds: 6121"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[8-dtype_pair0-cpu-config1]",
            "value": 5921.951999508695,
            "unit": "iter/sec",
            "range": "stddev: 0.000011278576120982263",
            "extra": "mean: 168.8632397025446 usec\nrounds: 4710"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[8-dtype_pair1-cpu-config0]",
            "value": 8221.818133554407,
            "unit": "iter/sec",
            "range": "stddev: 0.000008919059501747819",
            "extra": "mean: 121.62759912176334 usec\nrounds: 5241"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[8-dtype_pair1-cpu-config1]",
            "value": 5879.936605086292,
            "unit": "iter/sec",
            "range": "stddev: 0.000011406048312457517",
            "extra": "mean: 170.06986081022964 usec\nrounds: 4713"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[16-dtype_pair0-cpu-config0]",
            "value": 8176.59877497693,
            "unit": "iter/sec",
            "range": "stddev: 0.000008920895633697914",
            "extra": "mean: 122.30024090949986 usec\nrounds: 4840"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[16-dtype_pair0-cpu-config1]",
            "value": 5760.871373212618,
            "unit": "iter/sec",
            "range": "stddev: 0.00001101950797611149",
            "extra": "mean: 173.58485118238949 usec\nrounds: 4482"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[16-dtype_pair1-cpu-config0]",
            "value": 8113.410062590803,
            "unit": "iter/sec",
            "range": "stddev: 0.000009698255350210473",
            "extra": "mean: 123.25273741688292 usec\nrounds: 6040"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[16-dtype_pair1-cpu-config1]",
            "value": 5350.107138204719,
            "unit": "iter/sec",
            "range": "stddev: 0.000032654041042661216",
            "extra": "mean: 186.91214477913422 usec\nrounds: 3792"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[32-dtype_pair0-cpu-config0]",
            "value": 8021.325357332203,
            "unit": "iter/sec",
            "range": "stddev: 0.000008875192517584086",
            "extra": "mean: 124.66767715461278 usec\nrounds: 5848"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[32-dtype_pair0-cpu-config1]",
            "value": 5301.190205501509,
            "unit": "iter/sec",
            "range": "stddev: 0.000011266703442194719",
            "extra": "mean: 188.63688364967788 usec\nrounds: 4263"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[32-dtype_pair1-cpu-config0]",
            "value": 7842.074710917811,
            "unit": "iter/sec",
            "range": "stddev: 0.000009730514338476745",
            "extra": "mean: 127.51727532100537 usec\nrounds: 5223"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[32-dtype_pair1-cpu-config1]",
            "value": 5187.132867898836,
            "unit": "iter/sec",
            "range": "stddev: 0.000012449132011784353",
            "extra": "mean: 192.78472818550964 usec\nrounds: 4183"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[64-dtype_pair0-cpu-config0]",
            "value": 7557.113062034467,
            "unit": "iter/sec",
            "range": "stddev: 0.000013810909327390509",
            "extra": "mean: 132.3256634896485 usec\nrounds: 3988"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[64-dtype_pair0-cpu-config1]",
            "value": 4772.94882663364,
            "unit": "iter/sec",
            "range": "stddev: 0.000010800184260038937",
            "extra": "mean: 209.5140837085613 usec\nrounds: 3775"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[64-dtype_pair1-cpu-config0]",
            "value": 7520.018215079483,
            "unit": "iter/sec",
            "range": "stddev: 0.000008708308013507705",
            "extra": "mean: 132.9784013015759 usec\nrounds: 4610"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[64-dtype_pair1-cpu-config1]",
            "value": 4423.8763444690385,
            "unit": "iter/sec",
            "range": "stddev: 0.000032479276071943",
            "extra": "mean: 226.0461012320682 usec\nrounds: 3408"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[128-dtype_pair0-cpu-config0]",
            "value": 7106.949127858129,
            "unit": "iter/sec",
            "range": "stddev: 0.000009481904077061234",
            "extra": "mean: 140.70735304410107 usec\nrounds: 5141"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[128-dtype_pair0-cpu-config1]",
            "value": 3947.648576053734,
            "unit": "iter/sec",
            "range": "stddev: 0.000011377839115161745",
            "extra": "mean: 253.31535488390654 usec\nrounds: 2846"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[128-dtype_pair1-cpu-config0]",
            "value": 6852.650458715577,
            "unit": "iter/sec",
            "range": "stddev: 0.000010978766550754162",
            "extra": "mean: 145.92893742714472 usec\nrounds: 4315"
          },
          {
            "name": "benchmarks/benchmark_slos_core.py::test_compute_batched_benchmark[128-dtype_pair1-cpu-config1]",
            "value": 3597.8067192769704,
            "unit": "iter/sec",
            "range": "stddev: 0.000012828664321833412",
            "extra": "mean: 277.94711556961124 usec\nrounds: 2916"
          }
        ]
      }
    ]
  }
}