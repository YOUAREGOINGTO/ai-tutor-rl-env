# Chapter 6: Sorting Algorithms

## Bubble Sort

Repeatedly steps through the list, compares adjacent elements, and swaps them if out of order.

**Time Complexity:** O(n²)
**Space Complexity:** O(1)

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
```

**Example:**
```python
bubble_sort([64, 34, 25, 12, 22])
# → [12, 22, 25, 34, 64]
```

**Pros:** Simple to understand and implement.
**Cons:** Very slow for large lists — O(n²) means 1 million comparisons for 1000 elements.

---

## Merge Sort

Divides the list in half recursively, sorts each half, then merges them back together.

**Time Complexity:** O(n log n)
**Space Complexity:** O(n)

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

**Example:**
```python
merge_sort([38, 27, 43, 3, 9])
# → [3, 9, 27, 38, 43]
```

**Pros:** Much faster than bubble sort for large inputs. Stable sort.
**Cons:** Uses extra memory (O(n)).

---

## Comparison

| Algorithm   | Time (avg) | Time (worst) | Space | Stable |
|-------------|------------|--------------|-------|--------|
| Bubble Sort | O(n²)      | O(n²)        | O(1)  | Yes    |
| Merge Sort  | O(n log n) | O(n log n)   | O(n)  | Yes    |

**Rule of thumb:** Use merge sort (or Python's built-in `sorted()`) for anything over a few hundred elements.
