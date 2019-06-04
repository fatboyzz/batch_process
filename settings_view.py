import bpy
from .utils import *
from .settings_model import *

register_classes = []

@register_class
class BatchAssign_PT_Settings(bpy.types.Panel):
    bl_idname = "BatchAssign_PT_Settings"
    bl_label = "Batch Assign Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Misc"

    def draw(self, context):
        layout = self.layout.column(align = True)
        settings = BatchAssign_SettingsModel.get()
        annotation = settings.__annotations__
        
        for prop in annotation.keys():
            layout.prop(
                data = settings,
                property = prop,
            )

