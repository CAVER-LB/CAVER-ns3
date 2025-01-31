## Run NS-3 on Ubuntu 20.04

This is an NS-3 simulator for "CAVER: Enhancing RDMA Load Balancing by Hunting Less-Congested Paths". We add CAVER's components to  [ConWeave(SIGCOMM'2023)'s NS-3 simulator](https://github.com/conweave-project/conweave-ns3) to simulate RDMA load balancing performance with various algorithms.

We describe how to run this repository using your local machine with `ubuntu:20.04`.

#### 0. Prerequisites

We tested the simulator on Ubuntu 20.04, but latest versions of Ubuntu should also work. 

Firstly, use the following command to install the required dependencies

```
sudo apt install build-essential python3 libgtk-3-0 bzip2 python2
```

For plotting, we use `numpy`, `matplotlib`, `pandas` and `cycler` for python3:

```
python3 -m pip install numpy matplotlib cycler pandas
```

#### 1. Configure & Build
Run following commands to configure and build simulation:
```
wget https://www.nsnam.org/releases/ns-allinone-3.19.tar.bz2
tar -xvf ns-allinone-3.19.tar.bz2
cd ns-allinone-3.19
rm -rf ns-3.19
git clone https://github.com/CAVER-LB/CAVER-ns3.git ns-3.19
cd ns-3.19
./waf configure --build-profile=optimized
./waf
```

#### 2. Run

To run the simulation, use the following command:

```
./autorun <topology> <load>
```

For example:

```
./autorun.sh fat_k8_100G_OS2 60
```

All topology files are stored in the ./config directory, along with various traffic workloads that were used to reproduce the results from our paper. We will explain these workloads in more detail later.

Each experiment will be assigned a unique ID. The results will be stored in the ./mix/output/ directory and logged in `./mix/autorun_history.txt`. For example, after running:

```
./autorun.sh fat_k8_100G_OS2 60
```

the `./mix/autorun_history.txt` file will include an entry like:

```
Thu Jan 31 14:25:16 PST 2025 TOPOLOGY:fat_k8_100G_OS2, NETLOAD=60, RUNTIME=0.03, INDEX=[caver:3,conga:4,conweave:5,hula:6,fecmp:7,]
```

In this case, 3, 4, 5, 6, 7 represent the experiment IDs.

To analyze the experiments, use the functions in `analysis/deep_analyse.py`. For example, you can call:

```
print(get_basic_result('3-7'))
```

This will return the average FCT slowdown, P99 FCT slowdown, large FCT slowdown, and small FCT slowdown for the experiments with IDs 3, 4, 5, 6, 7.

**Note**: Due to random factors, the results of each experiment may vary slightly.

#### 3. Reproduce

We also provide a simpler way to reproduce the experiments in the paper. You can use functions in `caver_run.py`. In particular:

- You can use `run_normal` in `caver_run.py` and `plot_overall_fctslowdown` in `analysis/deep_analyse.py` to reproduce Fig 7, Fig 17 in paper.
- You can use `run_caver_pathnum_ce_experiments` in `caver_run.py` to reproduce Fig 20 in paper.
- You can use `run_caver_patchoiceTimeout_experiments` in `caver_run.py` to reproduce Table 1 in paper.
- You can use `run_experiments_with_topology` in `caver_run.py` to reproduce Fig 8 in paper.
- You can use `run_with_traffic_patterns` in `caver_run.py` to reproduce Fig 9, Fig18, and Table 4 in paper.

