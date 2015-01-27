import os
import glob


class AnalysisPlugin(object):
    def __init__(self, input_directory, pid):
        self.input_directory = input_directory
        self.pid = pid

    def get_input_files(self, mask):
        glob_path = os.path.join(self.input_directory, mask)
        files = glob.glob(glob_path)
        files.sort()

        for file_name in files:
            if 'w3af-' in file_name:
                if not file_name.startswith('w3af-%s' % self.pid):
                    files.remove(file_name)

        return files