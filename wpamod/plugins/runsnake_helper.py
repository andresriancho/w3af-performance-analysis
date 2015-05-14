from wpamod.plugins.base.analysis_plugin import AnalysisPlugin, SPEED_VERY_FAST


class CPUUsageGUIShortcut(AnalysisPlugin):
    """
    Prints out commands used to view CPU usage using runsnake
    """
    SPEED = SPEED_VERY_FAST

    def analyze(self):
        output = []

        for i, cpudump in enumerate(self.get_input_files('*.cpu')):
            output.append((i, 'runsnake %s' % cpudump))

        return output

    def get_output_name(self):
        return 'CPU usage viewer GUI'


class MemoryUsageGUIShortcut(AnalysisPlugin):
    """
    Prints out commands used to view CPU usage using runsnake for memory usage
    """
    SPEED = SPEED_VERY_FAST

    def analyze(self):
        output = []

        for i, cpudump in enumerate(self.get_input_files('*.memory')):
            output.append((i, 'runsnakemem %s' % cpudump))

        return output

    def get_output_name(self):
        return 'Memory usage viewer GUI'
