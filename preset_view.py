import bpy
from .utils import *
from .preset_model import *
from .preset_control import *


@register_class
class BatchAssign_OP_PresetControlLoadFile(bpy.types.Operator):
    bl_idname = "batch_assign.preset_control_load_file"
    bl_label = "Load File"

    file : StringProperty(
        name = "Preset File",
        default = "batch_assign_preset.txt",
    )

    def execute(self, context):
        BatchAssign_PresetControl.get().load_file(self.file)
        return {"FINISHED"}


@register_class
class BatchAssign_OP_PresetControlWriteERNAS(bpy.types.Operator):
    bl_idname = "batch_assign.preset_control_write_ernas"
    bl_label = "Write ERNAS"
    bl_description = "Write ERNAS To Preset File With Preset Key"

    file : StringProperty(
        name = "Preset File",
        default = "batch_assign_preset.txt",
    )

    def execute(self, context):
        BatchAssign_PresetControl.get().write_ernas(self.file)
        return {"FINISHED"}


@register_class
class BatchAssign_MT_PresetFileMenu(bpy.types.Menu):
    bl_idname = "BatchAssign_MT_PresetLoadMenu"
    bl_label = "Select Preset File"

    def draw(self, context):
        control = BatchAssign_PresetControl.get()

        for text in bpy.data.texts:
            file = text.name
            self.layout.operator(
                BatchAssign_OP_PresetControlLoadFile.bl_idname,
                text = file
            ).file = file


@register_class
class BatchAssign_OP_PresetControlLoadKey(bpy.types.Operator):
    bl_idname = "batch_assign.preset_control_load_key"
    bl_label = "Load Key"

    key : StringProperty(
        name = "Preset Key",
        default = "",
    )

    def execute(self, context):
        BatchAssign_PresetControl.get().load_key(self.key)
        return {"FINISHED"}


@register_class
class BatchAssign_MT_PresetKeyMenu(bpy.types.Menu):
    bl_idname = "BatchAssign_MT_PresetKeyMenu"
    bl_label = "Select Key"

    def draw(self, context):
        control = BatchAssign_PresetControl.get()
        
        for key in control.preset.datas.keys():
            self.layout.operator(
                BatchAssign_OP_PresetControlLoadKey.bl_idname,
                text = key
            ).key = key


@register_class
class BatchAssign_PT_PresetPanel(bpy.types.Panel):
    bl_idname = "BatchAssign_PT_PresetPanel"
    bl_label = "Batch Assign Preset"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Misc"

    def draw_error(self, layout, error) -> bool:
        if len(error) > 0:
            layout.label(text = error, icon = "ERROR")
            return True
        else:
            return False

    def draw(self, context):
        model = BatchAssign_PresetModel.get()
        control = BatchAssign_PresetControl.get()

        layout = self.layout.column(align = True)

        loaded = control.preset_file_loaded
        layout.menu(
            BatchAssign_MT_PresetFileMenu.bl_idname,
            text = "Select Preset File" if loaded is None else loaded,
        )

        error = model.preset_error
        if self.draw_error(layout, error): return
        if control.preset_file_loaded is None: return
        
        loaded = control.preset_key_loaded
        layout.menu(
            BatchAssign_MT_PresetKeyMenu.bl_idname,
            text = "Select Preset Key" if loaded is None else loaded,
        )

        layout.operator(
            BatchAssign_OP_PresetControlWriteERNAS.bl_idname,
        ).file = control.preset_file_loaded
        
        
