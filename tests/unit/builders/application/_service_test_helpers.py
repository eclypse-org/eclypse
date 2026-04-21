from __future__ import annotations

from types import SimpleNamespace


class FakeRestResponse:
    def __init__(self, body):
        self.body = body
        self.data = body


class AwaitableResult:
    def __init__(self, result):
        self.result = result

    def __await__(self):
        async def _resolve():
            return self.result

        return _resolve().__await__()


class FakeRESTInterface:
    def __init__(self, handlers):
        self.handlers = handlers
        self.calls: list[tuple[str, str, dict[str, object]]] = []

    async def get(self, url: str, **kwargs):
        self.calls.append(("GET", url, kwargs))
        handler = self.handlers[("GET", url)]
        result = handler(**kwargs) if callable(handler) else handler
        return FakeRestResponse(result)

    async def post(self, url: str, **kwargs):
        self.calls.append(("POST", url, kwargs))
        handler = self.handlers[("POST", url)]
        result = handler(**kwargs) if callable(handler) else handler
        return FakeRestResponse(result)


class FakeMPIInterface:
    def __init__(self, messages):
        self.messages = list(messages)
        self.sent: list[tuple[str, dict[str, object]]] = []

    async def recv(self):
        return self.messages.pop(0)

    def send(self, recipient_id: str, body: dict[str, object]):
        self.sent.append((recipient_id, body))
        return AwaitableResult((recipient_id, body))


def attach_service_logger(service):
    service.attach_node(
        SimpleNamespace(
            _logger=SimpleNamespace(
                bind=lambda **_: SimpleNamespace(info=lambda *_args: None)
            )
        )
    )
    return service


def set_mpi(service, messages):
    service._comm = FakeMPIInterface(messages)
    return service._comm
