"""MPI workflow for the hotel reservation frontend."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class FrontendService(Service):
    """Drive a complete hotel reservation flow."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the frontend with a default test user."""
        super().__init__(service_id, store_step=store_step)
        self.user_id = 101

    async def step(self):
        """Search for hotels, fetch the profile, and submit a reservation."""
        await self.search_request()
        hotels = await self.mpi.recv()
        self.logger.info("Received response | " + format_log_kv(response=hotels))
        await self.profile_request()
        profile = await self.mpi.recv()
        self.logger.info("Received response | " + format_log_kv(response=profile))
        await self.reservation_request(hotels["hotels"], profile["user"])
        reservation = await self.mpi.recv()
        self.logger.info("Received response | " + format_log_kv(response=reservation))
        return reservation

    @mpi.exchange(send=True)
    def search_request(self):
        """Send a hotel search request for the demo travel plan."""
        return "SearchService", {
            "request_type": "search_hotels",
            "city": "Pisa",
            "nights": 2,
        }

    @mpi.exchange(send=True)
    def profile_request(self):
        """Request the traveller profile for the active user."""
        return "ProfileService", {
            "request_type": "get_profile",
            "user_id": self.user_id,
        }

    @mpi.exchange(send=True)
    def reservation_request(self, hotels: list[dict], user: dict):
        """Reserve the first available hotel for the requested user."""
        return "ReservationService", {
            "request_type": "create_reservation",
            "hotel": hotels[0],
            "user": user,
        }
