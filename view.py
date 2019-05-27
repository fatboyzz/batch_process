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
class BatchAssign_PT_Settings(bpy.types.Panel):
    bl_idname = "BatchAssign_PT_Settings"
    bl_label = "Batch Assign Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Misc"

    def draw(self, context):
        layout = self.layout.column(align = True)
        settings = Control.settings()
        annotation = settings.__annotations__
        
        for prop in annotation.keys():
            layout.prop(
                data = settings,
                property = prop,
            )

# @append(register_classes)
# class BatchAssign_ERNA_Preset(bpy.types.Panel):
#     bl_idname = "BatchAssign_PT_Preset"
#     bl_label = "Batch Assign Preset"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "Misc"
    
@append(register_classes)
class BatchAssign_PT_MainPanel(bpy.types.Panel):
    bl_idname = "BatchAssign_PT_MainPanel"
    bl_label = "Batch Assign"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Misc"
    
    def draw_error(self, layout, error) -> bool:
        if len(error) > 0:
            layout.label(text = error, icon = "ERROR")
            return True
        else:
            return False

    def draw_error_indicator(self, layout, indicator) -> bool:
        errors = Control.errors()

        if len(getattr(errors, indicator)) > 0:
            layout.prop(
                data = errors,
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
        layout.label(text = "ERNA Data Path:")

        layout_column = layout.column(align = True)
        props = Control.properties()        
        errors = Control.errors()

        layout_column.prop(
            data = props,
            property = "erna",
            text = "",
            icon = "TEXT",
        )

        self.draw_error_indicator(layout_column, "erna_error_indicator")
        self.draw_error(layout, errors.erna_error)

        self.draw_assign_expr()

    def draw_assign_expr(self):
        layout = self.layout.box()
        layout.label(text = "Assign Expression: ")

        layout_column = layout.column(align = True)
        props = Control.properties()
        errors = Control.errors()

        layout_column.prop(
            data = props,
            property = "assign_expr",
            text = "",
            icon = "TEXT",
        )
    
        self.draw_error_indicator(layout_column, "assign_expr_error_indicator")
        self.draw_error(layout, errors.assign_expr_error)

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
        errors = Control.errors()

        error = errors.unexpected_error
        if self.draw_error(layout, error): return

        error = errors.selection_error
        if self.draw_error(layout, error): return

        error = errors.erna_error
        if len(error) > 0: return

        error = errors.collection_error
        if self.draw_error(layout, error): return

        self.draw_collection()
        
    def draw_collection(self):
        collection = Control.collection
        if collection is None: return

        layout = self.layout.box()
        layout.label(text = "Assign Preview: ")

        layout = layout.column(align = True)
        for index, context in enumerate(collection.contexts):
            data = context.data
            layout_row = layout.row(align = True)

            if issubclass(collection.data_type, bpy.types.bpy_struct): 
                layout_row.prop(
                    data = data,
                    property = collection.property,
                    text = "",
                )
            else:
                layout_row.label(
                    text = str(getattr(data, collection.property))
                )
            
            error = Control.errors().assign_expr_error
            if len(error) > 0: continue

            layout_row.label(
                text = str(collection.datas_assign[index])
            )

        self.draw_accessable_property()

    def draw_accessable_property(self):
        layout = self.layout.box()
        layout.label(text = "Accessable Property: ")

        layout = layout.column_flow(align = True, columns = 2)
        for prop in Control.accessable_properties():
            layout.label(text = prop)
