import os
import glob
import logging


def is_valid_pid(directory, query_pid):
    directory = os.path.expanduser(directory)
    glob_path = os.path.join(directory, 'w3af-*')
    files = glob.glob(glob_path)
    files.sort()

    all_pids = set()

    for path_file in files:
        path, file_name = os.path.split(path_file)
        try:
            current_pid = int(file_name.split('-')[1])
        except IndexError:
            continue
        except ValueError:
            continue
        else:
            all_pids.add(current_pid)

    all_pids = list(all_pids)
    all_pids.sort()
    all_pids = [str(i) for i in all_pids]

    if query_pid in all_pids:
        return True
    else:
        msg = 'Invalid PID %s specified, valid PIDs are: %s'
        args = (query_pid, ' '.join(all_pids))
        logging.warning(msg % args)
        return False
