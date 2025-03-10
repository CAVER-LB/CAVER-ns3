import sys
import random
import math
import heapq
from optparse import OptionParser

from custom_rand import CustomRand
import numpy as np

class Flow:
	def __init__(self, src, dst, size, t):
		self.src, self.dst, self.size, self.t = src, dst, size, t
	def __str__(self):
		return "%d %d 3 %d %.9f"%(self.src, self.dst, self.size, self.t)

def translate_bandwidth(b):
	if b == None:
		return None
	if type(b)!=str:
		return None
	if b[-1] == 'G':
		return float(b[:-1])*1e9
	if b[-1] == 'M':
		return float(b[:-1])*1e6
	if b[-1] == 'K':
		return float(b[:-1])*1e3
	return float(b)

def poisson(lam):
	return -math.log(1-random.random())*lam

def generate_normal_integer(mean, std_dev):
    random_float = np.random.normal(mean, std_dev)
    random_int = int(round(random_float))
    return random_int

def get_random_host_by_pod(pod_size, pod_no):
	return random.randint(pod_size * pod_no, pod_size * (pod_no + 1) - 1)

def gini_coefficient(data):
    """
    计算基尼系数
    :param data: 输入数据，必须为一维数组或列表
    :return: 基尼系数
    """
    data = np.array(data)
    if data.size == 0:
        return None
    if np.any(data < 0):
        raise ValueError("数据中存在负值，基尼系数仅适用于非负值。")
    sorted_data = np.sort(data)
    n = len(data)
    cumulative_sum = np.cumsum(sorted_data)
    gini = (2 / n) * np.sum((np.arange(1, n + 1) * sorted_data)) / cumulative_sum[-1] - (n + 1) / n
    return gini

def classify_and_calculate_gini_with_pandas(flows):
    """
    使用 pandas 对 flows 数据分类，并计算平均基尼系数
    :param flows: 包含 Flow 对象的列表
    :return: 平均基尼系数
    """
    # 将 flows 转换为 pandas DataFrame
    data = pd.DataFrame([{'src': flow.src, 'dst': flow.dst, 'size': flow.size, 't': flow.t} for flow in flows])
    
    # 按 src 分组，并对每组计算基尼系数
    gini_values = data.groupby('src')['t'].apply(gini_coefficient).dropna()
    
    # 计算平均基尼系数
    average_gini = gini_values.mean()
    
    return average_gini

def interval_difference_statistic(times):
    """
    计算间隔差异统计
    :param times: 一维数组或列表，表示时间点
    :return: 间隔差异统计值（标准差/平均间隔）
    """
    times = np.array(times)
    if len(times) < 2:
        return None  # 无法计算间隔

    # 排序时间点
    sorted_times = np.sort(times)

    # 计算相邻时间点的间隔
    intervals = np.diff(sorted_times)

    # 计算间隔的标准差和均值
    interval_std = np.std(intervals)
    interval_mean = np.mean(intervals)

    # 返回标准差与均值的比值作为差异统计
    if interval_mean > 0:
        return interval_std / interval_mean
    else:
        return None  # 避免除零

def classify_and_calculate_difference_with_pandas(flows):
    """
    使用 pandas 对 flows 数据分类，并计算基于时间间隔的统计值
    :param flows: 包含 Flow 对象的列表
    :return: 平均间隔差异统计值
    """
    # 将 flows 转换为 pandas DataFrame
    data = pd.DataFrame([{'src': flow.src, 'dst': flow.dst, 'size': flow.size, 't': flow.t} for flow in flows])

    # 按 src 分组，并对每组时间点计算间隔差异统计
    difference_values = data.groupby('src')['t'].apply(interval_difference_statistic).dropna()

    # 计算平均间隔差异统计值
    average_difference = difference_values.mean()

    return average_difference

if __name__ == "__main__":
	port = 80
	parser = OptionParser()
	parser.add_option("-c", "--cdf", dest = "cdf_file", help = "the file of the traffic size cdf", default = "AliStorage2019.txt")
	parser.add_option("-n", "--nhost", dest = "nhost", help = "number of hosts", default = 256)
	parser.add_option("-l", "--load", dest = "load", help = "the percentage of the traffic load to the network capacity, by default 0.3", default = "0.3")
	parser.add_option("-b", "--bandwidth", dest = "bandwidth", help = "the bandwidth of host link (G/M/K), by default 10G", default = "100G")
	parser.add_option("-t", "--time", dest = "time", help = "the total run time (s), by default 10", default = "0.03")
	parser.add_option("-o", "--output", dest = "output", help = "the output file", default = "tmp_traffic.txt")
	
	
	options,args = parser.parse_args()

	base_t = 2000000000 # 2000000000

	if not options.nhost:
		print("please use -n to enter number of hosts")
		sys.exit(0)
	nhost = int(options.nhost)
	load = float(options.load)
	bandwidth = translate_bandwidth(options.bandwidth)
	time = float(options.time)*1e9 # translates to ns
	output = options.output
	if bandwidth == None:
		print("bandwidth format incorrect")
		sys.exit(0)

	fileName = options.cdf_file
	file = open(fileName,"r")
	lines = file.readlines()
	# read the cdf, save in cdf as [[x_i, cdf_i] ...]
	cdf = []
	for line in lines:
		x,y = map(float, line.strip().split(' '))
		cdf.append([x,y])

	# create a custom random generator, which takes a cdf, and generate number according to the cdf
	customRand = CustomRand()
	if not customRand.setCdf(cdf):
		print("Error: Not valid cdf")
		sys.exit(0)

	ofile = open(output, "w")

	# generate flows
	avg = customRand.getAvg()
	flows = []
    # 首先，生成random流量
	avg_inter_arrival = 1/(bandwidth*load/8./avg)*1000000000 
	#n_flow_estimate = int(time / avg_inter_arrival * nhost)
	#n_flow = 0
	host_list = [(base_t + int(poisson(avg_inter_arrival)), i) for i in range(nhost)]# (时间，hostid)
	heapq.heapify(host_list)
	while len(host_list) > 0:
		t,src = host_list[0]
		inter_t = int(poisson(avg_inter_arrival))
		dst = random.randint(0, nhost-1)
		while (dst == src):
			dst = random.randint(0, nhost-1)
		if (t + inter_t > time + base_t):
			heapq.heappop(host_list)
		else:
			size = int(customRand.rand())
			if size <= 0:
				size = 1
			#n_flow += 1
			flows.append(Flow(src, dst, size, t * 1e-9))
			heapq.heapreplace(host_list, (t + inter_t, src))

	flows.sort(key=lambda x : x.t)
	ofile.write(f"{len(flows)}\n")
	for f in flows:
		ofile.write(f.__str__() + '\n')
	ofile.close()
