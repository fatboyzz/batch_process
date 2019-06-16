import unittest
import bpy

class TestExample(unittest.TestCase):
    def setUp(self):
        self.bp = bpy.ops.batch_process
        self.bp.preset_control_load_file(file = "EXAMPLES.txt")
    
    def set_scene(self, name):
        bpy.context.window.scene = bpy.data.scenes[name]

    def run_erna_of_key(self, key):
        self.bp.preset_control_load_key(key = key)
        self.bp.main_control_update()
        self.bp.main_control_assign()

    def test_Rename_Objects_Sort_By_X(self):
        self.set_scene("test_Rename_Objects_Sort_By_X")

        A, B, C = (bpy.data.objects[name] for name in ["A", "B", "C"])
        
        self.run_erna_of_key("Rename_Objects_Sort_By_X")
        
        self.assertEqual(A.name, "obj_002")
        self.assertEqual(B.name, "obj_001")
        self.assertEqual(C.name, "obj_000")

    def test_Rename_Bones(self):
        self.set_scene("test_Rename_Bones")

        Armature = bpy.data.objects["Armature"]
        BONES = Armature.data.bones
        PELVIS = BONES["pelvis"]
        LEFT = BONES["leg left thigh"]
        RIGHT = BONES["leg right thigh"]

        self.run_erna_of_key("Rename_Bones_Append_LR")

        self.assertEqual(PELVIS.name, "pelvis")
        self.assertEqual(LEFT.name, "leg___thigh.L")
        self.assertEqual(RIGHT.name, "leg___thigh.R")

        self.run_erna_of_key("Rename_Bones_Trim_LR")

        self.assertEqual(PELVIS.name, "pelvis")
        self.assertEqual(LEFT.name, "leg left thigh")
        self.assertEqual(RIGHT.name, "leg right thigh")

    def test_Rename_Materials_With_Object_Name(self):
        self.set_scene("test_Rename_Materials_With_Object_Name")

        CUBE = bpy.data.objects["CUBE"]
        M00, M01, M02 = (slot.material for slot in CUBE.material_slots)
        
        self.run_erna_of_key("Rename_Materials_With_Object_Name")

        self.assertEqual(M00.name, "CUBE_00")
        self.assertEqual(M01.name, "CUBE_01")
        self.assertEqual(M02.name, "CUBE_02")

