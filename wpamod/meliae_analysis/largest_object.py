DEFAULT_TYPES_IGNORE = ('frame', 'module')


def largest_object(meliae_memory, top=20, ignore_types=DEFAULT_TYPES_IGNORE):
    """
    This function returns a list of the top N objects which reference more
    memory. Meliae provides great features which output something like:

        Strings     use 30% of your memory
        FooObjects  use 60% of your memory

    but lacks a feature to tell you that there is a list which is referencing
    all your strings which are hold in memory. (and it would be amazing if it
    could tell you the variable name for that list, but that's a different
    story).

    :param meliae_memory: ObjManager instance from Meliae
    :return: A summary with the largest objects in memory (including it's
             childs) that's easy to read.
    """
    meliae_memory.compute_parents()
    all_objs = []

    for obj in meliae_memory.objs.itervalues():

        # I don't care if a frame references a big variable, that's fine, frames
        # are not persistent
        if obj.type_str in ignore_types:
            continue

        meliae_memory.compute_total_size(obj)
        all_objs.append(obj)

    all_objs.sort(size_sort)
    all_objs.reverse()

    interesting_objs = all_objs[:top]

    return [ObjSummary(io) for io in interesting_objs]


class ObjSummary(object):
    """
    Wrapper around meliae object in order to get some summarized data.

    Note that some loops are not very pythonic, this is because of issues like
    this one:

    File "/home/pablo/pch/w3af-performance-analysis/wpamod/meliae_analysis/
    largest_object.py", line 72, in get_child_len
        return len(self.meliae_obj.c)

    File "meliae/_loader.pyx", line 513, in meliae._loader._MemObjectProxy.c.
    __get__ (meliae/_loader.c:5170)

    File "meliae/_loader.pyx", line 778, in meliae._loader.MemObjectCollection.
    __getitem__ (meliae/_loader.c:8364)
        KeyError: 'address 140617317982568 not present'
    """
    def __init__(self, meliae_obj):
        self.meliae_obj = meliae_obj

    def get_type(self):
        return self.meliae_obj.type_str

    def get_total_size(self):
        return self.meliae_obj.total_size

    def get_child_types(self):
        child_type_set = set()

        for i in xrange(10):
            try:
                child = self.meliae_obj.c[i]
            except:
                pass
            else:
                child_type_set.add(child.type_str)

        return list(child_type_set)

    def get_child_values(self):
        child_values_set = set()

        for i in xrange(10):
            try:
                child = self.meliae_obj.c[i]
            except:
                pass
            else:
                child_values_set.add(child.value)

        return list(child_values_set)

    def get_child_len(self):
        return len(self.meliae_obj.ref_list)

    def __repr__(self):
        fmt = '<%s object with %s child objects of types %r with values %r>'
        args = (self.get_type(), self.get_child_len(), self.get_child_types(),
                self.get_child_values())
        return fmt % args


def size_sort(obj_1, obj_2):
    return cmp(obj_1.total_size, obj_2.total_size)