class pyobj:
    def __init__(self, val):
        self.val = val

def inject_int(i):
    return pyobj(i)

def inject_bool(b):
    return pyobj(b)

def project_int(obj):
    if isinstance(obj, pyobj):
        return int(obj.val)
    return int(obj)

def project_bool(obj):
    if isinstance(obj, pyobj):
        return int(obj.val)
    return bool(obj)

def is_int(obj):
    if isinstance(obj, pyobj):
        return isinstance(obj.val, int)
    return isinstance(obj, int)

def is_bool(obj):
    if isinstance(obj, pyobj):
        return isinstance(obj.val, bool)
    return isinstance(obj, bool)

def print_any(obj):
    if isinstance(obj, pyobj):
        print(obj.val)
    else:
        print(obj)