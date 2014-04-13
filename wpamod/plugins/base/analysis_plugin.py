import os
import glob


class AnalysisPlugin(object):
    def __init__(self, input_directory):
        self.input_directory = input_directory

    def get_input_files(self, mask):
        glob_path = os.path.join(self.input_directory, mask)
        return glob.glob(glob_path)