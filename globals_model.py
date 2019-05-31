import re
import mathutils
import bpy

class Collection_Initial:
    bpy = bpy

Expression_Globals = {
    "__builtins__" : __builtins__,
    
    "re" : re,

    "mathutils" : mathutils,
}
