import os
import logging
import json

from wpamod.plugins.base.analysis_plugin import AnalysisPlugin


class CoreStatus(AnalysisPlugin):

    DATA_KEYS = {'Requests per minute', 'Crawl queue input speed',
                 'Crawl queue output speed', 'Crawl queue size',
                 'Audit queue input speed', 'Audit queue output speed',
                 'Audit queue size'}

    def analyze(self):
        """
        Show the core status data, which looks like this:

            data = {'Requests per minute': s.get_rpm(),
                    'Crawl queue input speed': s.get_crawl_input_speed(),
                    'Crawl queue output speed': s.get_crawl_output_speed(),
                    'Crawl queue size': s.get_crawl_qsize(),
                    'Audit queue input speed': s.get_audit_input_speed(),
                    'Audit queue output speed': s.get_audit_output_speed(),
                    'Audit queue size': s.get_audit_qsize()}
        """
        output = []

        for i, core_dump in enumerate(self.get_input_files('*.core')):
            logging.debug('Analyzing "%s" core status dump' % core_dump)

            core_stat_json = json.load(file(core_dump))
            core_stats = core_stat_json.items()

            dumpfname = os.path.split(core_dump)[1]
            output.append(('Measurement #%s (%s)' % (i, dumpfname),
                           tuple(core_stats)))

        return output

    def get_output_name(self):
        return 'Core status summary'
