import os
import logging
import json

from wpamod.plugins.base.analysis_plugin import AnalysisPlugin


class HTTPRequestCount(AnalysisPlugin):
    def analyze(self):
        req_file = os.path.join(self.input_directory, 'w3af-request-count.txt')
        logging.debug('Analyzing "%s" request count dump' % req_file)

        try:
            requests = json.load(file(req_file))
        except IOError:
            logging.error('File not found: "%s"' % req_file)
            return []

        return [('Total', requests)]

    def get_output_name(self):
        return 'HTTP requests sent'

