import threading
from typing import (
    Any,
    List,
)

import torch
from torch.utils.data import DataLoader

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService

from .model import MNISTModel
from .utils import (
    BATCH_SIZE,
    EPOCHS,
    LEARNING_RATE,
    load_data,
)


class TrainerService(RESTService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.train_thread: threading.Thread = None
        self.data = None
        self.model: torch.nn.Module = None
        self.model_queue: List[Any] = None
        self.epoch: int = 0

    @rest.endpoint("/get_model", method="GET")
    def get_model(self):
        if len(self.model_queue) > 0:
            return 200, {
                "model": self.model_queue.pop(0),
            }
        return 404, {"error": "No model available."}

    def train(self):
        self.logger.info("Training started.")
        loader = DataLoader(
            self.data,
            batch_size=BATCH_SIZE,
            shuffle=True,
        )
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(self.model.parameters(), lr=LEARNING_RATE)
        self.model.train()
        self.model.to("cuda")
        for self.epoch in range(EPOCHS):
            for x, y in loader:
                x, y = x.to("cuda"), y.to("cuda")
                optimizer.zero_grad()
                outputs = self.model(x)
                loss = criterion(outputs, y)
                loss.backward()
                optimizer.step()
            self.model_queue.append(
                {k: v.detach().cpu() for k, v in self.model.state_dict().items()}
            )

    def on_deploy(self):
        self.logger.info(f"{self.id} deployed. Loading model...")
        self.model_queue = []
        self.model = MNISTModel()
        self.data = load_data()

        self.train_thread = threading.Thread(target=self.train, daemon=True)
        self.train_thread.start()

    def on_undeploy(self):
        self.model_queue = None
        self.train_thread = None
        self.data = None
        self.model = None

    @property
    def is_training(self):
        return self.train_thread.is_alive() if self.train_thread else False
