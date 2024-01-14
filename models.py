import typing as T
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import _sa_util
import sqlalchemy as sa



class Base(DeclarativeBase):

    __abstract__ = True

    @classmethod
    def get_or_create(
        cls, session: sa.orm.Session, defaults=None, commit=True, **kwargs
    ):
        """Django-inspired get_or_create."""
        predicates = [getattr(cls, k) == v for k, v in kwargs.items()]
        instance = session.scalar(sa.select(cls).where(*predicates))
        if instance:
            return instance, False

        defaults = defaults or {}
        instance_kwargs = kwargs | defaults
        instance = cls(**instance_kwargs)
        session.add(instance)
        if commit:
            session.commit()

        return instance, True

class BaseMaster(Base):
    
    __abstract__ = True

class BaseSlave(Base):
    
    __abstract__ = True

article_to_uni = sa.Table('article_to_uni', Base.metadata, 
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('uni_id', sa.Integer(), ForeignKey("universities.id")),
    sa.Column('article_id', sa.Integer(), ForeignKey("related_articles.id"))
)

article_to_state = sa.Table('article_to_state', Base.metadata, 
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('state_id', sa.Integer(), ForeignKey("states.id")),
    sa.Column('artical_id', sa.Integer(), ForeignKey("related_articles.id"))
)

class State(Base):
    __tablename__ = 'states'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(255), nullable=True)

class Universities(BaseMaster):
    __tablename__ = 'universities'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(255), nullable=True)
    state_id = sa.Column(sa.Integer, sa.ForeignKey('states.id'))

class Sources(BaseMaster):
    __tablename__ = "sources"

    link_to_state = sa.Column(sa.Text, name='Link to state news 1', nullable=True)
    domain = sa.Column(sa.Text, name='domain', nullable=True, primary_key=True)
    link = sa.Column(sa.Text, name='link to google news', nullable=True)
    score = sa.Column(sa.Text, name='score of relevance to the university', nullable=True)
    words = sa.Column(sa.Text, name='Words to determine atisimitics event', nullable=True)
    university_name = sa.Column(sa.Text, name='University name1', nullable=True)
    state_name = sa.Column(sa.Text, name='State name1', nullable=True)
    university_id = sa.Column(sa.Text, sa.ForeignKey('universities.id'), name='university_id', nullable=True)
    state_id = sa.Column(sa.Text, sa.ForeignKey('states.id'), name='state_id', nullable=True)
    university = relationship('Universities')
    state = relationship('State')

class RelatedArticles(BaseMaster):
    __tablename__ = 'related_articles'

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(255), nullable=True)
    link = sa.Column(sa.Text, nullable=True)
    text = sa.Column(sa.Text, nullable=True)
    pic = sa.Column(sa.Text, nullable=True)
    date = sa.Column(sa.DATETIME, nullable=True)
    university = sa.orm.relationship("Universities", secondary=article_to_uni, backref="articles")
    state = sa.orm.relationship("State", secondary=article_to_state, backref="articles")

class SmWords(BaseMaster):

    __tablename__ = 'sm_words'

    id = sa.Column(sa.Integer, primary_key=True)
    word = sa.Column(sa.String(255), nullable=True)
    last_update = sa.Column(sa.DATETIME, nullable=True)

class SmPost(BaseMaster):

    __tablename__ = 'sm_posts'

    id = sa.Column(sa.Integer, primary_key=True)
    network = sa.Column(sa.String(255), nullable=True)
    post_text = sa.Column(sa.Text, nullable=True)
    post_text = sa.Column(sa.Text, nullable=True)
    uni_id = sa.Column(sa.Integer, ForeignKey("universities.id"), nullable=True)
    sentiment = sa.Column(sa.Integer, nullable=True)
    author_name = sa.Column(sa.String(255), nullable=True)
    link = sa.Column(sa.String(255), nullable=True)
    community = sa.Column(sa.String(255), nullable=True)
    id_word = sa.Column(sa.Integer, ForeignKey("sm_words.id"), nullable=True)
    number_comments = sa.Column(sa.Integer, nullable=True)
    image = sa.Column(sa.Text, nullable=True)
    domain = sa.Column(sa.String(255), nullable=True)
    number_likes = sa.Column(sa.Integer, nullable=True)
    date_added_to_db = sa.Column(sa.DATETIME, nullable=True)
    post_create = sa.Column(sa.DATETIME, nullable=True)
    word = relationship('SmWords')
    

word_to_post = sa.Table('cm_scraping_posts_v2_tags', BaseSlave.metadata, 
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('scrapingpostv2_id', sa.Integer(), ForeignKey("cm_scraping_posts_v2.id")),
    sa.Column('scrapingkeywords_id', sa.Integer(), ForeignKey("cm_scraping_words.id"))
)


class CMScrapingAccounts(BaseSlave):

    __tablename__ = 'cm_scraping_accounts'

    id = sa.Column(sa.Integer, primary_key=True)
    acc_id = sa.Column(sa.Integer, nullable=True)
    name = sa.Column(sa.String(256), nullable=True)
    link = sa.Column(sa.String(1024), nullable=True)
    network = sa.Column(sa.String(128), nullable=True)


class CMScrapingPostGroups(BaseSlave):

    __tablename__ = 'cm_scraping_posts_groups'

    id = sa.Column(sa.Integer, primary_key=True)
    group_id = sa.Column(sa.Integer, nullable=False)
    post_id = sa.Column(sa.Integer, sa.ForeignKey('cm_scraping_posts_v2.id'), nullable=False)


class CMScrapedPostv2(BaseSlave):

    __tablename__ = 'cm_scraping_posts_v2'

    id = sa.Column(sa.Integer, primary_key=True)
    post_text = sa.Column(sa.Text, nullable=True)
    account = sa.Column(sa.String(400), nullable=True)
    link = sa.Column(sa.String(400), nullable=True)
    network = sa.Column(sa.String(400), nullable=True)
    date = sa.Column(sa.DATETIME, nullable=True)
    keywords = sa.Column(sa.Text, nullable=True)
    emotions = sa.Column(sa.Text, nullable=True)
    likes = sa.Column(sa.Integer, nullable=True)
    comments = sa.Column(sa.Integer, nullable=True)
    shares = sa.Column(sa.Integer, nullable=True)
    pic = sa.Column(sa.Text, nullable=True)
    defamatory = sa.Column(sa.Boolean, nullable=True)
    date_added_to_db = sa.Column(sa.DATETIME, nullable=True)
    lang = sa.Column(sa.String(150), nullable=True)
    score = sa.Column(sa.String(150), nullable=True)
    social_account_id = sa.Column(sa.Integer, ForeignKey("cm_scraping_accounts.id"), nullable=True)

class CMScrapedWords(BaseSlave):

    __tablename__ = 'cm_scraping_words'

    id = sa.Column(sa.Integer, primary_key=True)
    word = sa.Column(sa.String(400), nullable=False)
    user_group = sa.Column(sa.Integer, nullable=False)
    target_source = sa.Column(sa.String(64), nullable=True)
    data_extraction_mode = sa.Column(sa.Integer, nullable=True)
    posts = relationship("CMScrapedPostv2", secondary=word_to_post, backref='words')
