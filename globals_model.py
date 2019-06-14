import os
import re
import mathutils
import bpy

Expression_Globals = {
    "__builtins__" : __builtins__,
    
    "os" : os,
    "re" : re,

    "bpy": bpy,
    "mathutils" : mathutils,
}
