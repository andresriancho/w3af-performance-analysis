import logging
import json
import humanize

from wpamod.plugins.base.analysis_plugin import AnalysisPlugin, SPEED_FAST


class PSUtilSummary(AnalysisPlugin):

    SPEED = SPEED_FAST

    def analyze(self, humanize_bytes=True):
        """
        Show a summary of memory usage for python processes
        """
        output = []

        input_files = self.get_input_files('*.psutil')
        if len(input_files) == 0:
            return []

        for i, input_file in enumerate(input_files):
            try:
                psutil_data = json.loads(file(input_file).read())
            except:
                logging.debug('Failed to load JSON from %s' % input_file)
            else:
                self._process_psutil_memory_data(i, psutil_data,
                                                 output, input_file,
                                                 humanize_bytes=humanize_bytes)

        return output

    def generate_graph_data(self):
        """
        :return: The data to use in the HTML graph
        """
        raw_data = self.analyze(humanize_bytes=False)
        graph_data = []

        for measurement in raw_data:
            rss = float(measurement[1][0][1][0][1])
            graph_data.append(rss)

        return graph_data

    def _process_psutil_memory_data(self, count, psutil_data, output,
                                    input_file, humanize_bytes=True):
        """
        :param psutil_data: A dict containing the data
        :param output: A list with our parsed output
        :return: None
        """
        processes = psutil_data['Processes']
        memory_usage = []

        for pid, data in processes.iteritems():
            if self._is_w3af(data):
                target = self._get_process_target(pid)
                pid_target = '%s - %s' % (pid, target)

                usage = float(data['memory_percent'])
                usage = '%0.2f %%' % usage

                if humanize_bytes:
                    shared = humanize.naturalsize(data['memory_info_ex']['shared'])
                    rss = humanize.naturalsize(data['memory_info_ex']['rss'])
                else:
                    shared = data['memory_info_ex']['shared'] / 1024 / 1024
                    rss = data['memory_info_ex']['rss'] / 1024 / 1024

                process_data = [('rss', rss),
                                ('shared', shared),
                                ('Percent OS used', usage)]

                memory_usage.append((pid_target, process_data))

        if not psutil_data['ps_mem']:
            logging.warning('No ps_mem dump in "%s"' % input_file)
        else:
            if humanize_bytes:
                for key, value in psutil_data['ps_mem'][0].items():
                    try:
                        psutil_data['ps_mem'][0][key] = humanize.naturalsize(value * 1024)
                    except:
                        continue

            memory_usage.append(('Program memory by psmem',
                                 psutil_data['ps_mem'][0].items()))

        output.append(('Measurement #%s' % count, memory_usage))

    def _get_process_target(self, pid):
        input_files = self.get_input_files('*.processes')
        for input_file in input_files:
            try:
                process_data = json.loads(file(input_file).read())
            except:
                logging.debug('Failed to load JSON from %s' % input_file)
            else:
                if pid in process_data:
                    return process_data[pid]['name'] + '.' + process_data[pid]['target']

        return '(unknown subprocess target function)'

    def _is_w3af(self, data):
        if data['exe'] is None:
            return False

        return 'python' in data['exe']

    def get_output_name(self):
        return 'PSUtils memory usage summary'
