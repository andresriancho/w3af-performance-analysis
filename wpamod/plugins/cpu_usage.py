import os
import pstats
import logging

from wpamod.plugins.base.analysis_plugin import AnalysisPlugin


class CPUUsageByFunction(AnalysisPlugin):
    """
    Prints out the functions which take more CPU time.
    """
    def analyze(self):
        output = []

        for i, cpudump in enumerate(self.get_input_files('*.cpu')):
            logging.debug('Analyzing "%s" CPU usage dump' % cpudump)
            cpu_functions = []

            p = pstats.Stats(cpudump)
            s = p.strip_dirs().sort_stats('cumulative').get_print_list((20,))[1]

            for j, (filename, lineno, function) in enumerate(s):
                where = '%s:%s(%s)' % (filename, lineno, function)
                cpu_functions.append((j, where))

            dumpfname = os.path.split(cpudump)[1]
            output.append(('Measurement #%s (%s)' % (i, dumpfname),
                           tuple(cpu_functions)))

        return output

    def get_output_name(self):
        return 'CPU usage by function'
