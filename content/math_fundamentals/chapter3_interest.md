# Chapter 3: Interest & Growth

## Simple Interest
Simple interest is calculated only on the principal amount.

**Formula:** `I = P * r * t`

- `P` = principal (initial amount)
- `r` = annual interest rate (decimal)
- `t` = time in years

**Example:** £1000 at 5% for 3 years → I = 1000 × 0.05 × 3 = £150

## Compound Interest
Compound interest is calculated on the principal **and** accumulated interest.

**Formula:** `A = P * (1 + r/n) ** (n * t)`

- `A` = final amount
- `P` = principal
- `r` = annual interest rate (decimal, e.g. 0.05 for 5%)
- `n` = number of times interest compounds per year
- `t` = time in years

### Common Compounding Frequencies

| Frequency   | n value |
|-------------|---------|
| Annually    | 1       |
| Semi-annual | 2       |
| Quarterly   | 4       |
| Monthly     | 12      |
| Daily       | 365     |

### Example
£1000 at 5% compounded monthly for 3 years:
```
A = 1000 * (1 + 0.05/12) ** (12 * 3)
A = 1000 * (1.004167) ** 36
A ≈ £1161.62
```

## Compound vs Simple Interest
Compound interest grows **faster** over time because each period's interest also earns interest.
At 5% over 10 years:
- Simple: £500 interest (flat)
- Compound monthly: ≈ £647 interest
