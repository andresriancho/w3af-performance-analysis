import logging
import argparse

from wpamod.utils.show_results import show_result
from wpamod.plugins.meliae_basic import MeliaeBasic
from wpamod.plugins.meliae_usage_summary import MeliaeUsageSummary
from wpamod.plugins.sys_info import SystemInformation
from wpamod.utils.log import configure_logging

PLUGINS = {MeliaeBasic, MeliaeUsageSummary, SystemInformation}


def main():
    args = parse_args()

    configure_logging(args.debug)
    logging.debug('Starting performance analysis')

    output = []

    for plugin_klass in PLUGINS:
        plugin_inst = plugin_klass(args.idirectory)
        new_output = plugin_inst.analyze()
        name = plugin_inst.get_output_name()
        output.append((name, new_output))

    show_result('Performance analysis', tuple(output))


def parse_args():
    """
    return: A tuple with config_file, version.
    """
    parser = argparse.ArgumentParser(description='Analyze performance statistics')
    parser.add_argument('idirectory', help='Input directory')
    parser.add_argument('--debug', action='store_true', help='Print debugging information')
    args = parser.parse_args()
    return args