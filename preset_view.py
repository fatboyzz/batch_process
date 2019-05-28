import bpy
from .utils import *
from .preset_control import *

register_classes = []


@append(register_classes)
class BatchAssign_PresetControlLoadPresets(bpy.types.Operator):
    bl_idname = "batch_assign.preset_control_load_presets"
    bl_label = "Update Collection"
    bl_description = "Batch Assign Value"

    filename : StringProperty(
        name = "Preset Load Filename",
        default = "",
    )

    def execute(self, context):
        BatchAssign_PresetControl.get().load_presets(self.filename)


@append(register_classes)
class BatchAssign_PresetControlSavePresets(bpy.types.Operator):
    bl_idname = "batch_assign.preset_control_save_presets"
    bl_label = "Update Collection"
    bl_description = "Batch Assign Value"

    def execute(self, context):
        BatchAssign_PresetControl.get().save_presets()


@append(register_classes)
class BatchAssign_MT_PresetLoadMenu(bpy.types.Menu):
    bl_idname = "BatchAssign_MT_PresetLoadMenu"
    bl_label = "Batch Assign Preset Load"

    def draw(self, context):
        layout = self.layout

        for i in range(3):
            layout.label(text = "abc" + str(i))


@append(register_classes)
class BatchAssign_PT_PresetPanel(bpy.types.Panel):
    bl_idname = "BatchAssign_PT_PresetPanel"
    bl_label = "Batch Assign Preset"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Misc"

    def draw(self, context):
        layout = self.layout.column()

        layout.menu(BatchAssign_MT_PresetLoadMenu.bl_idname)
        