import logging
import argparse
import sys
import os

from jinja2 import Template

from wpamod.utils.main_pid import get_main_pid
from wpamod.utils.log import configure_logging
from wpamod.utils.cache import save_cache, clear_cache, get_from_cache

from wpamod.plugins.meliae_basic import MeliaeBasic
from wpamod.plugins.meliae_largest import MeliaeLargestObject
from wpamod.plugins.meliae_usage_summary import MeliaeUsageSummary
from wpamod.plugins.sys_info import SystemInformation
from wpamod.plugins.cpu_usage import CPUUsageByFunction
from wpamod.plugins.psutil_summary import PSUtilSummary
from wpamod.plugins.core_status import CoreStatus
from wpamod.plugins.request_count import HTTPRequestCount
from wpamod.plugins.log_parser import LogParser

# Leave the plugins list in this format so it's easier to comment the plugins
# we don't need during development/testing
#
# We'll create an HTML report using all these plugins, note that this is
# different from `wpa` where the user can choose which plugins to run
PLUGINS = [
           MeliaeBasic,
           MeliaeUsageSummary,
           MeliaeLargestObject,
           CPUUsageByFunction,
           CoreStatus,
           PSUtilSummary,
           SystemInformation,
           HTTPRequestCount,
           LogParser
]


def main():
    args = parse_args()

    configure_logging(args.debug)
    logging.debug('Starting wpa-html')

    # Here we store the data to send to the HTML template
    render_context = {}

    for directory in args.directories:

        try:
            config_version = os.path.join(directory, 'config', 'version')
            revision = file(config_version).read().strip()
        except IOError:
            msg = '%s is not a valid collector output directory'
            logging.error(msg % directory)
            sys.exit(-1)

        pargs = (directory, revision)
        logging.debug('Starting wpa-html analysis of %s (%s)' % pargs)

        if args.clear_cache:
            clear_cache(directory)

        #
        # Set unique revision id
        #
        i = -1

        while True:
            i += 1
            unique_revision = '%s-%s' % (revision, i)
            if unique_revision not in render_context:
                render_context[unique_revision] = {}
                break

        render_context[unique_revision]['directory'] = directory

        # Choose which PID to analyze
        pid = get_main_pid(directory)

        for plugin_klass in PLUGINS:
            plugin_inst = plugin_klass(directory, pid)
            name = plugin_inst.get_output_name()

            data = get_from_cache(directory, pid, name)

            if data is None:
                data = plugin_inst.analyze()
                save_cache(directory, pid, name, data)

            render_context[unique_revision][plugin_inst] = data

    # Render the HTML file using the context
    template = Template(file('wpamod/html_report/templates/report.html').read())
    rendered_template = template.render(render_context)
    file(args.output_file, 'w').write(rendered_template)


def parse_args():
    """
    return: A tuple with config_file, version.
    """
    parser = argparse.ArgumentParser(description='Analyze w3af performance'
                                                 ' data and generate HTML')
    parser.add_argument('directories', help='Input directories', nargs='+')
    parser.add_argument('--output-file', help='Output HTML file', required=True)
    parser.add_argument('--debug', action='store_true',
                        help='Print debugging information')
    parser.add_argument('--clear-cache', action='store_true',
                        help='Clear analysis cache for specified path')

    args = parser.parse_args()
    return args

