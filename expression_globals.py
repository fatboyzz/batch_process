import re
import mathutils
import bpy

Collection_Initial = [bpy]

Expression_Globals = {
    "__builtins__" : __builtins__,
    
    "re" : re,

    "mathutils" : mathutils,
}
