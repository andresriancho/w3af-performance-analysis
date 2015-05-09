import os
import re
import logging

from wpamod.plugins.base.analysis_plugin import AnalysisPlugin


class LogParser(AnalysisPlugin):
    """
    Summarize the log message types
    """
    LOG_RE = re.compile('\[.* - (.*?)\]')

    def analyze(self):
        log_file = os.path.join(self.input_directory, 'w3af-log-output.txt')
        logging.debug('Analyzing "%s" log' % log_file)

        try:
            log_file_handler = file(log_file)
        except IOError:
            logging.error('File not found: "%s"' % log_file)
            return []

        log_type_count = {}

        for line in log_file_handler:
            line = line.strip()
            match = self.LOG_RE.search(line)

            if match:
                log_type = match.group(1)
                log_type = log_type.lower()

                if log_type in log_type_count:
                    log_type_count[log_type] += 1
                else:
                    log_type_count[log_type] = 0

        result = log_type_count.items()
        result.sort(sort_second)
        result.reverse()

        return result

    def get_output_name(self):
        return 'Log message types'


def sort_second(a, b):
    return cmp(a[1], b[1])