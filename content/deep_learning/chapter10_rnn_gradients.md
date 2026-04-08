# Chapter 10: Sequence Modeling — Recurrent and Recursive Nets
# Source: "Deep Learning" by Goodfellow, Bengio, and Courville

## 10.7 The Challenge of Long-Term Dependencies

The mathematical challenge at the root of recurrent neural networks is that gradients propagated over many stages tend to either vanish or explode.

Consider a simplified RNN without a nonlinearity, defined by the recurrence:

h(t) = W * h(t-1)

After unrolling t steps, this becomes:

h(t) = W^t * h(0)

The behavior of this expression depends entirely on the eigenvalues of W. If we decompose W using its eigenvalue decomposition W = V * diag(lambda) * V^(-1), then:

W^t = V * diag(lambda)^t * V^(-1)

Any eigenvalue lambda_i with magnitude greater than 1 will grow exponentially as t increases. Any eigenvalue with magnitude less than 1 will shrink exponentially toward zero.

During backpropagation through time (BPTT), the gradient of the loss with respect to h(0) involves the same repeated matrix multiplication:

dL/dh(0) = (W^T)^t * dL/dh(t)

This means:
- If the largest eigenvalue of W is greater than 1, gradients explode exponentially — the gradient norm grows without bound, causing NaN losses and divergent training.
- If the largest eigenvalue of W is less than 1, gradients vanish exponentially — the gradient signal becomes effectively zero after many time steps, preventing the network from learning long-range dependencies.

This is why vanilla RNNs struggle with sequences longer than 10-20 steps. The network cannot learn that an event at step 1 is relevant to a prediction at step 100, because the gradient signal connecting them has either exploded or vanished by the time it reaches step 1.

The problem is made worse by the use of nonlinearities. With tanh or sigmoid activations, the Jacobian of the hidden state with respect to the previous hidden state has singular values that are at most 1, which means vanishing gradients are far more common than exploding gradients in practice for standard RNNs with saturating nonlinearities.

## 10.11 Optimization for Long-Term Dependencies

### 10.11.1 Clipping Gradients

Gradient clipping is a simple and highly effective technique for dealing with the exploding gradient problem. The core idea is to impose a hard constraint on the norm of the gradient before applying the parameter update.

The algorithm is as follows:

1. Compute the gradient g as usual via backpropagation through time.
2. Compute the global gradient norm: ||g|| = sqrt(sum of squares of all gradient elements)
3. If ||g|| exceeds a threshold value v, rescale the gradient:

   g = (v / ||g||) * g

4. Apply the update using the rescaled gradient.

This ensures that the gradient step never exceeds a fixed size in parameter space, regardless of how large the raw gradients become. The direction of the gradient is preserved; only its magnitude is clipped.

A simpler variant clips each gradient element individually (clip by value rather than by norm), but clipping by norm is generally preferred because it preserves the direction of the gradient update.

Pseudocode for gradient clipping by norm:

    threshold = 5.0
    grad_norm = sqrt(sum(g_i^2 for all parameters i))
    if grad_norm > threshold:
        g = g * (threshold / grad_norm)

Typical threshold values range from 1.0 to 10.0 depending on the model and task. The threshold is treated as a hyperparameter and tuned on the validation set.

Gradient clipping does not solve the vanishing gradient problem — it only addresses the exploding gradient problem. The vanishing gradient problem requires architectural solutions such as:
- Long Short-Term Memory (LSTM) networks, which use gating mechanisms and a cell state that allows gradients to flow unchanged over long distances.
- Gated Recurrent Units (GRUs), which use a similar but simplified gating mechanism.
- Attention mechanisms, which create direct connections between distant time steps.

In practice, gradient clipping is used almost universally when training RNNs, even when using LSTMs or GRUs, as a safety measure against occasional gradient spikes.
