import torchvision
from torchvision.datasets import MNIST

from eclypse.utils.constants import DEFAULT_SIM_PATH

BASE_PATH = DEFAULT_SIM_PATH / "image_prediction"
RUNTIME_PATH = BASE_PATH / "runtime"
LEARNING_RATE = 0.001
EPOCHS = 100
BATCH_SIZE = 1024
TICKS = 600
TICK_EVERY_MS = 1000


def load_data(train: bool = True) -> MNIST:
    """Loads the MNIST dataset from torchvision datasets."""
    return MNIST(
        BASE_PATH / "dataset",
        download=True,
        train=train,
        transform=torchvision.transforms.Compose(
            [
                torchvision.transforms.ToTensor(),
                torchvision.transforms.Normalize((0.1307,), (0.3081,)),
            ]
        ),
    )
