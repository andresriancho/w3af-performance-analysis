import os
import logging
import tracemalloc

from tracemalloc import Snapshot, Filter

from wpamod.plugins.base.analysis_plugin import AnalysisPlugin


class PyTraceMallocSummary(AnalysisPlugin):
    """
    Prints out the Top10 lines of code where memory is allocated
    """
    def analyze(self):
        output = []

        for i, tracedump in enumerate(self.get_input_files('*.tracemalloc')):
            logging.debug('Analyzing "%s" tracemalloc dump' % tracedump)

            try:
                snapshot = Snapshot.load(tracedump)
                top = format_top(snapshot)
            except Exception, e:
                logging.error('Exception in PyTraceMallocSummary: "%s"' % e)
            else:
                output.append(('Measurement #%s' % i, top))

            #break

        return output

    def get_output_name(self):
        return 'Top 15 lines of code where memory is allocated'


def format_top(snapshot, group_by='lineno', limit=15):
    snapshot = snapshot.filter_traces((
        # Some default ignores
        Filter(False, "<frozen importlib._bootstrap>"),
        Filter(False, "<unknown>"),

        # Ignore the impact of profiling tools
        Filter(False, "*tracemalloc*"),
        Filter(False, "*yappi*"),
        Filter(False, "*meliae*"),
    ))
    top_stats = snapshot.statistics(group_by)

    lines = []
    output = [("Top %s lines" % limit, lines)]

    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        lines.append(('%-2s' % index,
                      "%-35s:%-4s - %.1f KiB" % (filename,
                                                 frame.lineno,
                                                 stat.size / 1024)))

    # Blank line
    lines.append(('--', '--'))

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        lines.append(("%s other" % len(other), "%.1f KiB" % (size / 1024)))

    total = sum(stat.size for stat in top_stats)
    lines.append(("Total allocated size", "%.1f KiB" % (total / 1024)))

    return output

