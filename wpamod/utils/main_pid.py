import os
import sys
import glob
import logging


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
            pid = int(file_name.split('w3af-')[1].split('-')[0])
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
        logging.info('Analyzing PID %s of %s' % (max_pid, directory))
        logging.info('')

    return str(max_pid)
