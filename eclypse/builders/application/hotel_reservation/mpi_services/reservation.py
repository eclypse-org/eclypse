"""MPI workflow for reservation orchestration."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class ReservationService(Service):
    """Reserve a hotel room and coordinate payment."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the reservation orchestrator state."""
        super().__init__(service_id, store_step=store_step)
        self.pending_reservation: dict[str, object] = {}

    async def step(self):
        """Create a reservation and wait for the payment response."""
        await self.frontend_request()
        return await self.payment_request()

    @mpi.exchange(receive=True, send=True)
    def frontend_request(self, _sender_id, body):
        """Store the reservation context and trigger payment."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        self.pending_reservation = {
            "hotel": body["hotel"],
            "user": body["user"],
            "reservation_id": "rsv-2001",
        }
        return "PaymentService", {
            "request_type": "charge_card",
            "reservation_id": "rsv-2001",
            "amount": body["hotel"]["price"],
        }

    @mpi.exchange(receive=True, send=True)
    def payment_request(self, _sender_id, body):
        """Return the completed reservation once payment succeeds."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "FrontendService", {
            "response_type": "reservation_response",
            "reservation_id": self.pending_reservation["reservation_id"],
            "hotel_name": self.pending_reservation["hotel"]["name"],
            "transaction_id": body["transaction_id"],
            "status": body["status"],
        }
