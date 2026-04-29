explicate_test_defs = """

class pyobj:
    def __init__(self, val, tag):
        self.val = val
        self.tag = tag

class big_pyobj(pyobj):
    def __init__(self):
        self.tag = 3
        self.type = ""
        self.l_len = 0
        self.d_len = 0
        self.l = []
        self.d = {}

def inject_int(i):
    return pyobj(i, 0)

def inject_bool(b):
    if b == 0:
        return pyobj(False, 1)
    else:
        return pyobj(True, 1)

def project_int(obj):
    if is_int(obj):
        return int(obj.val)
    print("Err: project_int(NON INTEGER)")
    exit(1)

def project_bool(obj):
    if is_bool(obj):
        return int(obj.val)
    print("Err : project_bool(NON BOOL)")
    exit(1)

def is_int(obj):
    return (obj.tag == 0)

def is_bool(obj):
    return (obj.tag == 1)
    
def is_big(obj):
    return (obj.tag == 3)

def is_true(obj):
    if is_int(obj):
        if int(project_int(obj) == 0):
            return 0
        else:
            return 1
    elif is_bool(obj):
        if int(project_bool(obj) == 0):
            return 0
        else:
            return 1

def add(big_pyobj_1, big_pyobj_2):
    if big_pyobj_1.type == "LIST":
        if big_pyobj_2.type == "LIST":
            new = big_pyobj()
            new.type = "LIST"
            new.l = big_pyobj_1.l + big_pyobj_2.l
            new.l_len = big_pyobj_1.l_len + big_pyobj_2.l_len
            return new

def obj_equal(py_obj1, py_obj2):
    if is_int(py_obj1):
        if is_int(py_obj2):
            return project_int(py_obj1) == project_int(py_obj2)
        elif is_bool(py_obj2):
            return project_int(py_obj1) == project_bool(py_obj2)
    elif is_bool(py_obj1):
        if is_int(py_obj2):
            return project_bool(py_obj1) == project_int(py_obj2)
        elif is_bool(py_obj2):
            return project_bool(py_obj1) == project_bool(py_obj2)
    elif is_big(py_obj1):
        if is_big(py_obj2):
            return equal(py_obj1, py_obj2)
            

def equal(big_pyobj_1, big_pyobj_2):
    if big_pyobj_1.type == "LIST":
        if big_pyobj_2.type == "LIST":
            if big_pyobj_1.l_len != big_pyobj_2.l_len:
                return 0
            for i in range(big_pyobj_1.l_len):
                if not obj_equal(big_pyobj_1.l[i], big_pyobj_2.l[i]):
                    return 0
            return 1

def not_equal(big_pyobj_1, big_pyobj_2):
    return 1 - equal(big_pyobj_1, big_pyobj_2)

def print_lst(lst, level):
    print("[", end="")
    for i in range(len(lst)):
        print_any(lst[i], level + 1) 
        if i < len(lst) - 1:
            print(", ", end="")
    print("]", end="")

def print_any(obj, level=0):
    if isinstance(obj, big_pyobj):
        if obj.type == "LIST":
            print_lst(obj.l, level)
            if level == 0:
                print()
    elif isinstance(obj, pyobj):
        if level == 0:
            print(obj.val)
        else:
            print(obj.val, end="")
    else:
        if level == 0:
            print(obj.val)
        else:
            print(obj, end="")

def eval_input_pyobj():
    x = eval(input())
    if isinstance(x, int):
        return pyobj(x, 0)
    if isinstance(x, bool):
        return pyobj(x, 1)

def create_list(length):
    list_len = project_int(length)
    obj = big_pyobj()
    obj.type = "LIST"
    obj.l_len = list_len
    obj.l = [0] * list_len
    return obj

def set_subscript(c, key, pyobj_o):
    if isinstance(c, big_pyobj):
        k = project_int(key)
        if k >= 0 and k < c.l_len:
            c.l[k] = pyobj_o
        else:
            print("Err index out of range bro (set_subscript)")
    else:
        print("Err expecting big_pyobj in set_subscript")
        exit(1)

def get_subscript(c, key):
    if isinstance(c, big_pyobj):
        k = project_int(key)
        if k >= 0 and k < c.l_len:
            return c.l[k]
        else:
            print("Err index out of range bro (get_subscript)")
    else:
        print("Err expecting big_pyobj in get_subscript")
        exit(1)
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
        if project_bool(obj) == 0:
            return inject_bool(1)
        else:
            return inject_bool(0)
def box_unary_sub(obj):
    if is_int(obj):
        return inject_int(-project_int(obj))
    elif is_bool(obj):
        return inject_int(-project_bool(obj))
def box_int(obj):
    if is_int(obj):
        return inject_int(project_int(obj))
    elif is_bool(obj):
        return inject_int(project_bool(obj))
"""

