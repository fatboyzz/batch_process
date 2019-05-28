import bpy
from .utils import *
from .main_control import *

register_classes = []

@append(register_classes)
class BatchAssign_OP_MainControlUpdate(bpy.types.Operator):
    bl_idname = "batch_assign.main_control_update"
    bl_label = "Update Collection"
    bl_description = "Update Collection"

    def execute(self, context):
        BatchAssign_MainControl.get().update()
        return {'FINISHED'}

@append(register_classes)
class BatchAssign_OP_MainControlBatchAssign(bpy.types.Operator):
    bl_idname = "batch_assign.main_control_batch_assign"
    bl_label = "Update Collection"
    bl_description = "Batch Assign Value"
    
    def execute(self, context):
        BatchAssign_MainControl.get().update()
        return {'FINISHED'}
    
@append(register_classes)
class BatchAssign_PT_MainPanel(bpy.types.Panel):
    bl_idname = "BatchAssign_PT_MainPanel"
    bl_label = "Batch Assign Main"
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
        errors = BatchAssign_MainErrors.get()

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
            "batch_assign.main_control_update",
            text = "Update",
        )

        self.draw_erna()

    def draw_erna(self):
        layout = self.layout.box()
        layout.label(text = "ERNA Data Path:")

        layout_column = layout.column(align = True)
        model = BatchAssign_MainModel.get()
        errors = BatchAssign_MainErrors.get()

        layout_column.prop(
            data = model,
            property = "erna",
            text = "",
            icon = "TEXT",
        )

        self.draw_error_indicator(layout_column, "erna_error_indicator")
        self.draw_error(layout, errors.erna_error)

        self.draw_expr()

    def draw_expr(self):
        layout = self.layout.box()
        layout.label(text = "Assign Expression: ")

        layout_column = layout.column(align = True)
        model = BatchAssign_MainModel.get()
        errors = BatchAssign_MainErrors.get()

        layout_column.prop(
            data = model,
            property = "expr",
            text = "",
            icon = "TEXT",
        )
    
        self.draw_error_indicator(layout_column, "expr_error_indicator")
        self.draw_error(layout, errors.expr_error)

        self.draw_assign_button()

    def draw_assign_button(self):
        layout = self.layout
        layout.operator(
            "batch_assign.main_control_batch_assign",
            text = "Assign",
        )

        self.draw_errors()

    def draw_errors(self):
        layout = self.layout
        errors = BatchAssign_MainErrors.get()

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
        control = BatchAssign_MainControl.get()
        collection = control.collection
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
            
            error = BatchAssign_MainErrors.get().expr_error
            if len(error) > 0: continue

            layout_row.label(
                text = str(collection.datas_assign[index])
            )

        self.draw_accessable_property()

    def draw_accessable_property(self):
        layout = self.layout.box()
        layout.label(text = "Accessable Property: ")

        layout = layout.column_flow(align = True, columns = 2)

        control = BatchAssign_MainControl.get()
        for prop in control.accessable_properties():
            layout.label(text = prop)
