import bpy
from .utils import *
from .preset_model import *
from .preset_control import *


@register_class
class BATCH_PROCESS_OP_PresetControlLoadFile(bpy.types.Operator):
    bl_idname = "batch_process.preset_control_load_file"
    bl_label = "Load File"

    file : StringProperty(
        name = "Preset File",
        default = "batch_process_preset.txt",
    )

    def execute(self, context):
        BATCH_PROCESS_PresetControl.get().load_file(self.file)
        return {"FINISHED"}


@register_class
class BATCH_PROCESS_OP_PresetControlWriteERNAS(bpy.types.Operator):
    bl_idname = "batch_process.preset_control_write_ernas"
    bl_label = "Write ERNAS"
    bl_description = "Write ERNAS To Preset File"

    file : StringProperty(
        name = "Preset File",
        default = "batch_process_preset.txt",
    )

    def execute(self, context):
        BATCH_PROCESS_PresetControl.get().write_ernas(self.file)
        return {"FINISHED"}


@register_class
class BATCH_PROCESS_MT_PresetFileMenu(bpy.types.Menu):
    bl_idname = "BATCH_PROCESS_MT_PresetLoadMenu"
    bl_label = "Select Preset File"

    def draw(self, context):
        for text in bpy.data.texts:
            file = text.name
            self.layout.operator(
                BATCH_PROCESS_OP_PresetControlLoadFile.bl_idname,
                text = file
            ).file = file


@register_class
class BATCH_PROCESS_OP_PresetControlLoadKey(bpy.types.Operator):
    bl_idname = "batch_process.preset_control_load_key"
    bl_label = "Load Key"

    key : StringProperty(
        name = "Preset Key",
        default = "",
    )

    def execute(self, context):
        BATCH_PROCESS_PresetControl.get().load_key(self.key)
        return {"FINISHED"}


@register_class
class BATCH_PROCESS_MT_PresetKeyMenu(bpy.types.Menu):
    bl_idname = "BATCH_PROCESS_MT_PresetKeyMenu"
    bl_label = "Select Key"

    def draw(self, context):
        control = BATCH_PROCESS_PresetControl.get()
        
        for key in control.preset.datas.keys():
            self.layout.operator(
                BATCH_PROCESS_OP_PresetControlLoadKey.bl_idname,
                text = key
            ).key = key


@register_class
class BATCH_PROCESS_PT_PresetPanel(bpy.types.Panel):
    bl_idname = "BATCH_PROCESS_PT_PresetPanel"
    bl_label = "Batch Process Preset"
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
        model = BATCH_PROCESS_PresetModel.get()
        control = BATCH_PROCESS_PresetControl.get()

        layout = self.layout.column(align = True)
        layout_row = layout.row(align = True)

        loaded = control.preset_file_loaded

        layout_row.menu(
            BATCH_PROCESS_MT_PresetFileMenu.bl_idname,
            text = "Select Preset File" if loaded is None else loaded,
        )

        error = model.preset_error
        if self.draw_error(layout, error): return
        if control.preset_file_loaded is None: return

        layout_row.operator(
            BATCH_PROCESS_OP_PresetControlWriteERNAS.bl_idname,
            text = "",
            icon = "COPYDOWN",
        ).file = control.preset_file_loaded
        
        loaded = control.preset_key_loaded
        layout.menu(
            BATCH_PROCESS_MT_PresetKeyMenu.bl_idname,
            text = "Select Preset Key" if loaded is None else loaded,
        )
