# Batch Assign - Batch Assign Multiple Properties With ERNA Syntax

## Why Batch Assign add-on
Sometimes we want to set properties or do some job with simple rules.
These rules include

- Rename selected objects into "obj_000", "obj_001", ... sorted by their x position.
- Rename bones from "leg left thigh" to "leg___thigh.L" and "leg right thigh" to "leg___thigh.R"..
- Import "*.obj" files in folder "obj" (reletive to current blend file).
- Reload all images used by selected objects' materials

Batch Assign add-on helps you get these jobs done with one string instead of

- Writing a 20 line python script with multiple for loops and takes you some time to debug.
- Working with complecated ui which may or may not reach your specific needs.
- Doing them one by one.

## Warning
- Batch Assign add-on is for blender 2.8 only.
- To use this add-on effectively requires basic python programming skill.
- You should be comfortable with python documentation and blender python api documentation.
- Beta Version

## Installation
1. Download the Batch Assign add-on source code somewhere.
2. Copy folder `batch_assign` into *`<your blender path>/2.8/scripts/addons_contrib/`*.
3. Open blender click *Edit->Preferences->Add-ons* and enable *Testing* support level.
4. Search *Batch Assign* and enable it.

## How it works

### Concepts
The one string you input is called a ERNA(Extended RNA Data Path).
Just like RNA in blender is used to get one property of one object.
ERNA is used to get multiple properties of multiple objects.
We call these bunch of objects a *collection*. 
Each one of these objects itself is called *data* of *collection*.
ERNA is the rule of Transforming from one *collection* into another *collection*.

### A Simple Example
```
# Rename selected objects into "obj_000", "obj_001", ... sorted by their x position.
!$bpy.context.selected_objects$@$data.location.x$=name$"obj_{0:03}".format(index)$
```

This long ERNA can be seperated by parts and each part is indicating a *collection* Transform.
Each ERNA Part is just a shorter ERNA.
The following steps show each part and how this add-on interpret them.

1. `!$bpy.context.selected_objects$` **Initial Operation** `[<obj_c>, <obj_b>, <obj_a>]`

    `!$<expr>$` is the syntax of Initial Operation.
    It simply ignore the input *collection* and use the value of `<expr>` as output Collection.
    `<expr>` is any python expresion that return an iterable object.

2. `@$data.location.x$` **Sort Operation** `[<obj_a>, <obj_b>, <obj_c>]`

    `@$<expr>$` is the syntax of Sort Operation.
    Sort all *data* in *collection* by using `<expr>` to calculate the sort key.

3. `=name$"obj_{0:03}".format(index)$` **Assign Operation** `[<obj_a>, <obj_b>, <obj_c>]`

    `=<name>$<expr>$` is the syntax of Assign Operation.
    Assign "name" property of each *data* with value of `<expr>`.
    Assign Operation will not change *collection* but store the assign information.
    The actual assignment is done later when user click assign button.

### Another Example With Binding Variables



## User Interface
After Batch Assign add-on enabled, three panels will appear at "misc" panel of the sidebar (press "N" to show the sidebar).

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
Access property of each *data* as result *collection*.
`<name>` is a valid python identifier.

| *collection*               | ERNA    | *collection* Transformed                     |
|----------------------------|---------|----------------------------------------------|
| `[data_0, data_1, data_2]` | `name`  | `[data_0.name, data_1.name, data_2.name]`    |
| `[data_0, data_1, data_2]` | `a.b.c` | `[data_0.a.b.c, data_1.a.b.c, data_2.a.b.c]` |

### Flatten Operation
```
*
*$<expr>$
```
Access each *Item* inside *data* as result *collection*, *data* must have `__iter__` method.

| *collection*                                   | ERNA | *collection* Transformed                   |
|------------------------------------------------|------|--------------------------------------------|
| `[[item_0_0, item_0_1], [item_1_0, item_1_1]]` | `*`  | `[item_0_0, item_0_1, item_1_0, item_1_1]` |

If `<expr>` is not provided, no new local variables introduced.
If `<expr>` is provided, it is a valid python expression with following local variables.

| Variable    | Value                        |
|-------------|------------------------------|
| length      | length of *collection*       |
| index       | index of *data* start from 0 |
| data        | value of *data*              |
| length_data | length of *data*             |
| index_item  | index of *Item* start from 0 |
| item        | value of *Item*              |

With these variables you have `collection[index][index_item] == item`
The value of `<expr>` is a dict which is used to introduce new local variables to item.

