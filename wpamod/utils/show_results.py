from __future__ import print_function

import types

from fabric.colors import green, blue, yellow, red

INDENT_LEN = 4
COLORS = {0: green,
          1: blue,
          2: yellow}


def show_result(title, result, level=0):
    """
    Shows the result in the console using nice colors.
    
    :param result: A multi-level tuple. Example:
                    ('EC2 instance i123456', (('AMI', 'ami-7756...'),
                                              ('Status', 'available'),
                                              ('Foo', 'bar')))
    """
    if not level:
        print(green(title))
        print(green('=' * len(title)))
        print()
        
    if not result:
        _make_printable('No results to show.', level)
        print()
        return

    for item in result:
        
        try:
            key, value = item
        except:
            raise TypeError('Expected tuple got %s' % item)
        
        if _should_recurse(value):
            print(_make_printable(key, level))
            show_result(title, value, level=level+1)
            print()
            
        elif isinstance(value, list):
            print(_make_printable(key, level))
            
            if value:
                for leaf_value in value:
                    print(_make_printable('- %s' % leaf_value, level+1))
            else:
                # Print none when there are no items in the list.
                print(_make_printable('None', level+1))
            
        elif isinstance(value, (basestring, long, int, float, types.NoneType)):
            print(_make_printable('%s: ' % key, level), end='')
            print(value)
            
        else:
            msg = 'Unknown type (%s) for "%s" as value for "%s"'
            raise TypeError(msg % (type(value), value, key))

            
def _should_recurse(values):
    try:
        for val in values:
            if not(isinstance(val, tuple) and len(val) == 2):
                return False
    except:
        return False
    
    return True
    
    
def _make_printable(data, level):
    color = COLORS.get(level, lambda x: x)
    colored_key = color(data)
    spaces = ' ' * level * INDENT_LEN

    if '\n' in colored_key:
        colored_key = colored_key.replace('\n', '\n%s' % spaces)
        to_print = '\n%s%s' % (spaces, colored_key)
    else:
        to_print = '%s%s' % (spaces, colored_key)

    return to_print