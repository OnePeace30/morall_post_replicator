from models import SmPost, CMScrapedPostv2, CMScrapingAccounts, CMScrapingPostGroups, CMScrapedWords
from util import Database
from datetime import datetime as dt
import sqlalchemy as sa
import logging
from logging.handlers import TimedRotatingFileHandler


logger = logging.getLogger("replicator")
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler(f"replicator.log", interval=1, backupCount=3, when='d')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)


if __name__ == '__main__':
    db = Database()
    max_value_id = 9223372036854775807
    posts = db.master_session.query(SmPost).filter(SmPost.date_added_to_db > dt.now().date()).all()
    logger.info(f"New posts - {len(posts)}")
    for post in posts:
        logger.info(f'post - {post.id}')
        curr_id = max_value_id - post.id
        acc, created = CMScrapingAccounts.get_or_create(
            db.slave_session,
            defaults={
                "name": post.author_name,
                "network": post.network
            }, name=post.author_name, network=post.network
        )
        logger.info('Account {acc.name} is created {created}')
        cm_post, created = CMScrapedPostv2.get_or_create(
            db.slave_session,
            defaults={
                "id": max_value_id - post.id,
                "post_text": post.post_text,
                "account": post.author_name,
                "link": post.link,
                "network": post.network,
                "date": post.post_create,
                "likes": post.number_likes,
                "comments": post.number_comments,
                "pic": post.image,
                "date_added_to_db": post.date_added_to_db,
                "social_account_id": acc.id,
            }, id=max_value_id - post.id
        )
        logger.info('Post {cm_post.id} is created {created}')
        if not created:
            continue
        CMScrapingPostGroups.get_or_create(
            db.slave_session,
            group_id=496, post_id=cm_post.id
        )
        cm_word = db.slave_session.query(CMScrapedWords).filter(sa.and_(CMScrapedWords.word == post.word.word, CMScrapedWords.user_group == 496)).one_or_none()
        if cm_word:
            logger.info(f'Link post {cm_post.id} to word {cm_word.id}')
            cm_word.posts = [*cm_word.posts, cm_post]
            db.slave_session.commit()