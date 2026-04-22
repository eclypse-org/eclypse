from __future__ import annotations

import pytest

from eclypse.builders.application.thumbnailer import mpi_services as thumb_mpi
from eclypse.builders.application.thumbnailer import rest_services as thumb_rest
from tests.unit.builders.application._service_test_helpers import (
    FakeRESTInterface,
    attach_service_logger,
    set_mpi,
)


@pytest.mark.asyncio
async def test_thumbnailer_services(monkeypatch):
    transform = attach_service_logger(thumb_rest.TransformService("TransformService"))
    storage = attach_service_logger(thumb_rest.StorageService("StorageService"))
    notification = attach_service_logger(
        thumb_rest.NotificationService("NotificationService")
    )
    upload = attach_service_logger(thumb_rest.UploadService("UploadService"))

    code, body = transform.thumbnail("img-1", [1920, 1080])
    assert code == 200
    assert body["thumbnail"]["width"] == 320

    code, body = storage.store(
        "img-1",
        {"width": 320, "height": 180, "format": "jpeg"},
    )
    assert code == 200
    assert body["uri"].endswith("/img-1.jpg")

    code, body = notification.notify("img-1", "s3://thumbs/img-1.jpg")
    assert code == 200
    assert body["status"] == "stored"

    upload_rest = FakeRESTInterface(
        {
            ("POST", "TransformService/thumbnail"): {
                "thumbnail": {"width": 320, "height": 180, "format": "jpeg"}
            },
            ("POST", "StorageService/store"): {"uri": "s3://thumbs/img-1.jpg"},
            ("POST", "NotificationService/notify"): {"status": "stored"},
        }
    )
    monkeypatch.setattr(type(upload), "rest", property(lambda self: upload_rest))
    response = await upload.step()
    assert response.body["status"] == "stored"

    mpi_transform = attach_service_logger(
        thumb_mpi.TransformService("TransformService")
    )
    mpi_storage = attach_service_logger(thumb_mpi.StorageService("StorageService"))
    mpi_notification = attach_service_logger(
        thumb_mpi.NotificationService("NotificationService")
    )
    mpi_upload = attach_service_logger(thumb_mpi.UploadService("UploadService"))

    transform_comm = set_mpi(
        mpi_transform,
        [
            {
                "sender_id": "UploadService",
                "request_type": "create_thumbnail",
                "image_id": "img-1",
                "resolution": [1920, 1080],
            }
        ],
    )
    await mpi_transform.step()
    assert transform_comm.sent[0][1]["thumbnail"]["format"] == "jpeg"

    storage_comm = set_mpi(
        mpi_storage,
        [
            {
                "sender_id": "TransformService",
                "request_type": "store_thumbnail",
                "image_id": "img-1",
                "thumbnail": {"width": 320, "height": 180, "format": "jpeg"},
            }
        ],
    )
    await mpi_storage.step()
    assert storage_comm.sent[0][1]["uri"].endswith("/img-1.jpg")

    notification_comm = set_mpi(
        mpi_notification,
        [
            {
                "sender_id": "StorageService",
                "request_type": "notify_upload",
                "image_id": "img-1",
                "uri": "s3://thumbs/img-1.jpg",
            }
        ],
    )
    await mpi_notification.step()
    assert notification_comm.sent[0][1]["status"] == "stored"

    upload_comm = set_mpi(
        mpi_upload,
        [{"status": "stored", "uri": "s3://thumbs/img-1.jpg"}],
    )
    response = await mpi_upload.step()
    assert upload_comm.sent[0][0] == "TransformService"
    assert response["status"] == "stored"
