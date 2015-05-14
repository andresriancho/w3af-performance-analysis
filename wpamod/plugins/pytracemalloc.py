import os
import logging

from tracemalloc import Snapshot, Filter

from wpamod.plugins.base.analysis_plugin import AnalysisPlugin, SPEED_MEDIUM


class PyTraceMallocSummary(AnalysisPlugin):
    """
    Prints out the Top10 lines of code where memory is allocated
    """

    SPEED = SPEED_MEDIUM

    def analyze(self):
        output = []

        for i, tracedump in enumerate(self.get_input_files('*.tracemalloc')):
            logging.debug('Analyzing "%s" tracemalloc dump' % tracedump)

            try:
                snapshot = Snapshot.load(tracedump)
                snapshot = filter_traces(snapshot)
            except Exception, e:
                logging.error('Exception in PyTraceMallocSummary: "%s"' % e)
                continue

            top = format_top(snapshot)
            output.append(('Measurement #%s' % i, top))

            trace = format_tracebacks(snapshot)
            output.append(('Traceback #%s' % i, trace))

            #break

        return output

    def get_output_name(self):
        return 'Top 15 lines of code where memory is allocated'


def filter_traces(snapshot):
    snapshot = snapshot.filter_traces((
        # Some default ignores
        Filter(False, "<frozen importlib._bootstrap>"),
        Filter(False, "<unknown>"),

        # Ignore the impact of profiling tools
        Filter(False, "*tracemalloc*"),
        Filter(False, "*yappi*"),
        Filter(False, "*meliae*"),
        Filter(False, "*controllers/profiling*"),
    ))
    return snapshot


def format_tracebacks(snapshot, limit=3):
    """
    :return: Tracebacks for malloc
    """
    output = []
    top_stats = snapshot.statistics('traceback')

    for i in xrange(min(limit, len(top_stats))):
        stat = top_stats[i]

        key = "%s memory blocks: %.1f KiB" % (stat.count, stat.size / 1024)

        value = ''
        for line in stat.traceback.format():
            value += line + '\n'

        output.append((key, [value]))

    return output


def format_top(snapshot, group_by='lineno', limit=15):
    """
    :return: A list of top N lines based on how much they malloc
    """
    top_stats = snapshot.statistics(group_by)

    lines = []

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

    return lines

