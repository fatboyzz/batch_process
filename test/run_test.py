import sys
from os import path
import unittest
import batch_process
import bpy

BATCH_PROCESS_DIR = path.dirname(batch_process.__file__)
BATCH_PROCESS_TEST_DIR = path.join(BATCH_PROCESS_DIR, "test")

if __name__ == "__main__":
    pattern = "test*.py"
    suits = unittest.defaultTestLoader.discover(BATCH_PROCESS_TEST_DIR, pattern=pattern)
    unittest.TextTestRunner().run(suits)
    bpy.ops.wm.revert_mainfile()
