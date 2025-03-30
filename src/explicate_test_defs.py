explicate_test_defs = """
class pyobj:
    def __init__(self, val, tag):
        self.val = val
        self.tag = tag

def inject_int(i):
    return pyobj(i, 0)

def inject_bool(b):
    if b == 0:
        return pyobj(False, 1)
    else:
        return pyobj(True, 1)

def project_int(obj):
    return int(obj.val)

def project_bool(obj):
    return int(obj.val)

def is_int(obj):
    return (obj.tag == 0)

def is_bool(obj):
    return (obj.tag == 1)

def is_true(obj):
    if is_int(obj):
        return project_int(obj) == 1
    elif is_bool(obj):
        return project_bool(obj) == 1

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
    if is_int(obj_1):
        if is_int(obj_2):
            return inject_int(project_int(obj_1) + project_int(obj_2))
        elif is_bool(obj_2):
            return inject_int(project_int(obj_1) + project_int(obj_2))
    elif is_bool(obj_1):
        if is_int(obj_2):
            return inject_int(project_int(obj_1) + project_int(obj_2))
        elif is_bool(obj_2):
            return inject_int(project_int(obj_1) + project_int(obj_2))   
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
def box_not(obj):
    if is_int(obj):
        if project_int(obj) == 0:
            return inject_bool(1)
        else:
            return inject_bool(0)
    elif is_bool(obj):
        if project_bool(obj) == 1:
            return inject_bool(1)
        else:
            return inject_bool(0)
def box_unary_sub(obj):
    if is_int(obj):
        return inject_int(-project_int(obj))
    elif is_bool(obj):
        return inject_int(-project_bool(obj))
"""

