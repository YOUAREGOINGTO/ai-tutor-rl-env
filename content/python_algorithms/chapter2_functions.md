# Chapter 2: Functions & Scope

## Defining a Function
```python
def function_name(parameter1, parameter2):
    # body
    return result
```

## Basic Example
```python
def add(a, b):
    return a + b

result = add(3, 5)   # 8
```

## Default Parameters
```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

greet("Alice")           # "Hello, Alice!"
greet("Bob", "Hi")       # "Hi, Bob!"
```

## Applying to Math Formulas
Functions are ideal for encoding mathematical formulas clearly:

```python
def compound_interest(P, r, n, t):
    """
    Calculate compound interest.
    P: principal
    r: annual interest rate (decimal)
    n: compounding frequency per year
    t: time in years
    Returns: final amount A
    """
    return P * (1 + r / n) ** (n * t)
```

Usage:
```python
amount = compound_interest(1000, 0.05, 12, 3)
print(f"Final amount: £{amount:.2f}")   # £1161.62
```

## Scope
- Variables defined inside a function are **local** — not accessible outside.
- Variables defined outside a function are **global**.

```python
x = 10   # global

def show():
    x = 99   # local — does NOT change global x
    print(x)

show()    # 99
print(x)  # 10
```

## Return vs Print
- `return` sends the value back to the caller.
- `print` just displays it — the value is lost.

Always use `return` when the result will be used in further calculations.
