import os
import re
import logging

from wpamod.plugins.base.analysis_plugin import AnalysisPlugin, SPEED_MEDIUM


class LogParser(AnalysisPlugin):
    """
    Summarize the log message types
    """
    SPEED = SPEED_MEDIUM

    LOG_RE = re.compile('\[.* - (.*?)\]')

    IS_NOT_A_404_RE = re.compile('is NOT a 404')
    IS_A_404_RE = re.compile('is a 404 ')
    RETURNED_404_RE = re.compile('returned HTTP code "404"')

    def analyze(self):
        log_file = os.path.join(self.input_directory, 'w3af-log-output.txt')
        logging.debug('Analyzing "%s" log' % log_file)

        try:
            log_file_handler = file(log_file)
        except IOError:
            logging.error('File not found: "%s"' % log_file)
            return []

        log_type_count = {}
        four_o_four_data = {}

        for line in log_file_handler:
            line = line.strip()

            #
            #   Count the log types
            #
            match = self.LOG_RE.search(line)

            if match:
                log_type = match.group(1)
                log_type = log_type.lower()

                if log_type in log_type_count:
                    log_type_count[log_type] += 1
                else:
                    log_type_count[log_type] = 1

            #
            #   Count the 404s
            #
            is_not_404 = self.IS_NOT_A_404_RE.search(line)
            is_a_404 = self.IS_A_404_RE.search(line)
            returned_404 = self.RETURNED_404_RE.search(line)

            if is_a_404 or is_not_404 or returned_404:
                if is_not_404:
                    log_type = 'Tagged as NOT 404'
                elif is_a_404:
                    log_type = 'Tagged as 404'
                else:
                    log_type = 'HTTP response status is 404'

                if log_type in four_o_four_data:
                    four_o_four_data[log_type] += 1
                else:
                    four_o_four_data[log_type] = 1

        log_type_result = log_type_count.items()
        log_type_result.sort(sort_second)
        log_type_result.reverse()

        four_o_four_result = four_o_four_data.items()

        return [('Log types', log_type_result),
                ('404 analysis', four_o_four_result)]

    def get_output_name(self):
        return 'Log parser'


def sort_second(a, b):
    return cmp(a[1], b[1])