from collections import defaultdict

import numpy as np
from networkx.classes.reportviews import EdgeView


def exponential_decay(init, target, N, decay_rate=None):

    # Compute decay rate if not provided
    if decay_rate is None:
        decay_rate = np.log(init / target) / N

    # Calculate values for each step n
    steps = np.arange(0, N + 1)
    values = target + (init - target) * np.exp(-decay_rate * steps)

    return values


class DegradePolicy:

    def __init__(self, epochs: int):
        self.epochs = epochs
        self.starting_decay_epoch = int(0.75 * epochs)
        self.init_latency = defaultdict(lambda: None)
        self.values = defaultdict(lambda: None)
        self.i = 0
        self.target_latency = 1000

    def __call__(self, edges: EdgeView):
        if self.i > self.starting_decay_epoch:
            for s, d, resources in edges.data():
                if self.init_latency[(s, d)] is None:
                    self.init_latency[(s, d)] = resources["latency"]
                    self.values[(s, d)] = exponential_decay(
                        self.init_latency[(s, d)],
                        self.target_latency,
                        self.epochs - self.starting_decay_epoch,
                        decay_rate=0.005,
                    )

                else:
                    resources["latency"] = self.values[(s, d)][
                        self.i - self.starting_decay_epoch
                    ]
        self.i += 1
