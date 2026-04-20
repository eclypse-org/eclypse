"""REST workflow for image upload."""

from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class UploadService(Service):
    """Start the thumbnailing pipeline."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the uploader with a rolling image counter."""
        super().__init__(
            service_id,
            communication_interface="rest",
            store_step=store_step,
        )
        self.image_id = 0

    async def step(self):
        """Drive one image through the REST thumbnailing workflow."""
        self.image_id += 1
        transform_r = await self.rest.post(
            "TransformService/thumbnail",
            image_id=f"img-{self.image_id}",
            resolution=[1920, 1080],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="TransformService", body=transform_r.body)
        )
        storage_r = await self.rest.post(
            "StorageService/store",
            image_id=f"img-{self.image_id}",
            thumbnail=transform_r.body["thumbnail"],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="StorageService", body=storage_r.body)
        )
        notification_r = await self.rest.post(
            "NotificationService/notify",
            image_id=f"img-{self.image_id}",
            uri=storage_r.body["uri"],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="NotificationService", body=notification_r.body)
        )
        return notification_r
