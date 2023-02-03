
# Table of Contents

1.  [Installation](#org70e4049)
2.  [Usage](#orgb508a19)
    1.  [Immutable Models](#org0af78d0)
    2.  [Steps](#org0b869c1)
    3.  [Stateful Steps](#org361d033)
    4.  [Implementation Map](#orgcaba283)
    5.  [Flow File](#orge205dca)



<a id="org70e4049"></a>

# Installation

Nacolla requires python 3.9 or newer.
Install it through pip
```bash
    pip install nacolla
```

<a id="orgb508a19"></a>

# Usage

Nacolla provides a way to define type-hinted computation steps and compose them through type-validated flows.
Each step has an interface defined by all the functions contained inside the step. Those functions cannot have overlapping interfaces. When some data arrives with a given type is dispatched to the right function inside the step through the user-provided type hints. We then define where the output data will land given its type.
Running a flow is easy:
```python
    implementation_map: IMPLEMENTATION_MAP = parse_implementation_map(
          Path("<path/to/implementation_map.json>")
      )
      flow: Flow[WrappedInt] = parse_flow(
          Path("<path/to/flow.toml>"),
          implementation_map=implementation_map,
          source=WrappedFloat(a_float=2.0), # input data
      )
    
      intermediate_results = []
          for step in flow:
          intermediate_results.append(flow.current_message) # We can store intermediate results
```
We will now describe what the above means from the ground up.


<a id="org0af78d0"></a>

## Immutable Models

All transformations in Nacolla accept only types inheriting from ImmutableModel, which is a type provided by Nacolla.
Immutable Models are frozen pydantic base models:
```python
    class WrappedString(ImmutableModel):
        a_string: StrictStr
```
This allows us to remove a large portion of side effects in users&rsquo; computations.


<a id="org0b869c1"></a>

## Steps

The main building blocks of Nacolla are steps.
A step is any type-hinted function:
```python
    def int_to_str(i: WrappedInt) -> WrappedString:
        return WrappedString(a_string=str(i.a_int))
```
The above defines a step which maps a WrappedInt to a WrappedString.


<a id="org361d033"></a>

## Stateful Steps

A stateful step is any class which inherits from StatefulStep:
```python
    class A(StatefulStep[WrappedString, Union[WrappedString, WrappedEndString]]):
        def __init__(self, prefix: str) -> None:
            super().__init__()
            self.storage = prefix
    
        def str_append(self, s: WrappedString) -> Union[WrappedString, WrappedEndString]:
    
            self.storage += s.a_string
            if len(self.storage) < 20:
                return WrappedString(a_string=self.storage)
            else:
                return WrappedEndString(a_string=self.storage)
```
Here the interface of the block is defined by the public methods of the class, all non<sub>public</sub> methods (i.e. the ones starting with at least one underscore) are ignored.


<a id="orgcaba283"></a>

## Implementation Map
```json
    {
        "implementations":[
            {"callable": {"module":
                          "./resources/test_step_implementation_file.py"},
            "kwargs": {
                "A": {
                    "prefix": "my_prefix_in_dict"
                }
            },
             "name": "step1"},
            {"callable": {"module":
                          "./resources/test_step_implementation_file2.py",
                          "name": "int_to_str" },
             "name": "step2"},
            {"callable": {"module":
                          "./resources/test_step_implementation_file.py",
                          "name":"A"},
            "kwargs": {
                "prefix": "my_prefix"
            },
             "name": "step3"}
        ]
    }
```
An implementation map is a JSON file that specifies which blocks are available to nacolla.
The first section is the `callable` section. In there we specify the path to the file containing the module and in case the file contains multiple modules we also specify the name.
The second section is the optional `kwargs` section. This section is available only in case the file contains a StatefulStep and this kwargs will be passed to the constructor.


<a id="orge205dca"></a>

## Flow File
```toml
    root = "step1"
    
    [step1]
    WrappedInt = "step2"
    WrappedString  = ""
    
    [step2]
    WrappedString = "step3"
    
    [step3]
    WrappedString = "step3"
```
A flow file is a TOML file that specifies how blocks are connected.
The `root` field specifies the entry point.
Then for each step we want to include, in any order, we specify for each output type the corresponding destination block.
Data will be then dispatched to the right function inside the block given the type hints provided.

