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

    if not is_valid_pid(args.directory, args.pid):
        sys.exit(-1)

    enabled_plugins = filter_enabled_plugins(args)

    for plugin_klass in sorted(enabled_plugins, plugin_speed_cmd):
        plugin_inst = plugin_klass(args.directory, args.pid)
        name = plugin_inst.get_output_name()

        data = get_from_cache(args.directory, args.pid, name)

        if data is None:
            data = plugin_inst.analyze()
            save_cache(args.directory, args.pid, name, data)

        if data:
            show_result(name, data)
        else:
            logging.debug('No data for %s' % name)


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
    parser.add_argument('pid', help='Input directory')
    parser.add_argument('--debug', action='store_true',
                        help='Print debugging information')
    parser.add_argument('--clear-cache', action='store_true',
                        help='Clear analysis cache for specified path')

    for i, klass in enumerate(PLUGINS):
        parser.add_argument('-%s' % i, action='store_true',
                            help='Enable %s' % klass.__name__)

    args = parser.parse_args()
    return args