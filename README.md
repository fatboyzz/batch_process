# Batch Assign - Batch Set Multiple Properties With ERNA Syntax

## Overview
Sometimes we want to set multiple properties with simple rules.

These rules include:

- Renaming selected objects into "obj_0", "obj_1", ... sorted by their x position.
- Renaming all bones of an armature from "bone_left" to "bone.L" and same changes to corresponding vertex groups.

Batch Assign add-on helps you get these jobs done with one string instead of

- Writing a 20 line python script with multiple for loops and take you some time to debug.
- Working with complecated renaming ui which may or may not reach your specific needs.
- Doing them one by one.

## Warning

- To use this add-on effectively requires basic python programming knowledge.
- You should be comfortable with python documentation and blender api documentation.
- Everything is under development now(2019-06-01).

## How it works
The one string you input is called a ERNA(Extended RNA Data Path).

Just like RNA in blender is used to get one property of one object.

ERNA is used to get multiple properties of multiple objects.

We call these bunch of objects a Collection. 

These objects itself is called Data of Collection.

ERNA is the rule of Transforming form one Collection into another Collection.

Here is the full ERNA for renaming selected objects into "obj_0", "obj_1", ... sorted by their x position.

    bpy.context.selected_objects*@$data.location.x$=name$"obj_"+str(index)$

This long ERNA can be seperated by parts and each part is indicating a Collection Transform.

Each ERNA Part is just a shorter ERNA.

The following table show the steps of how the add-on interpret this ERNA and transform the Collection.

| Collection                      | ERNA                     | Transform | Description                                                 |
|---------------------------------|--------------------------|-----------|-------------------------------------------------------------|
| `[<initial>]`                   |                          |           | initial is a special Data with one property "bpy"           |
| `[<initial>]`                   | bpy                      | Property  | access "bpy" property of each Data as the result Collection |
| `[<module 'bpy'>]`              | .context                 | Property  | access "context" property                                   |
| `[<bpy_struct, Context>]`       | .selected_objects        | Property  | access "selected_objects" property                          |
| `[[<obj_c>, <obj_b>, <obj_a>]]` | *                        | Flatten   | for each Data put all Data element in result Collection     |
| `[<obj_c>, <obj_b>, <obj_a>]`   | @$data.location.x$       | Sort      | sort Data by accessing property location.x as sort key      |
| `[<obj_a>, <obj_b>, <obj_c>]`   | =name$"obj_"+str(index)$ | Assign    | assign "name" property of each Data with python expression  |

## User Interface
After Batch Assign add-on enabled, three panels will appear at "misc" panel of sidebar (press "N" to show the sidebar).

### Batch Assign Main Panel

### Batch Assign Preset Panel

### Batch Assign Settings Panel

## ERNA Syntax

## ERNA Examples
- Renaming 100 objects into "obj_001", "obj_002", ... , "obj_100" sorted by their x position.
- Renaming all bones of an armature from "bone_left" to "bone.L" and same changes to corresponding vertex groups.
- Renaming materials of object "obj" into "obj_mat_001", "obj_mat_002", ... .
- Set "obj_color.tga", "obj_normal.tga", "obj_srma.tga", ... into corresponding image node of obj's material.
