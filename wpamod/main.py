import logging
import argparse
import sys

from wpamod.utils.show_results import show_result
from wpamod.plugins.meliae_basic import MeliaeBasic
from wpamod.plugins.meliae_largest import MeliaeLargestObject
from wpamod.plugins.meliae_usage_summary import MeliaeUsageSummary
from wpamod.plugins.sys_info import SystemInformation
from wpamod.plugins.cpu_usage import CPUUsageByFunction
from wpamod.plugins.runsnake_helper import CPUUsageGUIShortcut, MemoryUsageGUIShortcut
from wpamod.plugins.psutil_summary import PSUtilSummary
from wpamod.plugins.core_status import CoreStatus
from wpamod.plugins.pytracemalloc import PyTraceMallocSummary
from wpamod.plugins.request_count import HTTPRequestCount
from wpamod.plugins.log_parser import LogParser
from wpamod.utils.log import configure_logging
from wpamod.utils.cache import save_cache, clear_cache, get_from_cache
from wpamod.utils.is_valid_pid import is_valid_pid

# Leave the plugins list in this format so it's easier to comment the plugins
# we don't need during development/testing
PLUGINS = [
           MeliaeBasic,
           MeliaeUsageSummary,
           MeliaeLargestObject,
           CPUUsageByFunction,
           CoreStatus,
           CPUUsageGUIShortcut,
           MemoryUsageGUIShortcut,
           PSUtilSummary,
           PyTraceMallocSummary,
           SystemInformation,
           HTTPRequestCount,
           LogParser
]


def main():
    args = parse_args()

    configure_logging(args.debug)
    logging.debug('Starting performance analysis')

    if args.clear_cache:
        clear_cache(args.directory)

    if args.pid is None:
        # Find the main/parent PID and use that for the rest of the analysis
        pid = get_main_pid(args.directory)
    else:
        if not is_valid_pid(args.directory, args.pid):
            sys.exit(-1)
        else:
            pid = args.pid

    enabled_plugins = filter_enabled_plugins(args)

    for plugin_klass in sorted(enabled_plugins, plugin_speed_cmd):
        plugin_inst = plugin_klass(args.directory, pid)
        name = plugin_inst.get_output_name()

        data = get_from_cache(args.directory, pid, name)

        if data is None:
            data = plugin_inst.analyze()
            save_cache(args.directory, pid, name, data)

        if data:
            show_result(name, data)
        else:
            logging.debug('No data for %s' % name)


def get_main_pid(directory):
    """
    :param directory: The directory where the profiling dump lives
    :return: The PID of the main w3af process
    """
    mask = 'w3af-*-*.*'
    glob_path = os.path.join(directory, mask)
    files = glob.glob(glob_path)
    files.sort()

    pid_count = {}

    for file_name in files:
        try:
            pid = int(file_name.split('-')[1])
        except (IndexError, ValueError):
            continue

        if pid in pid_count:
            pid_count[pid] += 1
        else:
            pid_count[pid] = 1

    max_count = 0
    max_pid = None

    for pid, count in pid_count.iteritems():
        if count > max_count:
            max_pid = pid
            max_count = count

    if max_pid is None:
        msg = 'Failed to automatically retrieve the main PID, valid PIDs are: %s'
        logging.warning(msg % ', '.join(pid_count.keys()))
        sys.exit(-1)
    else:
        logging.info('Analyzing PID %s' % max_pid)
        logging.info('')

    return str(max_pid)


def plugin_speed_cmd(p1, p2):
    return cmp(p1.SPEED, p2.SPEED)


def filter_enabled_plugins(args):
    plugins = []

    for i, klass in enumerate(PLUGINS):
        if args.__dict__[str(i)]:
            logging.debug('Enabling %s' % klass.__name__)
            plugins.append(klass)

    if not plugins:
        plugins.extend(PLUGINS)

    return plugins


def parse_args():
    """
    return: A tuple with config_file, version.
    """
    parser = argparse.ArgumentParser(description='Analyze w3af performance data')
    parser.add_argument('directory', help='Input directory')
    parser.add_argument('pid', nargs='?', help='Process ID to analyze, if none'
                                               ' is specified the main process'
                                               ' will be used.')
    parser.add_argument('--debug', action='store_true',
                        help='Print debugging information')
    parser.add_argument('--clear-cache', action='store_true',
                        help='Clear analysis cache for specified path')

    for i, klass in enumerate(PLUGINS):
        parser.add_argument('-%s' % i, action='store_true',
                            help='Enable %s' % klass.__name__)

    args = parser.parse_args()
    return args