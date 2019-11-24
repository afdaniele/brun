# brun

**brun** (batch-run) is a utility used to run parameterized shell commands


## Install

You can install **brun** using pip:

```
pip3 install brun
```


## Usage

The simplest **brun** command looks like the following

```
brun -f x:range:10 -- echo {x}
```

If we run this command, the output will be

```
0
1
2
3
4
5
6
7
8
9
```


## Syntax

The syntax for **brun** is very simple:

```
brun --field name:type:arguments -- command
```

The argument `--field` (in short `-f`) defines a field. A field has a `name`, a `type` and some `arguments`. For example,
`-f x:range:10` defines the field `x` as the range `[0,9]`. The delimiter `--` indicates where the `command` begins. The `command` is a prototype of a shell command with some dynamic parts. For example, `echo {x}` together with the range `x = [0,9]` generates 10 commands by replacing `{x}` with all the values of `x`.

### Fields

**brun** supports multiple field types.

#### List

Populates a placeholder according to a list of given values. The syntax is
```
-f name:list:value1,value2,...
```
For example, `-f x:list:0,2,4`, or, similarly `-f x:l:0,2,4`.


#### Range

Populates a placeholder according to a given range of values. The syntax is
```
-f name:range:s[,f[,i]]
```
If only `s` is given, the computed range will be `[0,s-1]`. If only `s` and `f` are given, the computed range will be `[s,f-1]`. If all the three arguments are given, the range will be `[s,f-1]` with a step of `i`.
The type `r` is an alias for `range`.


#### File

Populates a placeholder according to the content of a file. The syntax is
```
-f name:file:filepath
```
The values will be loaded from the given file, the content of one line will generate one value.
The type `f` is an alias for `file`.


#### Glob

Populates a placeholder according to the content of a directory. The syntax is
```
-f name:glob:path,[query,[filter-type]]
```
The argument `path` specifies the path to examine, `query` is a glob-like regular expression to filter the results, `filter-type` is one of `[*, f, g]` indicating the types of objects to include, `* (all)`, `f (file)`, `d (directories)`.
The type `g` is an alias for `glob`.


### Groups

Groups are used to link two or more fields together.
In particular, a group defines how the values of two or more fields change with respect to each other.

Groups are specified using the argument `--group` (in short `-g`). The syntax is the following:
```
--group type:field1,field2,...[:arguments]
```

 A group has a `type`, a list of fields (i.e., `field1,field2,...`), and some `arguments`.


#### Cross

The type `cross` links two or more field values using the Cartesian product. This is the default grouping strategy for fields in **brun**.
For example, the command

```
brun -f x:r:2 -f y:r:3 -g cross:x,y -- echo {x},{y}
```

will produce the following output

```
0,0
0,1
0,2
1,0
1,1
1,2
```


#### Zip

The type `zip` links two or more field values using the indices of their values.
Field values will be clipped at the size of the smallest field within the group.
For example, the command

```
brun -f x:r:2 -f y:r:3 -g zip:x,y -- echo {x},{y}
```

will produce the following output

```
0,0
1,1
```
