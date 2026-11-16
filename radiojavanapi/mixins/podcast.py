from radiojavanapi.mixins.private import PrivateRequest
from radiojavanapi.extractors import extract_podcast
from radiojavanapi.constants import PLAY_API_DOMAIN, PLAY_API_HEADERS
from radiojavanapi.models import Podcast
from radiojavanapi.helper import url_to_id

from typing import Union
import requests
from pydantic import HttpUrl, ValidationError

class PodcastMixin(PrivateRequest):
    LIKE_ENDPOINT = 'podcast_vote'
    TYPE = 'podcast'

    def get_podcast_by_url(self, url: HttpUrl) -> Podcast:
        """
        Get podcast info by site url (e.g. `play.radiojavan.com/podcast/...` or `play.radiojavan.com/redirect?r=radiojavan://podcast/...`)

        Arguments
        ----------
            url: Site url of podcast

        Returns
        -------
            Podcast: An object of Podcast type

        """
        return self.get_podcast_by_id(url_to_id(url))

    def get_podcast_by_id(self, id: Union[int, str]) -> Podcast:
        """
        Get podcast info by id

        Arguments
        ----------
            id: Unique id of podcast

        Returns
        -------
            Podcast: An object of Podcast type

        """
        # Prefer the Play API: newer podcasts can include timestamped track entries.
        # URL-based lookups may yield a slug, so resolve it through API2 when needed.
        try:
            return self._get_podcast_from_play_api(id)
        except (requests.RequestException, ValueError, ValidationError, KeyError, TypeError):
            pass

        legacy_data = self.private_request('podcast', params=f'id={id}').json()
        legacy_id = legacy_data.get('id') if isinstance(legacy_data, dict) else None
        legacy_podcast = extract_podcast(legacy_data)

        if legacy_id is not None and str(legacy_id) != str(id):
            try:
                return self._get_podcast_from_play_api(legacy_id)
            except (requests.RequestException, ValueError, ValidationError, KeyError, TypeError):
                pass

        return legacy_podcast

    def _get_podcast_from_play_api(self, id: Union[int, str]) -> Podcast:
        """Fetch and parse a podcast using Radio Javan's current Play API."""
        response = requests.get(
            PLAY_API_DOMAIN.format('podcast'),
            params={'id': id},
            headers=PLAY_API_HEADERS,
            proxies=self.private.proxies or None,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or data.get('id') is None:
            raise ValueError('Unexpected response from Radio Javan Play API')
        return extract_podcast(data)

    def like_podcast(self, podcast_id: Union[int, str]) -> bool:
        """
        Like a podcast

        Arguments
        ----------
            podcast_id: A digit id of podcast

        Returns
        -------
            bool: Returns false if podcast had been liked already

        """
        return PodcastMixin.__like__(self, podcast_id)

    def unlike_podcast(self, podcast_id: Union[int, str]) -> bool:
        """
        UnLike a podcast

        Arguments
        ----------
            podcast_id: A digit id of podcast

        Returns
        -------
            bool: Returns false if podcast hadn't been liked before

        """
        return PodcastMixin.__unlike__(self, podcast_id)

