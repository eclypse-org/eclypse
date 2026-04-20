"""REST endpoints for hotel payment."""

import random as rnd

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class PaymentService(RESTService):
    """Charge a payment method for a reservation."""

    @rest.endpoint("/pay", "POST")
    def pay(self, reservation_id: str, amount: float, **_):
        """Charge the reservation and return a synthetic transaction id."""
        self.logger.info(
            "Received request | "
            + format_log_kv(reservation_id=reservation_id, amount=amount)
        )
        return 200, {
            "reservation_id": reservation_id,
            "amount": amount,
            "transaction_id": f"txn-{rnd.randint(1000, 9999)}",
            "status": "confirmed",
        }
