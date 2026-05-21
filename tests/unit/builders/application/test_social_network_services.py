from __future__ import annotations

import pytest

from eclypse.builders.application.deathstarbench.social_network import (
    mpi_services as social_mpi,
)
from eclypse.builders.application.deathstarbench.social_network import (
    rest_services as social_rest,
)
from tests.unit.builders.application._service_test_helpers import (
    FakeRESTInterface,
    attach_service_logger,
    set_mpi,
)


@pytest.mark.asyncio
async def test_social_network_services(monkeypatch):
    compose = attach_service_logger(
        social_rest.ComposePostService("ComposePostService"),
    )
    unique_id = attach_service_logger(social_rest.UniqueIdService("UniqueIdService"))
    text = attach_service_logger(social_rest.TextService("TextService"))
    mentions = attach_service_logger(
        social_rest.UserMentionService("UserMentionService"),
    )
    urls = attach_service_logger(
        social_rest.UrlShortenService("UrlShortenService"),
    )
    media = attach_service_logger(social_rest.MediaService("MediaService"))
    user = attach_service_logger(social_rest.UserService("UserService"))
    post_storage = attach_service_logger(
        social_rest.PostStorageService("PostStorageService"),
    )
    user_timeline = attach_service_logger(
        social_rest.UserTimelineService("UserTimelineService"),
    )
    home_timeline = attach_service_logger(
        social_rest.HomeTimelineService("HomeTimelineService"),
    )
    social_graph = attach_service_logger(
        social_rest.SocialGraphService("SocialGraphService"),
    )

    compose_rest = FakeRESTInterface(
        {
            ("POST", "UniqueIdService/compose"): {
                "post_id": 5001,
                "status": "posted",
                "follower_count": 2,
            }
        }
    )
    monkeypatch.setattr(type(compose), "rest", property(lambda self: compose_rest))
    compose_response = await compose.step()
    assert compose_response.body["post_id"] == 5001

    unique_rest = FakeRESTInterface(
        {("POST", "TextService/compose"): {"post_id": 5001, "status": "posted"}}
    )
    monkeypatch.setattr(type(unique_id), "rest", property(lambda self: unique_rest))
    code, body = await unique_id.compose(
        req_id=1,
        reply_to="ComposePostService",
        username="alice",
        user_id=101,
        text="Hello @bob check https://example.com",
        media_ids=[11],
        media_types=["image"],
        post_type="POST",
    )
    assert code == 200
    assert unique_rest.calls[0][1] == "TextService/compose"
    assert unique_rest.calls[0][2]["post_id"] == 5001
    assert body["status"] == "posted"

    text_rest = FakeRESTInterface(
        {
            ("POST", "UserMentionService/compose"): {
                "user_mentions": [{"user_id": 201, "username": "bob"}]
            }
        }
    )
    monkeypatch.setattr(type(text), "rest", property(lambda self: text_rest))
    code, body = await text.compose(
        text="Hello @bob check https://example.com",
        post_id=5001,
        req_id=1,
    )
    assert code == 200
    assert text_rest.calls[0][2]["mentions"] == ["bob"]
    assert text_rest.calls[0][2]["urls"] == ["https://example.com"]
    assert body["user_mentions"][0]["username"] == "bob"

    mention_rest = FakeRESTInterface(
        {
            ("POST", "UrlShortenService/compose"): {
                "shortened_urls": [{"shortened_url": "https://t.ec/1"}]
            }
        }
    )
    monkeypatch.setattr(type(mentions), "rest", property(lambda self: mention_rest))
    code, body = await mentions.compose(
        mentions=["bob"],
        post_id=5001,
        req_id=1,
    )
    assert code == 200
    assert mention_rest.calls[0][2]["user_mentions"][0]["user_id"] == 201
    assert body["shortened_urls"][0]["shortened_url"] == "https://t.ec/1"

    url_rest = FakeRESTInterface(
        {
            ("POST", "MediaService/compose"): {
                "media": [{"media_id": 11, "media_type": "image"}]
            }
        }
    )
    monkeypatch.setattr(type(urls), "rest", property(lambda self: url_rest))
    code, body = await urls.compose(
        urls=["https://example.com"],
        post_id=5001,
        req_id=1,
    )
    assert code == 200
    assert url_rest.calls[0][2]["shortened_urls"][0]["expanded_url"] == (
        "https://example.com"
    )
    assert body["media"][0]["media_type"] == "image"

    media_rest = FakeRESTInterface(
        {("POST", "UserService/compose"): {"creator": {"user_id": 101}}}
    )
    monkeypatch.setattr(type(media), "rest", property(lambda self: media_rest))
    code, body = await media.compose(
        media_ids=[11],
        media_types=["image"],
        post_id=5001,
        req_id=1,
    )
    assert code == 200
    assert media_rest.calls[0][2]["media"][0]["media_id"] == 11
    assert body["creator"]["user_id"] == 101

    code, body = user.creator(user_id=101, username="alice")
    assert code == 200
    assert body["creator"]["username"] == "alice"

    user_rest = FakeRESTInterface(
        {("POST", "PostStorageService/store"): {"status": "posted"}}
    )
    monkeypatch.setattr(type(user), "rest", property(lambda self: user_rest))
    code, body = await user.compose(
        user_id=101,
        username="alice",
        post_id=5001,
        req_id=1,
    )
    assert code == 200
    assert user_rest.calls[0][2]["creator"]["username"] == "alice"
    assert body["status"] == "posted"

    post_storage.posts[5001] = {"post_id": 5001, "text": "Hello"}
    code, body = post_storage.read_many(post_ids=[5001])
    assert code == 200
    assert body["posts"][0]["post_id"] == 5001

    post_storage_rest = FakeRESTInterface(
        {
            ("POST", "UserTimelineService/write"): {
                "status": "posted",
                "post_id": 5001,
            }
        }
    )
    monkeypatch.setattr(
        type(post_storage),
        "rest",
        property(lambda self: post_storage_rest),
    )
    code, body = await post_storage.store(
        post_id=5001,
        creator={"user_id": 101, "username": "alice"},
        text="Hello",
        user_mentions=[],
        media=[],
        shortened_urls=[],
        reply_to="ComposePostService",
    )
    assert code == 201
    assert post_storage_rest.calls[0][1] == "UserTimelineService/write"
    assert body["status"] == "posted"

    user_timeline.timelines[101] = [5001]
    user_timeline_read_rest = FakeRESTInterface(
        {
            ("GET", "PostStorageService/read_many"): {
                "posts": [{"post_id": 5001, "text": "Hello"}]
            }
        }
    )
    monkeypatch.setattr(
        type(user_timeline),
        "rest",
        property(lambda self: user_timeline_read_rest),
    )
    code, body = await user_timeline.read(user_id=101)
    assert code == 200
    assert body["posts"][0]["post_id"] == 5001

    user_timeline_write_rest = FakeRESTInterface(
        {("POST", "HomeTimelineService/write"): {"status": "posted", "post_id": 5001}}
    )
    monkeypatch.setattr(
        type(user_timeline),
        "rest",
        property(lambda self: user_timeline_write_rest),
    )
    code, body = await user_timeline.write(
        creator={"user_id": 101, "username": "alice"},
        post_id=5001,
        post={"post_id": 5001, "text": "Hello"},
        reply_to="ComposePostService",
    )
    assert code == 200
    assert user_timeline_write_rest.calls[0][1] == "HomeTimelineService/write"
    assert body["status"] == "posted"

    home_timeline.timelines[101] = [5001]
    home_read_rest = FakeRESTInterface(
        {
            ("GET", "PostStorageService/read_many"): {
                "posts": [{"post_id": 5001, "text": "Hello"}]
            }
        }
    )
    monkeypatch.setattr(
        type(home_timeline),
        "rest",
        property(lambda self: home_read_rest),
    )
    code, body = await home_timeline.read(user_id=101)
    assert code == 200
    assert body["posts"][0]["text"] == "Hello"

    home_write_rest = FakeRESTInterface(
        {("GET", "SocialGraphService/followers"): {"followers": [202, 303]}}
    )
    monkeypatch.setattr(
        type(home_timeline),
        "rest",
        property(lambda self: home_write_rest),
    )
    code, body = await home_timeline.write(
        creator={"user_id": 101, "username": "alice"},
        post_id=5001,
        post={"post_id": 5001, "text": "Hello"},
        reply_to="ComposePostService",
    )
    assert code == 201
    assert body["follower_count"] == 2
    assert 202 in body["delivered_to"]

    code, body = social_graph.followers(user_id=101)
    assert code == 200
    assert body["followers"] == [202, 303]

    code, body = social_graph.follow(user_id=101, follower_id=404)
    assert code == 200
    assert 404 in body["followers"]

    code, duplicate_body = social_graph.follow(user_id=101, follower_id=404)
    assert code == 200
    assert duplicate_body["followers"].count(404) == 1

    mpi_compose = attach_service_logger(
        social_mpi.ComposePostService("ComposePostService"),
    )
    mpi_unique_id = attach_service_logger(social_mpi.UniqueIdService("UniqueIdService"))
    mpi_text = attach_service_logger(social_mpi.TextService("TextService"))
    mpi_mentions = attach_service_logger(
        social_mpi.UserMentionService("UserMentionService"),
    )
    mpi_urls = attach_service_logger(
        social_mpi.UrlShortenService("UrlShortenService"),
    )
    mpi_media = attach_service_logger(social_mpi.MediaService("MediaService"))
    mpi_user = attach_service_logger(social_mpi.UserService("UserService"))
    mpi_post_storage = attach_service_logger(
        social_mpi.PostStorageService("PostStorageService"),
    )
    mpi_user_timeline = attach_service_logger(
        social_mpi.UserTimelineService("UserTimelineService"),
    )
    mpi_home_timeline = attach_service_logger(
        social_mpi.HomeTimelineService("HomeTimelineService"),
    )
    mpi_social_graph = attach_service_logger(
        social_mpi.SocialGraphService("SocialGraphService"),
    )

    compose_comm = set_mpi(
        mpi_compose,
        [{"response_type": "compose_post_response", "post_id": 5001}],
    )
    compose_response = await mpi_compose.step()
    assert compose_comm.sent[0][0] == "UniqueIdService"
    assert compose_response["post_id"] == 5001

    unique_comm = set_mpi(
        mpi_unique_id,
        [
            {
                "sender_id": "ComposePostService",
                "request_type": "compose_post",
                "reply_to": "ComposePostService",
                "text": "Hello @bob check https://example.com",
                "media_ids": [11],
                "media_types": ["image"],
            }
        ],
    )
    await mpi_unique_id.step()
    assert unique_comm.sent[0][0] == "TextService"
    assert unique_comm.sent[0][1]["post_id"] == 5001

    text_comm = set_mpi(
        mpi_text,
        [
            {
                "sender_id": "UniqueIdService",
                "text": "Hello @bob check https://example.com",
            }
        ],
    )
    await mpi_text.step()
    assert text_comm.sent[0][0] == "UserMentionService"
    assert text_comm.sent[0][1]["mentions"] == ["bob"]

    mention_comm = set_mpi(
        mpi_mentions,
        [{"sender_id": "TextService", "mentions": ["bob"]}],
    )
    await mpi_mentions.step()
    assert mention_comm.sent[0][0] == "UrlShortenService"
    assert mention_comm.sent[0][1]["user_mentions"][0]["username"] == "bob"

    url_comm = set_mpi(
        mpi_urls,
        [{"sender_id": "UserMentionService", "urls": ["https://example.com"]}],
    )
    await mpi_urls.step()
    assert url_comm.sent[0][0] == "MediaService"
    assert url_comm.sent[0][1]["shortened_urls"][0]["shortened_url"] == "https://t.ec/1"

    media_comm = set_mpi(
        mpi_media,
        [
            {
                "sender_id": "UrlShortenService",
                "media_ids": [11],
                "media_types": ["image"],
            }
        ],
    )
    await mpi_media.step()
    assert media_comm.sent[0][0] == "UserService"
    assert media_comm.sent[0][1]["media"][0]["media_id"] == 11

    user_comm = set_mpi(
        mpi_user,
        [{"sender_id": "MediaService", "user_id": 101, "username": "alice"}],
    )
    await mpi_user.step()
    assert user_comm.sent[0][0] == "PostStorageService"
    assert user_comm.sent[0][1]["creator"]["username"] == "alice"

    storage_comm = set_mpi(
        mpi_post_storage,
        [
            {
                "sender_id": "UserService",
                "request_type": "compose_post",
                "post_id": 5001,
                "creator": {"user_id": 101, "username": "alice"},
                "text": "Hello",
                "user_mentions": [],
                "media": [],
                "shortened_urls": [],
                "reply_to": "ComposePostService",
            }
        ],
    )
    await mpi_post_storage.step()
    assert storage_comm.sent[0][0] == "UserTimelineService"
    assert storage_comm.sent[0][1]["request_type"] == "write_user_timeline"

    storage_read_comm = set_mpi(
        mpi_post_storage,
        [
            {
                "sender_id": "UserTimelineService",
                "request_type": "read_posts",
                "post_ids": [5001, 9999],
            }
        ],
    )
    await mpi_post_storage.step()
    assert storage_read_comm.sent[0][0] == "UserTimelineService"
    assert storage_read_comm.sent[0][1] == {
        "response_type": "read_posts_response",
        "posts": [
            {
                "post_id": 5001,
                "creator": {"user_id": 101, "username": "alice"},
                "text": "Hello",
                "user_mentions": [],
                "media": [],
                "urls": [],
            }
        ],
    }

    user_timeline_comm = set_mpi(
        mpi_user_timeline,
        [
            {
                "sender_id": "PostStorageService",
                "request_type": "write_user_timeline",
                "creator": {"user_id": 101, "username": "alice"},
                "post_id": 5001,
                "post": {"post_id": 5001, "text": "Hello"},
                "reply_to": "ComposePostService",
            }
        ],
    )
    await mpi_user_timeline.step()
    assert user_timeline_comm.sent[0][0] == "HomeTimelineService"

    user_timeline_read_comm = set_mpi(
        mpi_user_timeline,
        [
            {
                "sender_id": "FrontendService",
                "request_type": "read_user_timeline",
                "user_id": 101,
            }
        ],
    )
    await mpi_user_timeline.step()
    assert user_timeline_read_comm.sent[0][0] == "PostStorageService"
    assert user_timeline_read_comm.sent[0][1] == {
        "request_type": "read_posts",
        "reply_to": "FrontendService",
        "post_ids": [5001],
    }

    social_graph_comm = set_mpi(
        mpi_social_graph,
        [
            {
                "sender_id": "HomeTimelineService",
                "request_type": "get_followers",
                "user_id": 101,
            }
        ],
    )
    await mpi_social_graph.step()
    assert social_graph_comm.sent[0][0] == "HomeTimelineService"
    assert social_graph_comm.sent[0][1]["followers"] == [202, 303]

    home_timeline_comm = set_mpi(
        mpi_home_timeline,
        [
            {
                "sender_id": "UserTimelineService",
                "request_type": "write_home_timeline",
                "creator": {"user_id": 101, "username": "alice"},
                "post_id": 5001,
                "post": {"post_id": 5001, "text": "Hello"},
                "reply_to": "ComposePostService",
            },
            {
                "sender_id": "SocialGraphService",
                "followers": [202, 303],
            },
        ],
    )
    await mpi_home_timeline.step()
    assert home_timeline_comm.sent[0][0] == "SocialGraphService"
    assert home_timeline_comm.sent[1][0] == "ComposePostService"
    assert home_timeline_comm.sent[1][1]["follower_count"] == 2
