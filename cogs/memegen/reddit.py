from .commons import Generator, GeneratorError

from praw import Reddit
from praw.exceptions import MissingRequiredAttributeException

from urllib.parse import urlparse
from datetime import datetime, timezone


class RedditMeme(Generator):
    """A partial implementation which skims through only a defined set of sub-reddits and cherrypicks random
    image based posts on demand, those are considered as image-based memes."""

    def __init__(self, id: str, secret: str):
        """Initialize the praw API for grabbing image based submissions from Reddit.

        :param id: client id of the reddit app
        :param secret: client secret of the reddit app
        :raises GeneratorError: if the credentials were invalid
        """
        try:
            self.source = Reddit(client_id=id, client_secret=secret,
                                 user_agent=self.__class__.__name__) \
                .subreddit('PewDiePieSubmissions+'
                           'memes+'
                           'dankmemes+'
                           'me_irl')
        except MissingRequiredAttributeException:
            raise GeneratorError("required attributes were invalid")

    def _get_image(self):
        allowed_domains = ['i.redd.it', 'i.imgur.com']

        submission = None
        while submission is None or not urlparse(submission.url)[1] in allowed_domains:
            submission = self.source.random()

        return submission

    def __call__(self):
        image = self._get_image()

        return image.url, {
            'title': image.title,
            'author': image.author.name,
            'creation': datetime.fromtimestamp(image.created_utc, timezone.utc),
        }
