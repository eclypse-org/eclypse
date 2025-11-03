import time

import numpy as np
import torch

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService

from .model import MNISTModel
from .utils import (
    EPOCHS,
    STEP_EVERY_MS,
    STEPS,
)


class PredictorService(RESTService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = None
        self.img_counter = 0
        self.last_model_time = None
        self.new_model = False
        self.new_model_signal = True

    @rest.endpoint("/predict", method="GET")
    async def predict(self, image: np.ndarray):
        last_time, req_time = self.last_model_time, time.time()
        if self.last_model_time is None or (req_time - self.last_model_time) > (
            STEPS / EPOCHS
        ) * (STEP_EVERY_MS / 1000):
            self.last_model_time = req_time
            self.new_model = await self.poll_model()
            if not self.new_model:
                self.last_model_time = last_time
            else:
                self.new_model_signal = True

        self.model.eval()
        image = np.expand_dims(image, axis=0)
        image = torch.tensor(image)
        with torch.no_grad():
            prediction = torch.argmax(self.model(image), dim=-1)

        self.img_counter += 1
        return 200, {"predictions": prediction}

    async def poll_model(self):
        req = await self.rest.get("TrainerService/get_model")
        if req.status_code == 200:
            self.model.load_state_dict(req.body["model"])
            self.logger.warning("Model updated.")
            return True
        return False

    def on_deploy(self):
        self.logger.info(f"{self.id} deployed. Loading model...")
        self.model = MNISTModel()
        self.logger.info(f"Model loaded successfully.")

    def on_undeploy(self):
        self.model = None
