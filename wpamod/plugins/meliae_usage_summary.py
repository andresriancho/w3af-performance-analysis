import logging

from wpamod.meliae_analysis.load_meliae import load_meliae
from wpamod.plugins.base.analysis_plugin import AnalysisPlugin


class MeliaeUsageSummary(AnalysisPlugin):
    def analyze(self):
        """
        Show a summary of two memory dumps:
            * First,
            * Before last
        """
        memory_summaries = []

        input_files = self.get_input_files('*.memory')
        if len(input_files) <= 1:
            return []

        first_mem_dump = input_files[0]
        before_last_mem_dump = input_files[-2]
        tasks = (('First', first_mem_dump),
                 ('Before last', before_last_mem_dump))
        spaces = ' ' * 8

        for name, memdump in tasks:
            logging.debug('Analyzing "%s" memory dump' % memdump)

            om = load_meliae(memdump)

            if om is None:
                logging.error('Failed to load "%s"' % memdump)
                continue

            summary = repr(om.summarize())
            summary = summary.replace('\n', '\n%s' % spaces)
            summary = ('\n%s' % spaces) + summary

            memory_summaries.append((name, summary))

        return memory_summaries

    def get_output_name(self):
        return 'Memory usage summary'
