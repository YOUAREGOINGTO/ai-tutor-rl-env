# Chapter 2: The Normal Distribution

The **normal distribution** (also called the Gaussian distribution) is the most important probability distribution in statistics and data science. It describes how continuous data is distributed symmetrically around a central mean value.

## Definition

A normal distribution is completely defined by two parameters:
- **Mean (μ)**: The center of the distribution, where the peak occurs
- **Standard Deviation (σ)**: Controls the spread — larger σ means more dispersed data

The probability density function is:

```
f(x) = (1 / (σ√(2π))) * exp(-(x - μ)² / (2σ²))
```

## The Bell Curve Shape

The normal distribution produces a characteristic **bell-shaped curve** that is:
- **Symmetric** about the mean: exactly half the data falls above, half below
- **Unimodal**: one single peak at the mean
- **Asymptotic**: the tails approach but never touch zero

## The 68-95-99.7 Rule (Empirical Rule)

One of the most useful properties of the normal distribution is how data clusters around the mean:
- **68%** of data falls within **1 standard deviation** of the mean (μ ± σ)
- **95%** of data falls within **2 standard deviations** (μ ± 2σ)
- **99.7%** of data falls within **3 standard deviations** (μ ± 3σ)

## Why Normal Distributions Appear Everywhere

The **Central Limit Theorem (CLT)** explains why the normal distribution is so ubiquitous. It states that when independent random variables are added together, their normalized sum tends toward a normal distribution — regardless of the shape of the original distribution.

This is why:
- Heights of people in a population are normally distributed
- Measurement errors in experiments are normally distributed
- Test scores across large populations are normally distributed

## The Standard Normal and Z-Scores

The **standard normal distribution** has μ = 0 and σ = 1. Any normal distribution can be converted to the standard normal using the **z-score**:

```
z = (x - μ) / σ
```

The z-score tells you how many standard deviations a data point is from the mean, allowing comparison across different datasets.

## Applications in Machine Learning

Normal distributions appear throughout machine learning:
- **Weight initialization**: Neural network weights are often initialized from a normal distribution
- **Gaussian Naive Bayes**: Assumes features are normally distributed within each class
- **Anomaly detection**: Points with a high z-score (far from mean) are flagged as anomalies
- **Linear regression**: Assumes residual errors are normally distributed
