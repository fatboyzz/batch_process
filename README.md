# Batch Assign - Batch Assign Multiple Properties With ERNA Syntax

## Why Batch Assign add-on
Sometimes we want to set multiple properties with some simple rules.

These rules including:

- Renaming selected objects into "obj_0", "obj_1", ... sorted by their x position.
- Renaming all bones of an armature from "bone_left" to "bone.L" and same changes to corresponding vertex groups.

Batch Assign add-on helps you get these jobs done with one string instead of

- Writing a 20 line python script with multiple for loops and take you some time to debug.
- Working with complecated renaming ui which may or may not reach your specific needs.
- Doing them one by one.

## Warning
- This add-on is for blender 2.8 only.
- To use this add-on effectively requires basic python programming skill.
- You should be comfortable with python documentation and blender python api documentation.
- Everything under development.

## How it works
The one string you input is called a ERNA(Extended RNA Data Path).
Just like RNA in blender is used to get one property of one object.
ERNA is used to get multiple properties of multiple objects.
We call these bunch of objects a *Collection*. 
Each one of these objects itself is called *Data* of *Collection*.
ERNA is the rule of Transforming from one *Collection* into another *Collection*.
Here is the full ERNA for renaming selected objects into "obj_0", "obj_1", ... sorted by their x position.

```
bpy.context.selected_objects*@$data.location.x$=name$"obj_"+str(index)$
```

This long ERNA can be seperated by parts and each part is indicating a *Collection* Transform.
Each ERNA Part is just a shorter ERNA.
The following table show the steps of how the add-on interpret this ERNA and transform the *Collection*.

| *Collection*                    | ERNA                       | Transform | Description                                                     |
|---------------------------------|----------------------------|-----------|-----------------------------------------------------------------|
| `[<initial>]`                   |                            |           | initial is a special *Data* with one property "bpy"             |
| `[<initial>]`                   | `bpy`                      | Property  | access "bpy" property of each *Data* as the result *Collection* |
| `[<module 'bpy'>]`              | `.context`                 | Property  | access "context" property                                       |
| `[<bpy_struct, Context>]`       | `.selected_objects`        | Property  | access "selected_objects" property                              |
| `[[<obj_c>, <obj_b>, <obj_a>]]` | `*`                        | Flatten   | for each *Data* put all *Data* element in result *Collection*   |
| `[<obj_c>, <obj_b>, <obj_a>]`   | `@$data.location.x$`       | Sort      | sort *Data* by accessing property location.x as sort key        |
| `[<obj_a>, <obj_b>, <obj_c>]`   | `=name$"obj_"+str(index)$` | Assign    | assign "name" property of each *Data* with python expression    |

## Installation
1. Download the Batch Assign add-on source code somewhere.
2. Copy folder `batch_assign` into *`<your blender path>/2.8/scripts/addons_contrib/`*.
3. Open blender click *Edit->Preferences->Add-ons* and enable *Testing* support level.
4. Search *Batch Assign* and enable it.

## User Interface
After Batch Assign add-on enabled, three panels will appear at "misc" panel of sidebar (press "N" to show the sidebar).

![panels_title.png](image/panels_title.png)


### Batch Assign Main Panel

### Batch Assign Preset Panel

### Batch Assign Settings Panel

## ERNA Syntax Reference

### Property Operation
```
<name>
<name>.<name>.<name> ...
```
Access property of each *Data* as result *Collection*.
`<name>` is a valid python identifier.

| *Collection*               | ERNA    | *Collection* Transformed                     |
|----------------------------|---------|----------------------------------------------|
| `[data_0, data_1, data_2]` | `name`  | `[data_0.name, data_1.name, data_2.name]`    |
| `[data_0, data_1, data_2]` | `a.b.c` | `[data_0.a.b.c, data_1.a.b.c, data_2.a.b.c]` |

### Flatten Operation
```
*
*$<expr>$
```
Access each *Item* inside *Data* as result *Collection*, *Data* must have `__iter__` method.

| *Collection*                                   | ERNA | *Collection* Transformed                   |
|------------------------------------------------|------|--------------------------------------------|
| `[[item_0_0, item_0_1], [item_1_0, item_1_1]]` | `*`  | `[item_0_0, item_0_1, item_1_0, item_1_1]` |

If `<expr>` is not provided, no new local variables introduced.
If `<expr>` is provided, it is a valid python expression with following local variables.

| Variable    | Value                        |
|-------------|------------------------------|
| length      | length of *Collection*       |
| index       | index of *Data* start from 0 |
| data        | value of *Data*              |
| length_data | length of *Data*             |
| index_item  | index of *Item* start from 0 |
| item        | value of *Item*              |

With these variables you have `collection[index][index_item] == item`
The value of `<expr>` is a dict which is used to introduce new local variables to item.

| *Collection*               | ERNA                             | *Collection* Transformed                   |
|----------------------------|----------------------------------|--------------------------------------------|
| `[[item_0_0], [item_1_0]]` | `*${"i":index, "j":index_item}$` | `[item_0_0{i:0, j:0}, item_1_0{i:1, j:0}]` |

