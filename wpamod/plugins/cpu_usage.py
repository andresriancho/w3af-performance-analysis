import os
import pstats
import logging
import fnmatch

from wpamod.plugins.base.analysis_plugin import AnalysisPlugin, SPEED_SLOW

BLACKLIST = ['*/profiling/*', '*meliae*', '*pstats.py']
MAX_FUNC = 15


class CPUUsageByFunction(AnalysisPlugin):
    """
    Prints out the functions which take more CPU time.
    """

    SPEED = SPEED_SLOW

    def analyze(self):
        output = []

        for i, cpudump in enumerate(self.get_input_files('*.cpu')):
            logging.debug('Analyzing "%s" CPU usage dump' % cpudump)
            cpu_functions = []

            p = pstats.Stats(cpudump)
            print_list = p.sort_stats('cumulative').get_print_list((200,))[1]
            current = 1

            for filename, lineno, function in print_list:

                for blacklist_pattern in BLACKLIST:
                    if fnmatch.fnmatch(filename, blacklist_pattern):
                        break
                else:
                    where = '%s:%s (%s)' % (os.path.basename(filename),
                                            lineno, function)
                    cpu_functions.append((current, where))
                    current += 1

                if current == (MAX_FUNC + 1):
                    break

            dumpfname = os.path.split(cpudump)[1]
            output.append(('Measurement #%s (%s)' % (i, dumpfname),
                           tuple(cpu_functions)))

        return output

    def get_output_name(self):
        return 'CPU usage by function'
