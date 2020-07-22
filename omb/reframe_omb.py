""" Performance test using OSU's Micro Benchmarks (OMB).
            
    See README for details.
"""

import reframe as rfm
import reframe.utility.sanity as sn
from pprint import pprint
import sys, re
from collections import namedtuple
sys.path.append('.')
import modules
from modules.reframe_extras import sequence, Scheduler_Info

Metric = namedtuple('Metric', ['column', 'function', 'unit', 'label'])

@sn.sanity_function
def reduce(path, column, function):
    data = modules.omb.read_omb_out(path)
    return function(data[column])

class OSU_Micro_Benchmarks(rfm.RunOnlyRegressionTest):

    def __init__(self):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['omb']
        self.exclusive_access = True
        self.perf_patterns = {} # something funny about reframe's attr lookup
        self.add_metrics()
    
    def add_metrics(self):
        """ Add all Metrics from self.METRICS to sanity/performance/reference patterns """

        for metric in self.METRICS:
            self.sanity_patterns = sn.assert_found(re.escape(metric.column), self.stdout)
            self.perf_patterns[metric.label] = reduce(self.stdout, metric.column, metric.function)
            self.reference[metric.label] = (0, None, None, metric.unit) # oddly we don't have to supply the "*" scope key??

@rfm.simple_test
class Osu_alltoall(OSU_Micro_Benchmarks):
    # 'column', 'function', 'unit', 'label'
    METRICS = [Metric('Avg Latency(us)', min, 'us', "min_av_latency")]

    def __init__(self):
        super().__init__()
        self.executable = 'osu_alltoall'
        self.num_tasks_per_node = modules.reframe_extras.Scheduler_Info().pcores_per_node
        self.num_tasks = 2 * self.num_tasks_per_node

@rfm.simple_test
class Osu_allgather(OSU_Micro_Benchmarks):
    METRICS = [Metric('Avg Latency(us)', min, 'us', "min_av_latency")]

    def __init__(self):
        super().__init__()
        self.executable = 'osu_allgather'
        self.num_tasks_per_node = modules.reframe_extras.Scheduler_Info().pcores_per_node
        self.num_tasks = 2 * self.num_tasks_per_node

@rfm.simple_test
class Osu_allreduce(OSU_Micro_Benchmarks):
    
    METRICS = [Metric('Avg Latency(us)', min, 'us', "min_av_latency")]

    def __init__(self):
        super().__init__()
        self.executable = 'osu_allreduce '
        self.num_tasks_per_node = modules.reframe_extras.Scheduler_Info().pcores_per_node
        self.num_tasks = 2 * self.num_tasks_per_node


@rfm.simple_test
class Osu_bw(OSU_Micro_Benchmarks):

    METRICS = [Metric('Bandwidth (MB/s)', max, 'MB/s', "max_bandwidth")]

    def __init__(self):
        
        super().__init__()
        self.executable = 'osu_bw'
        self.num_tasks = 2
        self.num_tasks_per_node = 1

@rfm.simple_test
class Osu_latency(OSU_Micro_Benchmarks):

    METRICS = [Metric('Latency (us)', min, 'us', "min_latency")]

    def __init__(self):
        
        super().__init__()
        self.executable = 'osu_latency'
        self.num_tasks = 2
        self.num_tasks_per_node = 1

@rfm.simple_test
class Osu_bibw(OSU_Micro_Benchmarks):

    METRICS = [Metric('Bandwidth (MB/s)', max, 'MB/s', "max_bandwidth")]

    def __init__(self):
        
        super().__init__()
        self.executable = 'osu_bibw'
        self.num_tasks = 2
        self.num_tasks_per_node = 1

total_procs = modules.reframe_extras.sequence(2, 2 * modules.reframe_extras.Scheduler_Info().pcores_per_node + 2, 2)

@rfm.parameterized_test(*[[np] for np in total_procs])
class Osu_mbw_mr(OSU_Micro_Benchmarks):
    """ Determine bandwidth and message rate between two nodes with different numbers of processes per node.
        
        See https://downloads.openfabrics.org/Media/Sonoma2008/Sonoma_2008_Tues_QLogic-TomElken-MPIperformanceMeasurement.pdf
    """
    
    METRICS = [
        Metric('MB/s', max, 'MB/s', "max_bandwidth"),
        Metric('Messages/s', max, 'Messages/s', "max_message_rate"),
    ]

    def __init__(self, num_procs):
        
        super().__init__()
        self.executable = 'osu_mbw_mr'
        self.num_tasks = num_procs
        self.num_tasks_per_node = int(num_procs / 2)
        self.time_limit = '15m'
        

if __name__ == '__main__':
    # e.g:
    #(hpc-tests) [steveb@openhpc-login-0 hpc-tests]$ PYTHONPATH='reframe' python omb/reframe_omb.py
    pass