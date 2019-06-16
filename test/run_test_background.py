import sys
import os
from os import path
import subprocess

FILE_DIR = path.dirname(__file__)
BLENDER_EXE = path.normpath(path.join(FILE_DIR, "../../../../../blender.exe"))

subprocess.run([
    BLENDER_EXE, 
    "--factory-startup", 
    "--background", 
    path.join(FILE_DIR, "test.blend"),
    "--addons", "batch_process",
    "--python-text", "run_test.py", 
])
