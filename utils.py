import sys
import traceback
import bpy


register_classes = []


def register():
    for cls in register_classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(register_classes):
        bpy.utils.unregister_class(cls)
        

def register_class(cls):
    """Decorator for blender register class"""
    register_classes.append(cls)
    return cls


def singleton(cls):
    """Decorator for singleton class"""
    cls.__singleton__ = None

    def get():
        if cls.__singleton__ == None:
            cls.__singleton__ = cls()
        return cls.__singleton__
        
    cls.get = get
    return cls


def model(prop):
    """Decorator for blender scene property class"""
    def decorator(cls):

        def register():
            S, P = bpy.types.Scene, bpy.props.PointerProperty
            setattr(S, prop, P(type=cls))

        def unregister():
            delattr(bpy.types.Scene, prop)
            
        def get():
            return getattr(bpy.context.scene, prop)
        
        cls.register = register
        cls.unregister = unregister
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