| *collection*               | ERNA                             | *collection* Transformed                   |
|----------------------------|----------------------------------|--------------------------------------------|
| `[[item_0_0], [item_1_0]]` | `*${"i":index, "j":index_item}$` | `[item_0_0{i:0, j:0}, item_1_0{i:1, j:0}]` |

### Sort Operation
```
@$<expr>$
```
Stable sort *collection* with the value of `<expr>` as key.

`<expr>` is any valid python expression with following local variables

| Variable | Value                  |
|----------|------------------------|
| data     | value of *data*        |
| length   | length of *collection* |

Suppose we have `data_0.name == "c" and data_1.name == "b" and data_2.name == "a"`

| *collection*               | ERNA           | *collection* Transformed   |
|----------------------------|----------------|----------------------------|
| `[data_0, data_1, data_2]` | `@$data.name$` | `[data_2, data_1, data_0]` |

### Filter Operation
```
|$<expr>$
```
Filter *collection* with the value of `<expr>`.

`<expr>` is any valid python expression with following local variables

| Variable | Value                        |
|----------|------------------------------|
| data     | value of *data*              |
| index    | index of *data* start from 0 |
| length   | length of *collection*       |

The value of `<expr>` is a bool which test whether the *data* exist in result *collection*.

Suppose we have `data_0.name == "a" and data_1.name == "b" and data_2.name == "c"`

| *collection*               | ERNA                  | *collection* Transformed |
|----------------------------|-----------------------|--------------------------|
| `[data_0, data_1, data_2]` | `|$data.name == "b"$` | `[data_1]`               |
| `[data_0, data_1, data_2]` | `|$index % 2 == 0$`   | `[data_0, data_2]`       |

### Take Operation
```
[<start>:<stop>:<step>]
```

Take *data* in *collection* with python slice similar syntax.
`<start>`, `<stop>` and `<step>` are int numbers.

| *collection*                               | ERNA    | *collection* Transformed   |
|--------------------------------------------|---------|----------------------------|
| `[data_0, data_1, data_2, data_3, data_4]` | `[2]`   | `[data_2]`                 |
| `[data_0, data_1, data_2, data_3, data_4]` | `[2:4]` | `[data_2, data_3]`         |
| `[data_0, data_1, data_2, data_3, data_4]` | `[::2]` | `[data_0, data_2, data_4]` |

### Variable Operation
```
%$<expr>$
%%$<expr>$
```
`%$<expr>$` Introduce new local variables bind to *data*.
`%%$<expr>$` Introduce new global variables bind to *collection*.

`<expr>` is a python expression with following local variables

| Variable | Value                        |
|----------|------------------------------|
| length   | length of *collection*       |
| index    | index of *data* start from 0 |
| data     | value of *data*              |

The return value of `<expr>` is a dict which is used to introduce new variables.
This operation will not change *collection*.

| *collection*       | ERNA                         | *collection* Transformed               |
|--------------------|------------------------------|----------------------------------------|
| `[data_0, data_1]` | `%${"i":index, "l":length}$` | `[data_0{i:0, l:2}, data_1{i:1, l:2}]` |


### Assign Operation
```
=<name>$<expr>$
```

Store an assignment which assign value of `<expr>` to *data*.`<name>` property.
Will do the actual assignment after user clicking the Assign button.
This operation will not change *collection*.

| Variable | Value                        |
|----------|------------------------------|
| length   | length of *collection*       |
| index    | index of *data* start from 0 |
| data     | value of *data*              |
| prop     | value of *data*`.<name>`     |

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
op -> one of op_???
op_prop -> ["."] t_name ("." op_prop)*
op_map -> "-" t_expr
op_init -> "!" (t_expr | t_number)
op_flatten -> "*" [ t_expr ]
op_sort -> "@" [ t_expr ]
op_filter -> "|" t_expr
op_take -> "[" t_number [ ":" t_number [ ":" t_number ]] "]"
op_var -> "%" t_expr
op_assign -> "=" t_name t_expr
op_delay -> "\" t_expr
```

## Preset File
A preset file is just a plain text file which save multiple ERNA with keys.
It is saved as text data so you may edit it with blender text editor or append it across blender files.
The Batch Assign Preset Panel is used to load preset file and set ERNA to Batch Assign Main Panel.
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

## Examples
File `EXAMPLES.txt` in source code show some examples in preset file syntax.
