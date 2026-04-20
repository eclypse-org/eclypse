"""REST endpoints for reservation orchestration."""

from eclypse.remote.communication import rest
from eclypse.remote.communication.rest import HTTPStatusCode
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class ReservationService(RESTService):
    """Reserve a hotel room and coordinate payment."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the reservation service with a stable booking id."""
        super().__init__(service_id, store_step=store_step)
        self.reservation_id = "rsv-2001"

    @rest.endpoint("/reserve", "POST")
    async def reserve(self, hotel: dict, user: dict, **_):
        """Create a reservation and charge the selected hotel stay."""
        self.logger.info("Received request | " + format_log_kv(hotel=hotel, user=user))
        payment_r = await self.rest.post(
            "PaymentService/pay",
            reservation_id=self.reservation_id,
            amount=hotel["price"],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="PaymentService", body=payment_r.body)
        )
        return HTTPStatusCode.CREATED, {
            "reservation_id": self.reservation_id,
            "hotel_name": hotel["name"],
            "guest_name": user["name"],
            "transaction_id": payment_r.body["transaction_id"],
            "status": payment_r.body["status"],
        }
