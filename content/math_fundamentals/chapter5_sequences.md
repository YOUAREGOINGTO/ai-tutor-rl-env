# Chapter 5: Sequences

## Arithmetic Sequences
Each term increases by a fixed amount called the **common difference** (`d`).

**General term:** `a_n = a + (n-1) * d`

**Sum of first n terms:** `S = n/2 * (2a + (n-1)*d)`

**Example:** 2, 5, 8, 11 … (d = 3)

## Geometric Sequences
Each term is multiplied by a fixed value called the **common ratio** (`r`).

**General term:** `a_n = a * r ** (n-1)`

**Sum of first n terms:**
```
S = a * (1 - r**n) / (1 - r)    # when r ≠ 1
S = a * n                        # when r = 1
```

- `a` = first term
- `r` = common ratio
- `n` = number of terms

### Example
Sequence: 3, 6, 12, 24 … (a=3, r=2)

Sum of first 5 terms:
```
S = 3 * (1 - 2**5) / (1 - 2)
S = 3 * (1 - 32) / (-1)
S = 3 * 31 = 93
```

### Special Case: Infinite Geometric Series
When |r| < 1, the series converges:
```
S_∞ = a / (1 - r)
```

Example: 1 + 0.5 + 0.25 + … → S = 1 / (1 - 0.5) = 2
