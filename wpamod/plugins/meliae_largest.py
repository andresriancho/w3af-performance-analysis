import logging

from wpamod.meliae_analysis.load_meliae import load_meliae
from wpamod.meliae_analysis.largest_object import largest_object
from wpamod.plugins.base.analysis_plugin import AnalysisPlugin, SPEED_SLOW


class MeliaeLargestObject(AnalysisPlugin):
    """
    Get the largest objects in memory
    """
    SPEED = SPEED_SLOW

    def analyze(self):
        largest_memory_objects = []

        for i, memdump in enumerate(self.get_input_files('*.memory')):

            msg = ('Analyzing largest objects in "%s" memory dump. This'
                   ' operation might take some minutes to complete')
            logging.debug(msg % memdump)

            om = load_meliae(memdump)

            if om is None:
                logging.error('Failed to load "%s"' % memdump)
                continue

            try:
                result = largest_object(om)
            except:
                logging.error('Failed to summarize "%s"' % memdump)
                continue

            data = []

            for result_num, summary in enumerate(result):
                tmp = []
                s = summary
                total = '%s bytes' % s.get_total_size()

                tmp.extend([('Total referenced memory', total),
                            ('Type', s.get_type()),
                            ('Number of children', s.get_child_len()),
                            ('Raw', str(s.meliae_obj))])

                child_types = s.get_child_types()
                child_values = s.get_child_values()

                if child_types:
                    tmp.append(('Child types', s.get_child_types()))

                if child_values:
                    tmp.append(('Child values', s.get_child_values()))

                data.append(('Top #%s' % result_num, tmp))

            largest_memory_objects.append(('File dump #%s' % i, data))

        return largest_memory_objects

    def get_output_name(self):
        return 'Largest objects in memory'

