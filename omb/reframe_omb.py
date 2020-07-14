""" Performance test using OSU's Micro Benchmarks (OMB).

    This runs:
        osu_bw: 2x nodes, 1x process per node
        osu_latency: 2x nodes, 1x process per node
        osu_bibw (Bidirectional Bandwidth Test): 2x nodes, 1x process per node
        osu_mbw_mr (Multiple Bandwidth / Message Rate Test): 2x nodes, range of process numbers from 1 per CPU (x a "cpu_factor") down to 1 per node

    Run using e.g.:
        
        cd hpc-tests
        conda activate hpc-tests
        reframe/bin/reframe -C reframe_config.py -c omb/ --run --performance-report

"""

import reframe as rfm
import reframe.utility.sanity as sn
from pprint import pprint
import sys, re
from collections import namedtuple
sys.path.append('.')
import modules

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

n_tasks = modules.reframe_extras.ntasks_param(cpu_factor=0.5) # because alaska has HT enabled TODO: add to config?

@rfm.parameterized_test(*[[n] for n in n_tasks]) # because alaska has HT enabled TODO: add to config?
class Osu_mbw_mr(OSU_Micro_Benchmarks):
    """ Determine bandwidth and message rate between two nodes with different numbers of processes per node.
        
        See https://downloads.openfabrics.org/Media/Sonoma2008/Sonoma_2008_Tues_QLogic-TomElken-MPIperformanceMeasurement.pdf
    """
    
    METRICS = [
        Metric('MB/s', max, 'MB/s', "max_bandwidth"),
        Metric('Messages/s', max, 'Messages/s', "max_message_rate"),
    ]

    def __init__(self, num_cpus):
        
        super().__init__()
        self.executable = 'osu_mbw_mr'
        self.num_tasks = num_cpus
        self.num_tasks_per_node = int(num_cpus / 2)
    
    @rfm.run_before('run')
    def add_launcher_options(self):
        self.job.launcher.options = ['--distribution=block'] # is default, but important here that 1st 1/2 of processes are on 1st node


if __name__ == '__main__':
    # e.g:
    #(hpc-tests) [steveb@openhpc-login-0 hpc-tests]$ PYTHONPATH='reframe' python omb/reframe_omb.py
    print(ntasks_param())