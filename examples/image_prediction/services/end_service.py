from __future__ import annotations

import random as rnd
from typing import (
    TYPE_CHECKING,
    Optional,
)

if TYPE_CHECKING:
    from torchvision.datasets import MNIST

from eclypse.remote.service import Service

from .utils import load_data


class EndService(Service):
    def __init__(self, name: str):
        super().__init__(name, comm_interface="rest")
        self.data: Optional[MNIST] = None
        self.img_counter = 0
        self.correct = 0

    async def step(self):
        image_idx = rnd.randint(0, len(self.data) - 1)
        image, label = self.data[image_idx]

        image_pred = await self.rest.get("PredictorService/predict", image=image)
        image_pred = image_pred.body
        if image_pred["predictions"] == label:
            self.correct += 1
            self.logger.success(f"Prediction on image {image_idx} is correct.")
        else:
            self.logger.error(f"Prediction on image {image_idx} is incorrect.")
        self.img_counter += 1

    def on_deploy(self):
        self.logger.info(f"{self.id} deployed. Loading dataset...")
        self.data = load_data(train=False)
        self.logger.info(f"Dataset loaded successfully.")

    def on_undeploy(self):
        self.data = None
