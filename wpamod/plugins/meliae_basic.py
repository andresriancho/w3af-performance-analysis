import logging

from wpamod.meliae_analysis.load_meliae import load_meliae
from wpamod.plugins.base.analysis_plugin import AnalysisPlugin, SPEED_SLOW


class MeliaeBasic(AnalysisPlugin):
    """
    Basic analysis of memory dumps with meliae

    http://jam-bazaar.blogspot.com.ar/2010/08/step-by-step-meliae.html
    http://jam-bazaar.blogspot.com.ar/2009/11/memory-debugging-with-meliae.html
    """
    SPEED = SPEED_SLOW

    def analyze(self):
        memory_over_time = []

        for i, memdump in enumerate(self.get_input_files('*.memory')):
            logging.debug('Analyzing "%s" memory dump' % memdump)

            om = load_meliae(memdump)

            if om is None:
                logging.error('Failed to load "%s"' % memdump)
                continue

            try:
                summary = om.summarize()
            except:
                logging.error('Failed to summarize "%s"' % memdump)
            else:
                total_memory = '%.1fMiB' % (summary.total_size / 1024. / 1024)
                memory_over_time.append((i, total_memory))

        return memory_over_time

    def generate_graph_data(self):
        """
        :return: The data to use in the HTML graph
        """
        raw_data = self.analyze()
        graph_data = []

        for measurement_idx, measurement_value in raw_data:
            graph_data.append(float(measurement_value.replace('MiB', '')))

        return graph_data

    def get_output_name(self):
        return 'Total memory referenced by Python GC'
