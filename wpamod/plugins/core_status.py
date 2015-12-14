import os
import logging
import json

from wpamod.plugins.base.analysis_plugin import AnalysisPlugin, SPEED_VERY_FAST

REQUESTS_PER_MINUTE = 'Requests per minute'


class CoreStatus(AnalysisPlugin):

    SPEED = SPEED_VERY_FAST

    DATA_KEYS = {REQUESTS_PER_MINUTE, 'Crawl queue input speed',
                 'Crawl queue output speed', 'Crawl queue size',
                 'Audit queue input speed', 'Audit queue output speed',
                 'Audit queue size'}
    CACHE_STATS = 'Cache stats'

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

            try:
                core_stat_json = json.load(file(core_dump))
            except ValueError:
                logging.debug('Ignoring %s - JSON decode failed!' % core_dump)
                continue

            if self.CACHE_STATS in core_stat_json:
                cache_stats = core_stat_json.pop(self.CACHE_STATS)
                core_stats_items = core_stat_json.items()
                core_stats_items.append((self.CACHE_STATS, tuple(cache_stats.items())))
            else:
                core_stats_items = core_stat_json.items()

            core_stats = list(core_stats_items)
            core_stats.sort()

            dumpfname = os.path.split(core_dump)[1]
            output.append(('Measurement #%s (%s)' % (i, dumpfname), core_stats))

        return output

    def generate_graph_data(self):
        """
        :return: The data to use in the HTML graph
        """
        raw_data = self.analyze()
        graph_data = {}

        for measurement_id, data in raw_data:
            key = int(measurement_id.split('#')[1].split(' ')[0])
            values = data
            graph_data[key] = dict(values)

        return graph_data

    def get_output_name(self):
        return 'Core status summary'
