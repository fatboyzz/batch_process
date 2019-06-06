import re
import mathutils
import bpy

Expression_Globals = {
    "__builtins__" : __builtins__,
    
    "re" : re,

    "bpy": bpy,
    "mathutils" : mathutils,
}
