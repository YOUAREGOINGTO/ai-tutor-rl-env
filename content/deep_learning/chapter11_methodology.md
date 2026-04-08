# Chapter 11: Practical Methodology
# Source: "Deep Learning" by Ian Goodfellow, Yoshua Bengio, Aaron Courville

Successfully applying deep learning techniques requires more than just a good knowledge of what algorithms exist and the principles that explain how they work. A good machine learning practitioner also needs to know how to choose an algorithm for a particular application and how to monitor and respond to feedback obtained from experiments in order to improve a machine learning system. During day to day development of machine learning systems, practitioners need to decide whether to gather more data, increase or decrease model capacity, add or remove regularizing features, improve the optimization of a model, improve approximate inference in a model, or debug the software implementation of the model. All of these operations are at the very least time-consuming to try out, so it is important to be able to determine the right course of action rather than blindly guessing.

We recommend the following practical design process:

- Determine your goals — what error metric to use, and your target value for this error metric. These goals and error metrics should be driven by the problem that the application is intended to solve.
- Establish a working end-to-end pipeline as soon as possible, including the estimation of the appropriate performance metrics.
- Instrument the system well to determine bottlenecks in performance. Diagnose which components are performing worse than expected and whether it is due to overfitting, underfitting, or a defect in the data or software.
- Repeatedly make incremental changes such as gathering new data, adjusting hyperparameters, or changing algorithms, based on specific findings from your instrumentation.

## 11.1 Performance Metrics

Determining your goals, in terms of which error metric to use, is a necessary first step because your error metric will guide all of your future actions. You should also have an idea of what level of performance you desire.

Keep in mind that for most applications, it is impossible to achieve absolute zero error. The Bayes error defines the minimum error rate that you can hope to achieve, even if you have infinite training data and can recover the true probability distribution. This is because your input features may not contain complete information about the output variable, or because the system might be intrinsically stochastic.

Sometimes it is much more costly to make one kind of a mistake than another. Rather than measuring the error rate of a spam classifier, we may wish to measure some form of total cost, where the cost of blocking legitimate messages is higher than the cost of allowing spam messages.

Precision is the fraction of detections reported by the model that were correct, while recall is the fraction of true events that were detected. When using precision and recall, it is common to plot a PR curve, with precision on the y-axis and recall on the x-axis. We can convert precision p and recall r into an F-score given by:

F = 2pr / (p + r)

Coverage is the fraction of examples for which the machine learning system is able to produce a response. It is possible to trade coverage for accuracy.

## 11.2 Default Baseline Models

After choosing performance metrics and goals, the next step in any practical application is to establish a reasonable end-to-end system as soon as possible.

- If the input has known topological structure (e.g., images), use a convolutional network.
- If your input or output is a sequence, use a gated recurrent net (LSTM or GRU).
- A reasonable choice of optimization algorithm is SGD with momentum with a decaying learning rate. Another very reasonable alternative is Adam.
- Unless your training set contains tens of millions of examples or more, include some mild forms of regularization from the start. Early stopping should be used almost universally. Dropout is an excellent regularizer.

## 11.3 Determining Whether to Gather More Data

After the first end-to-end system is established, it is time to measure the performance of the algorithm and determine how to improve it. Many machine learning novices are tempted to make improvements by trying out many different algorithms. However, it is often much better to gather more data than to improve the learning algorithm.

If performance on the training set is poor, the learning algorithm is not using the training data that is already available, so there is no reason to gather more data. Instead, try increasing the size of the model by adding more layers or adding more hidden units to each layer.

If the performance on the training set is acceptable, then measure the performance on a test set. If test set performance is much worse than training set performance, then gathering more data is one of the most effective solutions.

## 11.4 Selecting Hyperparameters

Most deep learning algorithms come with many hyperparameters that control many aspects of the algorithm's behavior. There are two basic approaches to choosing these hyperparameters: choosing them manually and choosing them automatically.

### 11.4.1 Manual Hyperparameter Tuning

The goal of manual hyperparameter search is usually to find the lowest generalization error subject to some runtime and memory budget.

The generalization error typically follows a U-shaped curve when plotted as a function of one of the hyperparameters. At one extreme, the hyperparameter value corresponds to low capacity, and generalization error is high because training error is high — the underfitting regime. At the other extreme, the hyperparameter value corresponds to high capacity, and the generalization error is high because the gap between training and test error is high.

The learning rate is perhaps the most important hyperparameter. If you have time to tune only one hyperparameter, tune the learning rate. When the learning rate is too large, gradient descent can inadvertently increase rather than decrease the training error. When the learning rate is too small, training is not only slower, but may become permanently stuck with a high training error.

Effect of hyperparameters on model capacity:

| Hyperparameter        | Increases capacity when... | Reason |
|-----------------------|---------------------------|--------|
| Number of hidden units | increased | Increases representational capacity |
| Learning rate | tuned optimally | Improper learning rate causes optimization failure |
| Weight decay coefficient | decreased | Frees parameters to become larger |
| Dropout rate | decreased | Units cooperate more to fit training set |

### 11.4.2 Automatic Hyperparameter Optimization Algorithms

The ideal learning algorithm just takes a dataset and outputs a function, without requiring hand-tuning of hyperparameters. Hyperparameter optimization algorithms wrap a learning algorithm and choose its hyperparameters automatically.

### 11.4.3 Grid Search

When there are three or fewer hyperparameters, the common practice is to perform grid search. For each hyperparameter, the user selects a small finite set of values to explore. The grid search algorithm then trains a model for every joint specification of hyperparameter values in the Cartesian product of the set of values.

Grid search usually involves picking values approximately on a logarithmic scale, e.g., a learning rate taken from the set {0.1, 0.01, 0.001, 0.0001, 0.00001}.

The obvious problem with grid search is that its computational cost grows exponentially with the number of hyperparameters. If there are m hyperparameters, each taking at most n values, then the number of trials required grows as O(n^m).

### 11.4.4 Random Search

Random search is as simple to program, more convenient to use, and converges much faster to good values of the hyperparameters than grid search (Bergstra and Bengio, 2012).

A random search proceeds by defining a marginal distribution for each hyperparameter and randomly sampling joint hyperparameter configurations. For example:

log_learning_rate ~ Uniform(-1, -5)
learning_rate = 10^(log_learning_rate)

Random search can be exponentially more efficient than grid search when there are several hyperparameters that do not strongly affect the performance measure, because there are no wasted experimental runs.

### 11.4.5 Model-Based Hyperparameter Optimization

The search for good hyperparameters can be cast as an optimization problem. Most model-based algorithms use a Bayesian regression model to estimate both the expected value of the validation set error for each hyperparameter and the uncertainty around this expectation. Optimization involves a tradeoff between exploration and exploitation. Contemporary approaches include Spearmint, TPE, and SMAC.

## 11.5 Debugging Strategies

When a machine learning system performs poorly, it is usually difficult to tell whether the poor performance is intrinsic to the algorithm itself or whether there is a bug in the implementation.

Some important debugging tests include:

- **Visualize the model in action**: Directly observing the machine learning model performing its task helps determine whether quantitative performance numbers seem reasonable.
- **Visualize the worst mistakes**: By viewing the training set examples that are hardest to model correctly, one can often discover problems with the way the data has been preprocessed or labeled.
- **Fit a tiny dataset**: If you cannot train a classifier to correctly label a single example, there is likely a software defect preventing successful optimization.
- **Compare back-propagated derivatives to numerical derivatives**: If you are implementing your own gradient computation, compare against finite difference approximations to verify correctness.
- **Monitor activations and gradient histograms**: Check that activations and gradients do not saturate or explode during training.
