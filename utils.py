import sys
import traceback
import bpy

def register_module(mod):
    if not hasattr(mod, "register_classes"): return

    for cls in mod.register_classes:
        if issubclass(cls, bpy.types.bpy_struct):
            bpy.utils.register_class(cls)

        if hasattr(cls, "register_module"):
            cls.register_module()


def unregister_module(mod):
    if not hasattr(mod, "register_classes"): return

    for cls in reversed(mod.register_classes):

        if hasattr(cls, "unregister_module"):
            cls.unregister_module()

        if issubclass(cls, bpy.types.bpy_struct):
            bpy.utils.unregister_class(cls)
        

def append(seq):
    def decorator(cls):
        seq.append(cls)
        return cls

    return decorator


def singleton(cls):
    cls.__singleton__ = None

    def get():
        if cls.__singleton__ == None:
            cls.__singleton__ = cls()
        return cls.__singleton__
        
    cls.get = get
    return cls


def model(prop):
    def decorator(cls):

        def register_module():
            S, P = bpy.types.Scene, bpy.props.PointerProperty
            setattr(S, prop, P(type=cls))

        def unregister_module():
            delattr(bpy.types.Scene, prop)
            
        def get():
            return getattr(bpy.context.scene, prop)
        
        cls.register_module = register_module
        cls.unregister_module = unregister_module
        cls.get = get
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


def print_traceback_and_set_clipboard():
    etype, value, tb = sys.exc_info()
    if tb == None: return
        
    traceback.print_exception(etype, value, tb)

    tb_extracted = traceback.extract_tb(tb)
    if len(tb_extracted) > 0:
        file, line, _, _ = tb_extracted[-1]
        set_clipboard("{0}:{1}".format(file, line))
