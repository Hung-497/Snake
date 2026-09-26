# Keep DQN headless with separate training and evaluation artifacts

DQN is an optional, CPU-only headless Bot Mode in its first version. Its PyTorch dependency stays outside normal app startup and default Bot Experiments; a user explicitly selects DQN and its evaluation model. Training saves a full resumable checkpoint separately from the smaller evaluation model, so evaluation cannot accidentally change learning state and a later run can resume meaningfully.

## Considered Options

- Make PyTorch required for the whole app and use one saved file for both training and evaluation.
- Keep DQN headless and optional, with distinct artifacts for resuming training and evaluating a fixed model.

The second option keeps ordinary play usable without PyTorch and gives each saved artifact a clear purpose.

## Consequences

- A full checkpoint retains network and target-network weights, optimizer state, epsilon and game count, replay buffer, and random state. Resume restores its board and learning settings and writes a new run's artifacts without changing the source checkpoint.
- Each completed training run exports its final network as an evaluation model with identifying metadata. Evaluation reads an explicitly named model and writes only an experiment report.
- Training updates its own checkpoint at a documented game interval and on successful completion. Artifact formats need versioning and validation before training or evaluation begins.
- Version 2 artifacts explicitly record the CPU device, `9 → 64 → 64 → 3`
  ReLU network, Adam optimizer and learning rate, uniform replay capacity,
  batch-sized warm-up, and target-network update interval. The loader retains
  version 1 compatibility so existing trained runs remain usable.
