explicate_test_defs = """
class pyobj:
    def __init__(self, val):
        self.val = val

def inject_int(i):
    return pyobj(i)

def inject_bool(b):
    return pyobj(b)

def project_int(obj):
    return int(obj.val)

def project_bool(obj):
    return int(obj.val)

def is_int(obj):
    return isinstance(obj.val, int)

def is_bool(obj):
    return isinstance(obj.val, bool)

def print_any(obj):
    if isinstance(obj, pyobj):
        print(obj.val)
    else:
        print(obj)
def eval_input_pyobj():
    x = eval(input())
    if isinstance(x, int):
        return pyobj(x)
    if isinstance(x, bool):
        return pyobj(x)
"""

explicate_abbreviated_test_defs = """
def box_add(obj_1, obj_2):    
    if isinstance(obj_1, pyobj):
        int_1 = int(obj_1.val)
        if isinstance(obj_2, pyobj):
            int_2 = int(obj_2.val)
        else:
            int_2 = int(obj_2)
    else:
        int_1 = int(obj_1)
        if isinstance(obj_2, pyobj):
            int_2 = int(obj_2.val)
        else:
            int_2 = int(obj_2)
    return inject_int(int_1 + int_2)
def box_is(obj_1, obj_2):
    if is_int(obj_1):
        if is_int(obj_2):
            if project_int(obj_1) == project_int(obj_2):
                return inject_bool(1)
            else:
                return inject_bool(0)
        elif is_bool(obj_2):
            return inject_bool(0)
    elif is_bool(obj_1):
        if is_int(obj_2):
            return inject_bool(0)
        elif is_bool(obj_2):
            if project_bool(obj_1) == project_bool(obj_2):
                return inject_bool(1)
            else:
                return inject_bool(0)
def box_equal(obj_1, obj_2):
    if is_int(obj_1):
        if is_int(obj_2):
            if project_int(obj_1) == project_int(obj_2):
                return inject_bool(1)
            else:
                return inject_bool(0)
        elif is_bool(obj_2):
            if project_int(obj_1) == project_int(obj_2):
                return inject_bool(1)
            else:
                return inject_bool(0)
    elif is_bool(obj_1):
        if is_int(obj_2):
            if project_int(obj_1) == project_int(obj_2):
                return inject_bool(1)
            else:
                return inject_bool(0)
        elif is_bool(obj_2):
            if project_int(obj_1) == project_int(obj_2):
                return inject_bool(1)
            else:
                return inject_bool(0)
def box_nequal(obj_1, obj_2):
    if is_int(obj_1):
        if is_int(obj_2):
            if project_int(obj_1) != project_int(obj_2):
                return inject_bool(1)
            else:
                return inject_bool(0)
        elif is_bool(obj_2):
            if project_int(obj_1) != project_int(obj_2):
                return inject_bool(1)
            else:
                return inject_bool(0)
    elif is_bool(obj_1):
        if is_int(obj_2):
            if project_int(obj_1) != project_int(obj_2):
                return inject_bool(1)
            else:
                return inject_bool(0)
        elif is_bool(obj_2):
            if project_int(obj_1) != project_int(obj_2):
                return inject_bool(1)
            else:
                return inject_bool(0)
"""

