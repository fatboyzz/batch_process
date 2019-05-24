import os.path
import bpy
from .utils import *
from .control import Control

register_classes = []

@append(register_classes)
class BatchAssign_OP_ControlUpdate(bpy.types.Operator):
    bl_idname = "batch_assign.control_update"
    bl_label = "Update Collection"
    bl_description = "Update Collection"
    def execute(self, context):
        Control.update()
        return {'FINISHED'}

@append(register_classes)
class BatchAssign_OP_ControlBatchAssign(bpy.types.Operator):
    bl_idname = "batch_assign.control_batch_assign"
    bl_label = "Update Collection"
    bl_description = "Batch Assign Value"
    def execute(self, context):
        Control.batch_assign()
        return {'FINISHED'}

@append(register_classes)
class BatchAssign_PT_SettingsPanel(bpy.types.Panel):
    bl_idname = "BatchAssign_PT_SettingsPanel"
    bl_label = "Batch Assign Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Misc"

    def draw(self, context):
        layout = self.layout.column(align = True)
        settings = Control.settings()
        annotation = settings.__annotations__

        for prop, (_, infos) in annotation.items():
            layout.prop(
                data = settings,
                property = prop,
                text = infos["description"],
            )
        
@append(register_classes)
class BatchAssign_PT_MainPanel(bpy.types.Panel):
    bl_idname = "BatchAssign_PT_MainPanel"
    bl_label = "Batch Assign"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Misc"
    
    def draw_error(self, layout, err) -> bool:
        if len(err) > 0:
            layout.label(text = err, icon = "ERROR")
            return True
        else:
            return False

    def draw_error_indicator(self, layout, indicator) -> bool:
        props = Control.properties()

        if len(getattr(props, indicator)) > 0:
            layout.prop(
                data = props,
                property = indicator,
                text = "",
                icon = "ERROR",
            )
            return True
        else:
            return False

    def draw(self, context):
        self.context = context
        self.draw_update_button()

    def draw_update_button(self):
        layout = self.layout
        layout.operator_context = 'EXEC_DEFAULT'
        layout.operator(
            "batch_assign.control_update",
            text = "Update",
        )

        self.draw_erna()

    def draw_erna(self):
        layout = self.layout.box()
        layout.label(text = "Extended RNA Data Path:")

        layout_column = layout.column(align = True)
        props = Control.properties()        

        layout_column.prop(
            data = props,
            property = "erna",
            text = "",
            icon = "TEXT",
        )

        self.draw_error_indicator(layout_column, "erna_error_indicator")
        self.draw_error(layout, props.erna_error)

        self.draw_assign_expression()

    def draw_assign_expression(self):
        layout = self.layout.box()
        layout.label(text = "Assign Expression: ")

        layout_column = layout.column(align = True)
        props = Control.properties()

        layout_column.prop(
            data = props,
            property = "assign_exp",
            text = "",
            icon = "TEXT",
        )
    
        self.draw_error_indicator(layout_column, "assign_exp_error_indicator")
        self.draw_error(layout, props.assign_exp_error)

        self.draw_assign_button()

    def draw_assign_button(self):
        layout = self.layout
        layout.operator(
            "batch_assign.control_batch_assign",
            text = "Assign",
        )

        self.draw_errors()

    def draw_errors(self):
        layout = self.layout
        props = Control.properties()

        err = Control.check_selection()
        if self.draw_error(layout, err): return

        err = props.unexpected_error
        if self.draw_error(layout, err): return

        err = props.erna_error
        if len(err) > 0: return

        err = props.collection_error
        if self.draw_error(layout, err): return

        self.draw_collection()
        
    def draw_collection(self):
        collection = Control.collection
        if not issubclass(collection.property_type, bpy.types.bpy_struct): return

        layout = self.layout.box()
        layout.label(text = "Assign Preview: ")
        props = Control.properties()

        layout = layout.column(align = True)
        for index, data in enumerate(collection.datas):
            layout_row = layout.row()

            layout_row.prop(
                data = data,
                property = collection.property,
                text = "",
            )
            
            err = props.assign_exp_error
            if len(err) > 0: continue

            layout_row.label(
                text = str(collection.datas_assign[index])
            )
                

        self.draw_accessable_property()

    def draw_accessable_property(self):
        layout = self.layout.box()
        layout.label(text = "Accessable Property: ")

        layout = layout.column_flow(align = True, columns = 2)
        for prop in Control.collection.accessable_property():
            layout.label(text = prop)
