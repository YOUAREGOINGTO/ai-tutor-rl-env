# Chapter 4: For Loops

A `for` loop iterates over any sequence — a list, string, or range.

## Basic Syntax
```python
for variable in sequence:
    # body
```

## Using range()
`range()` generates a sequence of numbers.

```python
for i in range(5):
    print(i)   # prints 0, 1, 2, 3, 4
```

### range() Parameters
```python
range(stop)             # 0 to stop-1
range(start, stop)      # start to stop-1
range(start, stop, step)  # with custom step
```

Examples:
```python
range(1, 6)        # 1, 2, 3, 4, 5
range(0, 10, 2)    # 0, 2, 4, 6, 8
range(10, 0, -1)   # 10, 9, 8 ... 1 (countdown)
```

## Iterating Over a List
```python
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
```

## Iterating Over a String
```python
for char in "hello":
    print(char)   # h, e, l, l, o
```

## Nested For Loops
```python
for i in range(3):
    for j in range(3):
        print(i, j)
```

## Loop Control
- `break` — exit the loop immediately
- `continue` — skip to the next iteration
- `else` — runs after the loop completes normally (not after break)
