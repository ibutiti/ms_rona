import datetime
import logging
import os
import time

import redis
import sentry_sdk

from dateutil import parser

from tracker_api import TrackerAPI
from twitter_api import TwitterAPI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
db = redis.from_url(os.environ.get('REDIS_URL'))
sentry_sdk.init(os.environ.get('SENTRY_URL'))
tracker_api = TrackerAPI()
twitter_api = TwitterAPI()


def load_data():
    data = tracker_api.get_data_by_country()
    global_data = {
        'confirmed': f"{data['latest']['confirmed']:,}",
        'deaths': f"{data['latest']['deaths']:,}",
        'last_updated': data['locations'][0]['last_updated']
    }
    db.hmset('global_latest', global_data)


def compose_tweet(confirmed: int, deaths: int, handle: str, last_updated: datetime.datetime):
    time_delta = (datetime.datetime.utcnow().replace(tzinfo=last_updated.tzinfo) - last_updated).total_seconds()
    minutes = time_delta/60
    if minutes > 60:
        friendly_time = f'about {int(minutes/60)} hours ago'
    else:
        friendly_time = f'about {int(minutes)} minutes ago'

    content = f'Hey @{handle}!\n' \
              f'Hope you\'re #SocialDistancing wherever you are!\n' \
              f'Here are the #CoronaVirusOutbreak global stats reported {friendly_time}:\n' \
              f'Confirmed cases: {confirmed}\n' \
              f'Deaths: {deaths}\n' \
              f'Source: @JohnsHopkins\n\n' \
              f'#COVID19 #Covid_19 #coronavirus #pandemic'

    return content


def check_for_new_mentions(since):
    try:
        mentions = twitter_api.get_mentions(since)
    except:
        logger.exception('Exception while getting mentions')
        return

    newest_tweet_id = ''
    for mention in mentions:
        mention_id = str(mention.id)
        try:
            if mention_id == since or db.sismember('processed_mentions', mention_id):
                continue

            raw_stats = db.hmget('global_latest', 'confirmed', 'deaths', 'last_updated')
            stats = [stat.decode('utf-8') for stat in raw_stats]
            last_updated = parser.parse(stats[2])

            tweet_content = compose_tweet(
                confirmed=stats[0],
                deaths=stats[1],
                handle=mention.author.screen_name,
                last_updated=last_updated,
            )
            twitter_api.make_reply(mention, tweet_content)

            db.sadd('processed_mentions', mention_id)

            if newest_tweet_id < mention_id:
                newest_tweet_id = mention_id
                db.set('latest_mention_id', newest_tweet_id)

        except:
            logger.exception(f'Error while processing mention with id {mention_id}')

    logger.info('Mentions check complete')


if __name__ == '__main__':
    logger.info('Initial loading of data')
    load_data()
    logger.info('Service started')
    count = 0
    while True:
        count += 1
        time.sleep(15)
        logger.info('Checking for new mentions')
        check_for_new_mentions(db.get('latest_mention_id'))

        if count > 60:
            logger.info('Refreshing data')
            try:
                load_data()
                count = 0
            except:
                logger.exception('Failed to refresh data')


