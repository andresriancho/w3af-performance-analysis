import logging

from wpamod.plugins.base.analysis_plugin import AnalysisPlugin
from wpamod.utils.load_meliae import load_meliae


class MeliaeBasic(AnalysisPlugin):
    """
    Basic analysis of memory dumps with meliae

    http://jam-bazaar.blogspot.com.ar/2010/08/step-by-step-meliae.html
    http://jam-bazaar.blogspot.com.ar/2009/11/memory-debugging-with-meliae.html
    """
    def analyze(self):
        memory_over_time = []

        for i, memdump in enumerate(self.get_input_files('*.memory')):
            logging.debug('Analyzing "%s" memory dump' % memdump)

            try:
                om = load_meliae(memdump)
            except KeyError, ke:
                logging.error('Failed to load "%s": %s' % (memdump, ke))

            summary = om.summarize()
            total_memory = '%.1fMiB' % (summary.total_size / 1024. / 1024)

            memory_over_time.append((i, total_memory))

        return memory_over_time

    def get_output_name(self):
        return 'Total memory size'
