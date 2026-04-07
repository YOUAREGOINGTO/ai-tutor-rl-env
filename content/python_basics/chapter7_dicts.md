# Chapter 7: Dictionaries

A dictionary stores **key-value pairs**. Keys must be unique.

## Creating a Dictionary
```python
student = {"name": "Alice", "age": 20, "grade": "A"}
```

## Accessing Values
```python
print(student["name"])   # Alice
print(student["age"])    # 20
```

## KeyError
A **KeyError** is raised when you try to access a key that does not exist:
```python
d = {"a": 1}
print(d["b"])   # KeyError: 'b'
```

## Safe Access with .get()
Use `.get(key, default)` to avoid KeyError:
```python
print(d.get("b", "not found"))   # not found
print(d.get("a", "not found"))   # 1
```

If no default is given, `.get()` returns `None` instead of raising an error.

## Adding and Updating
```python
student["email"] = "alice@example.com"   # add new key
student["age"] = 21                      # update existing key
```

## Removing Keys
```python
del student["grade"]           # removes key, raises KeyError if missing
student.pop("age", None)       # removes key safely, returns None if missing
```

## Iterating
```python
for key in student:
    print(key, student[key])

for key, value in student.items():
    print(key, "->", value)
```

## Useful Methods
| Method             | Description                      |
|--------------------|----------------------------------|
| `.keys()`          | All keys                         |
| `.values()`        | All values                       |
| `.items()`         | All (key, value) pairs           |
| `.get(k, default)` | Safe access with fallback        |
| `.pop(k, default)` | Remove and return value safely   |
