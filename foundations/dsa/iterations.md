# Iterations

In programming, iterating means repeating some part of your program. This lesson presents basic programming constructions that allow iterations to be performed: “for” and “while” loops.

## Types of loops

1. For loops
2. While Loops


## For Loops

These are use for iterating in a set of values

### Python

```py
for variable in iterable_items:
    # do something with the variable
    pass
```

A very common thing you might see in python is the `range` function.

It is used like `range(start, stop, step)`

> It creates an iterable list of items.

```py
for i in range(0, 100, 1):
    print(i)
    # This prints from 0-99
```

In programming, indexing starts from 0 and conventionally, if you are using the range function and the first value is zero, you can omit it and then add just the final number without the step

```py
for i in range(100):
    print(i)
```

> If you are going to be adding a step, the start and stop are both required!

