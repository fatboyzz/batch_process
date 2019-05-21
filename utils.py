import bpy
import importlib


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

