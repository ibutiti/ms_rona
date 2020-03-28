import os

import tweepy


class TwitterAPI:

    def __init__(self):

        auth = tweepy.OAuthHandler(
            consumer_key=os.environ.get('TWITTER_API_KEY'),
            consumer_secret=os.environ.get('TWITTER_API_SECRET'),
        )

        auth.set_access_token(
            key=os.environ.get('TWITTER_ACCESS_TOKEN_KEY'),
            secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
        )

        self.api = tweepy.API(auth)

    def get_mentions(self, since: str):
        return self.api.mentions_timeline(since=since)

    def make_reply(self, tweet: tweepy.models.Status, content: str):
        return self.api.update_status(
            status=content,
            in_reply_to_status_id=tweet.id,
            auto_populate_reply_metadata=True
        )




