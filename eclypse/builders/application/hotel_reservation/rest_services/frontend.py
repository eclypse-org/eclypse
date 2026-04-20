"""REST workflow for the hotel reservation frontend."""

from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class FrontendService(Service):
    """Drive a complete hotel reservation flow."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the frontend with a default test user."""
        super().__init__(
            service_id,
            communication_interface="rest",
            store_step=store_step,
        )
        self.user_id = 101

    async def step(self):
        """Search for hotels, fetch the profile, and submit a reservation."""
        hotels_r = await self.rest.get("SearchService/search", city="Pisa", nights=2)
        self.logger.info(
            "Received response | "
            + format_log_kv(source="SearchService", body=hotels_r.body)
        )
        profile_r = await self.rest.get("ProfileService/profile", user_id=self.user_id)
        self.logger.info(
            "Received response | "
            + format_log_kv(source="ProfileService", body=profile_r.body)
        )
        reservation_r = await self.rest.post(
            "ReservationService/reserve",
            hotel=hotels_r.body["hotels"][0],
            user=profile_r.body["user"],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="ReservationService", body=reservation_r.body)
        )
        return reservation_r
