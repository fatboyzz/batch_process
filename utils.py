import sys
import traceback
import importlib
import bpy

def register_module(mod):
    if not hasattr(mod, "register_classes"):
        return

    for cls in mod.register_classes:
        if issubclass(cls, bpy.types.bpy_struct):
            bpy.utils.register_class(cls)
        elif hasattr(cls, "register_module"):
            cls.register_module()


def unregister_module(mod):
    if not hasattr(mod, "register_classes"):
        return

    for cls in reversed(mod.register_classes):
        if issubclass(cls, bpy.types.bpy_struct):
            bpy.utils.unregister_class(cls)
        elif hasattr(cls, "unregister_module"):
            cls.unregister_module()


def append(seq):
    def decorator(cls):
        seq.append(cls)
        return cls
    return decorator


def counter(n):
    def count():
        nonlocal n
        c = n
        n += 1
        return c
    return count


def get_clipboard():
    return bpy.context.window_manager.clipboard

def set_clipboard(s):
    bpy.context.window_manager.clipboard = s

def print_traceback_and_set_clipboard(self):
    etype, value, tb = sys.exc_info()
    if tb == None: return
        
    traceback.print_exception(etype, value, tb)

    tb_extracted = traceback.extract_tb(tb)
    if len(tb_extracted) > 0:
        file, line, _, _ = tb_extracted[-1]
        set_clipboard("{0}:{1}".format(file, line))
