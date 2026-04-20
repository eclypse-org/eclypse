"""MPI workflow for hotel payment."""

import random as rnd

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class PaymentService(Service):
    """Charge a payment method for a reservation."""

    async def step(self):
        """Handle the next payment request emitted by the reservation flow."""
        await self.reservation_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def reservation_request(self, sender_id, body):
        """Charge the reservation and return a synthetic transaction id."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return sender_id, {
            "response_type": "payment_response",
            "reservation_id": body["reservation_id"],
            "transaction_id": f"txn-{rnd.randint(1000, 9999)}",
            "status": "confirmed",
        }
