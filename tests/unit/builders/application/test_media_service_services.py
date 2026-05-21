from __future__ import annotations

import pytest

from eclypse.builders.application.deathstarbench.media_service import (
    mpi_services as media_mpi,
)
from eclypse.builders.application.deathstarbench.media_service import (
    rest_services as media_rest,
)
from tests.unit.builders.application._service_test_helpers import (
    FakeRESTInterface,
    attach_service_logger,
    set_mpi,
)


@pytest.mark.asyncio
async def test_media_service_services(monkeypatch):
    compose = attach_service_logger(
        media_rest.ComposeReviewService("ComposeReviewService"),
    )
    unique_id = attach_service_logger(media_rest.UniqueIdService("UniqueIdService"))
    movie_id = attach_service_logger(media_rest.MovieIdService("MovieIdService"))
    text = attach_service_logger(media_rest.TextService("TextService"))
    rating = attach_service_logger(media_rest.RatingService("RatingService"))
    user = attach_service_logger(media_rest.UserService("UserService"))
    review_storage = attach_service_logger(
        media_rest.ReviewStorageService("ReviewStorageService"),
    )
    user_review = attach_service_logger(
        media_rest.UserReviewService("UserReviewService"),
    )
    movie_review = attach_service_logger(
        media_rest.MovieReviewService("MovieReviewService"),
    )
    movie_info = attach_service_logger(media_rest.MovieInfoService("MovieInfoService"))
    cast_info = attach_service_logger(media_rest.CastInfoService("CastInfoService"))
    plot = attach_service_logger(media_rest.PlotService("PlotService"))

    compose_rest = FakeRESTInterface(
        {
            ("POST", "UniqueIdService/compose"): {
                "review_id": 7001,
                "status": "stored",
            }
        }
    )
    monkeypatch.setattr(type(compose), "rest", property(lambda self: compose_rest))
    compose_response = await compose.step()
    assert compose_response.body["review_id"] == 7001

    unique_rest = FakeRESTInterface(
        {
            ("POST", "MovieIdService/compose"): {
                "review_id": 7001,
                "movie_id": "m1",
            }
        }
    )
    monkeypatch.setattr(type(unique_id), "rest", property(lambda self: unique_rest))
    code, body = await unique_id.compose(
        req_id=1,
        reply_to="ComposeReviewService",
        user_id=101,
        username="ada",
        movie_title="The Matrix",
        rating=5,
        text="Great movie",
    )
    assert code == 200
    assert unique_rest.calls[0][2]["review_id"] == 7001
    assert body["movie_id"] == "m1"

    code, body = movie_id.lookup(movie_title="The Matrix")
    assert code == 200
    assert body["movie_id"] == "m1"

    movie_id_rest = FakeRESTInterface(
        {("POST", "TextService/compose"): {"text": "Great movie", "rating": 5}}
    )
    monkeypatch.setattr(type(movie_id), "rest", property(lambda self: movie_id_rest))
    code, body = await movie_id.compose(
        movie_title="The Matrix",
        review_id=7001,
        req_id=1,
        rating=5,
        text="Great movie",
    )
    assert code == 200
    assert movie_id_rest.calls[0][2]["movie_id"] == "m1"
    assert body["rating"] == 5

    text_rest = FakeRESTInterface(
        {("POST", "RatingService/compose"): {"rating": 5, "text": "Great movie"}}
    )
    monkeypatch.setattr(type(text), "rest", property(lambda self: text_rest))
    code, body = await text.compose(text=" Great movie ", review_id=7001, req_id=1)
    assert code == 200
    assert text_rest.calls[0][2]["text"] == "Great movie"
    assert body["text"] == "Great movie"

    rating_rest = FakeRESTInterface(
        {("POST", "UserService/compose"): {"user": {"user_id": 101}}}
    )
    monkeypatch.setattr(type(rating), "rest", property(lambda self: rating_rest))
    code, body = await rating.compose(rating=8, review_id=7001, req_id=1)
    assert code == 200
    assert rating_rest.calls[0][2]["rating"] == 5
    assert body["user"]["user_id"] == 101

    code, body = user.user(user_id=101, username="ada")
    assert code == 200
    assert body["user"]["username"] == "ada"

    user_rest = FakeRESTInterface(
        {("POST", "ReviewStorageService/store"): {"status": "stored"}}
    )
    monkeypatch.setattr(type(user), "rest", property(lambda self: user_rest))
    code, body = await user.compose(
        user_id=101,
        username="ada",
        review_id=7001,
        req_id=1,
    )
    assert code == 200
    assert user_rest.calls[0][2]["user"]["username"] == "ada"
    assert body["status"] == "stored"

    review_storage.reviews[7001] = {"review_id": 7001, "movie_id": "m1"}
    code, body = review_storage.read_many(review_ids=[7001])
    assert code == 200
    assert body["reviews"][0]["review_id"] == 7001

    review_storage_rest = FakeRESTInterface(
        {
            ("POST", "UserReviewService/write"): {
                "status": "stored",
                "review_id": 7001,
            }
        }
    )
    monkeypatch.setattr(
        type(review_storage),
        "rest",
        property(lambda self: review_storage_rest),
    )
    code, body = await review_storage.store(
        review_id=7001,
        movie_id="m1",
        movie_title="The Matrix",
        rating=5,
        text="Great movie",
        user={"user_id": 101, "username": "ada"},
        reply_to="ComposeReviewService",
    )
    assert code == 201
    assert review_storage_rest.calls[0][1] == "UserReviewService/write"
    assert body["status"] == "stored"

    user_review_rest = FakeRESTInterface(
        {
            ("POST", "MovieReviewService/write"): {
                "status": "stored",
                "review_id": 7001,
            }
        }
    )
    monkeypatch.setattr(
        type(user_review),
        "rest",
        property(lambda self: user_review_rest),
    )
    code, body = await user_review.write(
        review={
            "review_id": 7001,
            "movie_id": "m1",
            "movie_title": "The Matrix",
            "user": {"user_id": 101, "username": "ada"},
        },
        reply_to="ComposeReviewService",
    )
    assert code == 200
    assert user_review_rest.calls[0][1] == "MovieReviewService/write"
    assert body["review_id"] == 7001

    code, body = movie_review.write(
        review={
            "review_id": 7001,
            "movie_id": "m1",
            "movie_title": "The Matrix",
        },
        reply_to="ComposeReviewService",
    )
    assert code == 201
    assert body["review_count"] == 1

    code, body = movie_review.read(movie_id="m1")
    assert code == 200
    assert body["reviews"][0]["review_id"] == 7001

    code, body = cast_info.cast(movie_id="m1")
    assert code == 200
    assert "Keanu Reeves" in body["cast"]

    code, body = plot.plot(movie_id="m1")
    assert code == 200
    assert body["plot"].startswith("A hacker")

    movie_info_rest = FakeRESTInterface(
        {
            ("GET", "CastInfoService/cast"): {
                "cast": ["Keanu Reeves", "Carrie-Anne Moss"]
            },
            (
                "GET",
                "PlotService/plot",
            ): {"plot": "A hacker discovers the world is a simulation."},
            (
                "GET",
                "MovieReviewService/read",
            ): {"reviews": [{"review_id": 7001}]},
        }
    )
    monkeypatch.setattr(
        type(movie_info), "rest", property(lambda self: movie_info_rest)
    )
    code, body = await movie_info.details(movie_id="m1", movie_title="The Matrix")
    assert code == 200
    assert len(body["cast"]) == 2
    assert body["reviews"][0]["review_id"] == 7001

    mpi_compose = attach_service_logger(
        media_mpi.ComposeReviewService("ComposeReviewService"),
    )
    mpi_unique_id = attach_service_logger(media_mpi.UniqueIdService("UniqueIdService"))
    mpi_movie_id = attach_service_logger(media_mpi.MovieIdService("MovieIdService"))
    mpi_text = attach_service_logger(media_mpi.TextService("TextService"))
    mpi_rating = attach_service_logger(media_mpi.RatingService("RatingService"))
    mpi_user = attach_service_logger(media_mpi.UserService("UserService"))
    mpi_review_storage = attach_service_logger(
        media_mpi.ReviewStorageService("ReviewStorageService"),
    )
    mpi_user_review = attach_service_logger(
        media_mpi.UserReviewService("UserReviewService"),
    )
    mpi_movie_review = attach_service_logger(
        media_mpi.MovieReviewService("MovieReviewService"),
    )
    mpi_movie_info = attach_service_logger(
        media_mpi.MovieInfoService("MovieInfoService")
    )
    mpi_cast = attach_service_logger(media_mpi.CastInfoService("CastInfoService"))
    mpi_plot = attach_service_logger(media_mpi.PlotService("PlotService"))

    compose_comm = set_mpi(
        mpi_compose,
        [{"response_type": "compose_review_response", "review_id": 7001}],
    )
    compose_response = await mpi_compose.step()
    assert compose_comm.sent[0][0] == "UniqueIdService"
    assert compose_response["review_id"] == 7001

    unique_comm = set_mpi(
        mpi_unique_id,
        [{"sender_id": "ComposeReviewService", "request_type": "compose_review"}],
    )
    await mpi_unique_id.step()
    assert unique_comm.sent[0][0] == "MovieIdService"
    assert unique_comm.sent[0][1]["review_id"] == 7001

    movie_id_comm = set_mpi(
        mpi_movie_id,
        [
            {
                "sender_id": "UniqueIdService",
                "request_type": "compose_review",
                "movie_title": "The Matrix",
            }
        ],
    )
    await mpi_movie_id.step()
    assert movie_id_comm.sent[0][0] == "TextService"
    assert movie_id_comm.sent[0][1]["movie_id"] == "m1"

    movie_id_lookup_comm = set_mpi(
        mpi_movie_id,
        [
            {
                "sender_id": "MovieInfoService",
                "request_type": "lookup_movie",
                "movie_title": "The Matrix",
            }
        ],
    )
    await mpi_movie_id.step()
    assert movie_id_lookup_comm.sent[0][0] == "MovieInfoService"
    assert movie_id_lookup_comm.sent[0][1] == {
        "response_type": "lookup_movie_response",
        "movie_id": "m1",
        "title": "The Matrix",
    }

    text_comm = set_mpi(
        mpi_text,
        [{"sender_id": "MovieIdService", "text": " Great movie "}],
    )
    await mpi_text.step()
    assert text_comm.sent[0][0] == "RatingService"
    assert text_comm.sent[0][1]["text"] == "Great movie"

    rating_comm = set_mpi(
        mpi_rating,
        [{"sender_id": "TextService", "rating": 8}],
    )
    await mpi_rating.step()
    assert rating_comm.sent[0][0] == "UserService"
    assert rating_comm.sent[0][1]["rating"] == 5

    user_comm = set_mpi(
        mpi_user,
        [{"sender_id": "RatingService", "user_id": 101, "username": "ada"}],
    )
    await mpi_user.step()
    assert user_comm.sent[0][0] == "ReviewStorageService"
    assert user_comm.sent[0][1]["user"]["username"] == "ada"

    storage_comm = set_mpi(
        mpi_review_storage,
        [
            {
                "sender_id": "UserService",
                "request_type": "compose_review",
                "review_id": 7001,
                "movie_id": "m1",
                "movie_title": "The Matrix",
                "rating": 5,
                "text": "Great movie",
                "user": {"user_id": 101, "username": "ada"},
                "reply_to": "ComposeReviewService",
            }
        ],
    )
    await mpi_review_storage.step()
    assert storage_comm.sent[0][0] == "UserReviewService"
    assert storage_comm.sent[0][1]["request_type"] == "write_user_review"

    storage_read_comm = set_mpi(
        mpi_review_storage,
        [
            {
                "sender_id": "MovieInfoService",
                "request_type": "read_reviews",
                "review_ids": [7001, 9999],
            }
        ],
    )
    await mpi_review_storage.step()
    assert storage_read_comm.sent[0][0] == "MovieInfoService"
    assert storage_read_comm.sent[0][1]["response_type"] == "read_reviews_response"
    assert storage_read_comm.sent[0][1]["reviews"] == [
        {
            "review_id": 7001,
            "movie_id": "m1",
            "movie_title": "The Matrix",
            "rating": 5,
            "text": "Great movie",
            "user": {"user_id": 101, "username": "ada"},
        }
    ]

    user_review_comm = set_mpi(
        mpi_user_review,
        [
            {
                "sender_id": "ReviewStorageService",
                "request_type": "write_user_review",
                "review": {
                    "review_id": 7001,
                    "movie_id": "m1",
                    "movie_title": "The Matrix",
                    "user": {"user_id": 101, "username": "ada"},
                },
                "reply_to": "ComposeReviewService",
            }
        ],
    )
    await mpi_user_review.step()
    assert user_review_comm.sent[0][0] == "MovieReviewService"

    movie_review_comm = set_mpi(
        mpi_movie_review,
        [
            {
                "sender_id": "UserReviewService",
                "request_type": "write_movie_review",
                "review": {
                    "review_id": 7001,
                    "movie_id": "m1",
                    "movie_title": "The Matrix",
                },
                "reply_to": "ComposeReviewService",
            }
        ],
    )
    await mpi_movie_review.step()
    assert movie_review_comm.sent[0][0] == "ComposeReviewService"
    assert movie_review_comm.sent[0][1]["review_count"] == 1

    movie_review_read_comm = set_mpi(
        mpi_movie_review,
        [
            {
                "sender_id": "MovieInfoService",
                "request_type": "read_movie_reviews",
                "movie_id": "m1",
            }
        ],
    )
    await mpi_movie_review.step()
    assert movie_review_read_comm.sent[0][0] == "MovieInfoService"
    assert movie_review_read_comm.sent[0][1] == {
        "response_type": "read_movie_reviews_response",
        "reviews": [
            {
                "review_id": 7001,
                "movie_id": "m1",
                "movie_title": "The Matrix",
            }
        ],
    }

    cast_comm = set_mpi(
        mpi_cast,
        [
            {
                "sender_id": "MovieInfoService",
                "request_type": "get_cast",
                "movie_id": "m1",
            }
        ],
    )
    await mpi_cast.step()
    assert cast_comm.sent[0][0] == "MovieInfoService"
    assert "Keanu Reeves" in cast_comm.sent[0][1]["cast"]

    plot_comm = set_mpi(
        mpi_plot,
        [
            {
                "sender_id": "MovieInfoService",
                "request_type": "get_plot",
                "movie_id": "m1",
            }
        ],
    )
    await mpi_plot.step()
    assert plot_comm.sent[0][0] == "MovieInfoService"
    assert plot_comm.sent[0][1]["plot"].startswith("A hacker")

    movie_info_comm = set_mpi(
        mpi_movie_info,
        [
            {
                "sender_id": "FrontendService",
                "movie_id": "m1",
                "movie_title": "The Matrix",
            },
            {"cast": ["Keanu Reeves", "Carrie-Anne Moss"]},
            {"plot": "A hacker discovers the world is a simulation."},
            {"reviews": [{"review_id": 7001}]},
        ],
    )
    movie_info_response = await mpi_movie_info.step()
    assert movie_info_comm.sent[0][0] == "CastInfoService"
    assert movie_info_comm.sent[1][0] == "PlotService"
    assert movie_info_comm.sent[2][0] == "MovieReviewService"
    assert movie_info_response["reviews"][0]["review_id"] == 7001
