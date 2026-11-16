import copy
import unittest
from unittest.mock import Mock, patch

import requests

from radiojavanapi.constants import PLAY_API_DOMAIN, PLAY_API_HEADERS
from radiojavanapi.mixins.podcast import PodcastMixin


PODCAST_RESPONSE = {
    "id": 5462,
    "title": "AM Beat 17",
    "podcast_artist": "DJ AMB",
    "explicit": False,
    "talk": False,
    "link": "https://example.com/mix.mp3",
    "photo": "https://example.com/photo.jpg",
    "photo_large": "https://example.com/photo-large.jpg",
    "date": "DJ AMB",
    "photo_player": "https://example.com/photo-player.jpg",
    "photo_240": "https://example.com/photo-240.jpg",
    "thumbnail": "https://example.com/thumbnail.jpg",
    "likes": "483",
    "dislikes": "0",
    "plays": "120,093",
    "permlink": "AM-Beat-17",
    "created_at": "2026-11-01T23:30:00-05:00",
    "share_link": "https://example.com/podcast",
    "type": "podcast",
    "short_date": "DJ AMB",
    "date_added": "Nov 1, 2026",
    "premium_only": False,
    "duration": 1241.21,
    "sample_start": 20,
    "preview_link": "https://example.com/preview.mp3",
    "hls_link": "https://example.com/playlist.m3u8",
    "show_permlink": "AM-Beat",
    "lq_link": "https://example.com/low.m4a",
    "hq_link": "https://example.com/high.m4a",
    "lq_hls": "https://example.com/low.m3u8",
    "hq_hls": "https://example.com/high.m3u8",
    "lufs": -9.3,
    "credit_tags": ["dj amb"],
    "bg_colors": ["#0a3338", "#051a1c"],
    "artist_farsi": "دی‌جی ای‌ام‌بی",
    "title_farsi": "ای‌ام بیت ۱۷",
    "tracklist": "Amir Tataloo - Raftanet\\nAli Yasini - Nemikhastam",
    "tracklist_synced": [
        {"time": 20, "text": "Amir Tataloo - Raftanet", "mp3": 151137},
        {"time": 99, "text": "Ali Yasini - Nemikhastam", "mp3": 154038},
    ],
    "comments_count": 6,
    "comments_count_pretty": "6",
    "related": [],
}


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError("HTTP error")

    def json(self):
        return copy.deepcopy(self.payload)


class PodcastTracklistTests(unittest.TestCase):
    @patch("radiojavanapi.mixins.podcast.requests.get")
    def test_get_podcast_includes_timestamped_tracklist(self, get):
        get.return_value = FakeResponse(PODCAST_RESPONSE)

        podcast = PodcastMixin().get_podcast_by_id(5462)

        self.assertEqual(len(podcast.tracklist_synced), 2)
        self.assertEqual(podcast.tracklist_synced[0].time, 20.0)
        self.assertEqual(podcast.tracklist_synced[0].text, "Amir Tataloo - Raftanet")
        self.assertEqual(podcast.tracklist_synced[0].mp3, 151137)
        self.assertEqual(podcast.podcast_artist, "DJ AMB")
        self.assertEqual(podcast.title_farsi, "ای‌ام بیت ۱۷")
        get.assert_called_once_with(
            PLAY_API_DOMAIN.format("podcast"),
            params={"id": 5462},
            headers=PLAY_API_HEADERS,
            proxies=None,
            timeout=30,
        )

    @patch("radiojavanapi.mixins.podcast.requests.get")
    def test_legacy_podcast_without_synced_tracklist_returns_empty_list(self, get):
        legacy_payload = copy.deepcopy(PODCAST_RESPONSE)
        legacy_payload.pop("tracklist_synced")
        get.return_value = FakeResponse(legacy_payload)

        podcast = PodcastMixin().get_podcast_by_id(5462)

        self.assertEqual(podcast.tracklist, "Amir Tataloo - Raftanet\\nAli Yasini - Nemikhastam")
        self.assertEqual(podcast.tracklist_synced, [])

    @patch("radiojavanapi.mixins.podcast.requests.get")
    def test_null_synced_tracklist_returns_empty_list(self, get):
        payload = copy.deepcopy(PODCAST_RESPONSE)
        payload["tracklist_synced"] = None
        get.return_value = FakeResponse(payload)

        podcast = PodcastMixin().get_podcast_by_id(5462)

        self.assertEqual(podcast.tracklist_synced, [])

    @patch("radiojavanapi.mixins.podcast.requests.get")
    def test_slug_is_resolved_to_numeric_id_for_play_api(self, get):
        legacy_payload = copy.deepcopy(PODCAST_RESPONSE)
        legacy_payload.pop("tracklist_synced")
        get.side_effect = [
            FakeResponse({"message": "not found"}, status_code=404),
            FakeResponse(PODCAST_RESPONSE),
        ]
        client = PodcastMixin()
        client.private_request = Mock(return_value=FakeResponse(legacy_payload))

        podcast = client.get_podcast_by_id("am-beat-17")

        self.assertEqual(podcast.tracklist_synced[0].time, 20.0)
        self.assertEqual(get.call_args_list[0].kwargs["params"], {"id": "am-beat-17"})
        self.assertEqual(get.call_args_list[1].kwargs["params"], {"id": 5462})

    @patch("radiojavanapi.mixins.podcast.requests.get", side_effect=requests.ConnectionError)
    def test_falls_back_to_legacy_api2_when_play_api_fails(self, get):
        legacy_payload = copy.deepcopy(PODCAST_RESPONSE)
        legacy_payload.pop("tracklist_synced")
        legacy_response = FakeResponse(legacy_payload)
        client = PodcastMixin()
        client.private_request = Mock(return_value=legacy_response)

        podcast = client.get_podcast_by_id(5462)

        self.assertEqual(podcast.tracklist_synced, [])
        client.private_request.assert_called_once_with("podcast", params="id=5462")


if __name__ == "__main__":
    unittest.main()
