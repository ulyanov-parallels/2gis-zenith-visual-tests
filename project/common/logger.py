# coding: utf_8


global logs
logs = []


def log(s):
    msg = str(s)
    print(u''.join(msg))
    logs.append(msg)


def log_new(s):
    msg = u''.join(('\n', str(s)))
    print(msg)
    logs.append(msg)


def logg(s1, s2):
    msg = ': '.join((str(s1), str(s2)))
    print(u''.join(msg))
    logs.append(msg)


# new logging prototype
def logging(func):
    def wrapper(*args, **kwargs):
        log_new(func.__name__)
        log(args)
        res = func(*args, **kwargs)
        return res
    return wrapper
