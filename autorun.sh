#!/bin/bash

cecho(){  # source: https://stackoverflow.com/a/53463162/2886168
    RED="\033[0;31m"
    GREEN="\033[0;32m"
    YELLOW="\033[0;33m"
    # ... ADD MORE COLORS
    NC="\033[0m" # No Color

    printf "${!1}${2} ${NC}\n"
}

cecho "GREEN" "Running RDMA Network Load Balancing Simulations"

TOPOLOGY=$1 # or, fat_k8_100G_OS2, fat_k_4_OS1, leaf_spine_128_100G_OS2
NETLOAD=$2 # network load 50%
RUNTIME="0.03" # 0.1 second (traffic generation)

cecho "YELLOW" "\n----------------------------------"
cecho "YELLOW" "TOPOLOGY: ${TOPOLOGY}" 
cecho "YELLOW" "NETWORK LOAD: ${NETLOAD}" 
cecho "YELLOW" "TIME: ${RUNTIME}" 
cecho "YELLOW" "----------------------------------\n"

echo -n "$(date) TOPOLOGY:${TOPOLOGY}, NETLOAD=${NETLOAD}, RUNTIME=${RUNTIME}, INDEX=[" >> ./mix/autorun_history.txt

if [ ! -f "mix/index.txt" ] || [ ! -s "mix/index.txt" ]; then
  echo "0" > "mix/index.txt"
fi

# Lossless RDMA
cecho "GREEN" "Run Lossless RDMA experiments..."
if [ -z "$3" ]; then
    lb_modes=("caver" "conga" "conweave" "hula" "fecmp") # "dv" "noshare" 
else
    lb_modes=("caver")
fi
for lb_mode in "${lb_modes[@]}"; do
  cecho "GREEN" "Run $lb_mode RDMA experiments..."

  echo -n "$lb_mode:$(cat mix/index.txt)," >> ./mix/autorun_history.txt

  python3 run.py --lb $lb_mode --pfc 1 --irn 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
  #python3 run.py --lb $lb_mode --pfc 1 --irn 0 --simul_time 0.1 --netload 50 --topo fat_k8_100G_OS1 --my_flow llm_flow 2>&1 > /dev/null &
  #python3 run.py --lb $lb_mode --pfc 1 --irn 0 --simul_time 0.03 --netload 60 --topo fat_k8_100G_OS2 --my_flow incast300 2>&1 > /dev/null &
  sleep 10
done
#python3 run.py --lb caver --pfc 1 --irn 0 --simul_time 0.01 --netload 30 --topo leaf_spine_128_100G_OS2
echo "]" >> ./mix/autorun_history.txt

#python3 run.py --lb hula --pfc 1 --irn 0 --simul_time 0.1 --netload 50 --topo leaf_spine_128_100G_OS2

# IRN RDMA
#cecho "GREEN" "Run IRN RDMA experiments..."
#python3 run.py --lb fecmp --pfc 0 --irn 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
#sleep 5
#python3 run.py --lb letflow --pfc 0 --irn 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
#sleep 5
#python3 run.py --lb conga --pfc 0 --irn 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
#sleep 5
#python3 run.py --lb conweave --pfc 0 --irn 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
#sleep 5
##python3 run.py --lb hula --pfc 0 --irn 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
#sleep 5
#python3 run.py --lb dv --pfc 0 --irn 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
#sleep 5


cecho "GREEN" "Runing all in parallel. Check the processors running on background!"
