import logging

from meliae import loader

from wpamod.plugins.base.analysis_plugin import AnalysisPlugin


class MeliaeBasic(AnalysisPlugin):

    def analyze(self):
        memory_over_time = []

        for i, memdump in enumerate(self.get_input_files('*.memory')):
            logging.debug('Analyzing "%s" memory dump' % memdump)

            om = loader.load(memdump)
            om.remove_expensive_references()
            summary = om.summarize()
            total_memory = '%.1fMiB' % (summary.total_size / 1024. / 1024)

            memory_over_time.append((i, total_memory))

        return memory_over_time

    def get_output_name(self):
        return 'Total memory size'
