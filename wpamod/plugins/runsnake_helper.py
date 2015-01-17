from wpamod.plugins.base.analysis_plugin import AnalysisPlugin


class CPUUsageGUIShortcut(AnalysisPlugin):
    """
    Prints out commands used to view CPU usage using runsnake
    """
    def analyze(self):
        output = []

        for i, cpudump in enumerate(self.get_input_files('*.cpu')):
            output.append('runsnake %s' % cpudump)

        return output

    def get_output_name(self):
        return 'CPU usage viewer GUI'


class MemoryUsageGUIShortcut(AnalysisPlugin):
    """
    Prints out commands used to view CPU usage using runsnake for memory usage
    """
    def analyze(self):
        output = []

        for i, cpudump in enumerate(self.get_input_files('*.memory')):
            output.append('runsnakemem %s' % cpudump)

        return output

    def get_output_name(self):
        return 'Memory usage viewer GUI'
