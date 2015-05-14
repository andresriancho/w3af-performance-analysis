import os
import glob
import logging

SPEED_SLOW = 4
SPEED_MEDIUM = 3
SPEED_FAST = 2
SPEED_VERY_FAST = 1


class AnalysisPlugin(object):

    SPEED = SPEED_FAST

    def __init__(self, input_directory, pid):
        self.input_directory = input_directory
        self.pid = pid

    def get_input_files(self, mask):
        glob_path = os.path.join(self.input_directory, mask)
        files = glob.glob(glob_path)
        files.sort()

        filter_accepted = []

        for file_name in files:
            if 'w3af-' in file_name:

                pid_start = 'w3af-%s' % self.pid
                if pid_start not in file_name:
                    logging.debug('Ignoring file %s' % file_name)
                else:
                    logging.debug('Filter accepted file %s' % file_name)
                    filter_accepted.append(file_name)

        return filter_accepted