import logging

from functools32 import lru_cache
from meliae import loader


@lru_cache(maxsize=20)
def load_meliae(filename):
    try:
        om = loader.load(filename)
    except KeyError, ke:
        logging.error('Failed to load meliae file')
        return

    try:
        om.collapse_instance_dicts()
    except Exception, e:
        # Sometimes this collapse_instance_dicts fails with:
        #   KeyError: 'address 140088038122672 not present'
        #
        # But it's ok, we can still run summarize
        logging.debug('Failed to collapse_instance_dicts: "%s"' % e)

    om.remove_expensive_references()

    return om