### Sort Operation
```
@$<expr>$
```
Stable sort *Collection* with the value of `<expr>` as key.

`<expr>` is any valid python expression with following local variables

| Variable | Value                  |
|----------|------------------------|
| data     | value of *Data*        |
| length   | length of *Collection* |

Suppose we have `data_0.name == "c" and data_1.name == "b" and data_2.name == "a"`

| *Collection*               | ERNA           | *Collection* Transformed   |
|----------------------------|----------------|----------------------------|
| `[data_0, data_1, data_2]` | `@$data.name$` | `[data_2, data_1, data_0]` |

### Filter Operation
```
|$<expr>$
```
Filter *Collection* with the value of `<expr>`.

`<expr>` is any valid python expression with following local variables

| Variable | Value                        |
|----------|------------------------------|
| data     | value of *Data*              |
| index    | index of *Data* start from 0 |
| length   | length of *Collection*       |

The value of `<expr>` is a bool which test whether the *Data* exist in result *Collection*.

Suppose we have `data_0.name == "a" and data_1.name == "b" and data_2.name == "c"`

| *Collection*               | ERNA                  | *Collection* Transformed |
|----------------------------|-----------------------|--------------------------|
| `[data_0, data_1, data_2]` | `|$data.name == "b"$` | `[data_1]`               |
| `[data_0, data_1, data_2]` | `|$index % 2 == 0$`   | `[data_0, data_2]`       |

### Take Operation
```
[<start>:<stop>:<step>]
```

Take *Data* in *Collection* with python slice similar syntax.
`<start>`, `<stop>` and `<step>` are int numbers.

| *Collection*                               | ERNA    | *Collection* Transformed   |
|--------------------------------------------|---------|----------------------------|
| `[data_0, data_1, data_2, data_3, data_4]` | `[2]`   | `[data_2]`                 |
| `[data_0, data_1, data_2, data_3, data_4]` | `[2:4]` | `[data_2, data_3]`         |
| `[data_0, data_1, data_2, data_3, data_4]` | `[::2]` | `[data_0, data_2, data_4]` |

### Variable Operation
```
%$<expr>$
```
Introduce new local variables to *Data*.
`<expr>` is any valid python expression with following local variables

| Variable | Value                        |
|----------|------------------------------|
| data     | value of *Data*              |
| index    | index of *Data* start from 0 |
| length   | length of *Collection*       |

The return value of `<expr>` is a dict which is used to introduce new local variables to *Data*.
This operation will not change *Collection*.

| *Collection*       | ERNA                         | *Collection* Transformed               |
|--------------------|------------------------------|----------------------------------------|
| `[data_0, data_1]` | `%${"i":index, "l":length}$` | `[data_0{i:0, l:2}, item_1{i:1, l:2}]` |


### Assign Operation
```
=<name>$<expr>$
```

Declare an assignment that assign value of `<expr>` to *Data*'s `<name>` property.
Will do the actual assignment after user clicking the Assign button.
This operation will not change *Collection*.

### Global Variables
All python expression `<expr>` may access global variables in following table.

| Variables      |    |           |
|----------------|----|-----------|
| `__builtins__` | re | mathutils |

If you want to access python modules that are not listed here, 
you have to manually change `Expression_Globals` in source code file `globals_model.py`

### ERNA Grammar Specification
```
erna -> op* t_stop
op -> one of following op_???
op_prop -> ["."] t_name ("." op_prop)*
op_map -> "$" t_expr
op_init -> "!" t_expr
op_flatten -> "*" [ t_expr ]
op_sort -> "@" t_expr
op_filter -> "|" t_expr
op_take -> "[" t_number [ ":" t_number [ ":" t_number ]] "]"
op_var -> "%" t_expr
op_assign -> "=" t_name t_expr
op_delay -> "\" t_expr
```

## ERNA Examples
File `EXAMPLES.txt` in source code listed all examples bellow as a preset file.

### Object Select Examples : 

```
#[Initial] -> [bpy.types.Object]

```


### Renaming Examples


### Miscellaneous Examples

- Renaming objects selected into "obj_001", "obj_002", ... , "obj_100" sorted by their x position.


- Renaming all bones of an armature from "bone_left" to "bone.L" and same changes to corresponding vertex groups.


- Renaming all materials of selected objects into `"<obj_name>_M00"`, `"<obj_name>_M01"`, ... .
```

```

- Set "obj_color_00.tga", "obj_normal_00.tga", "obj_srma_00.tga", "obj_color_01.tga" ... into corresponding image node of obj's material slot.

## Preset File
A preset file is just a plain text file to save multiple ERNA with keys.
It is saved as text data so you may edit it with blender text editor or append it across blender files.
The Batch Assign Preset Panel is used to load preset file and set ERNA to Batch Assign Main Panel.
The preset file is loaded into an `OrderedList` thus the keys are sorted.
A preset file has a simple line based syntax showing bellow.

```
# Any characters after "#" of a line are comments
<zero or more empty lines>
<key_0> # The key must be unique for each preset file
<erna_0>
<erna_1>
<one or more empty lines>
<key_1>
<erna_0>
<erna_1>
<erna_2>
<one or more empty lines>
<key_2>
<erna_0>
```
