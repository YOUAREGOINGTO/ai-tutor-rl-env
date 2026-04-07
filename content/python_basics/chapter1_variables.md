# Chapter 1: Variables

A variable stores a value. Use `=` to assign it.

```python
x = 10
name = "Alice"
is_active = True
```

## Key Rules
- Variable names are case-sensitive: `age` and `Age` are different.
- Names can contain letters, digits, and underscores, but cannot start with a digit.
- Python is **dynamically typed** — you don't declare a type, Python infers it.

## Basic Types

| Type    | Example         |
|---------|-----------------|
| int     | `x = 5`         |
| float   | `pi = 3.14`     |
| str     | `name = "Bob"`  |
| bool    | `flag = True`   |

## Reassignment
Variables can be reassigned to a different type at any time:
```python
x = 10       # int
x = "hello"  # now a str — this is valid in Python
```

## Multiple Assignment
```python
a, b, c = 1, 2, 3
x = y = 0   # both x and y are 0
```
