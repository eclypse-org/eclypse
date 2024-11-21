import asyncio
import time

from eclypse_core.remote.service import Service


class EchoService(Service):
    def __init__(self, id: str):
        super().__init__(id, store_step=True)
        self.i = 0

    async def step(self):
        message = {"message": f"Hello from {self.id}!"}

        neigh = await self.mpi.get_neighbors()
        expected_wait_unicast = 0
        t_init_unicast = time.time()
        for n in neigh:
            req = await self.mpi.send(n, message)
            expected_wait_unicast += req.route.cost(message) if req.route else 0
        t_final_unicast = time.time()
        t_unicast = t_final_unicast - t_init_unicast
        self.logger.info(
            f"Service {self.id}, {self.i} -  Unicasts in: {t_unicast}, expected = {expected_wait_unicast}"
        )
        t_init_broadcast = time.time()
        req = await self.mpi.send(neigh, message)
        expected_wait_broadcast = max(
            [r.cost(message) for r in req.routes if r], default=0
        )
        t_final_broadcast = time.time()
        t_broadcast = t_final_broadcast - t_init_broadcast
        self.logger.info(
            f"Service {self.id}, {self.i} - Broadcasts in: {t_broadcast}, expected = {expected_wait_broadcast}"
        )
        self.i += 1
        await asyncio.sleep(1)
        return (
            self.i,
            t_unicast,
            expected_wait_unicast,
            t_broadcast,
            expected_wait_broadcast,
        )
