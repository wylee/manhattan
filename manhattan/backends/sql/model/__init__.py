from sqlalchemy import Column, ForeignKey, types, orm
from sqlalchemy.orm.exc import NoResultFound

from . import meta, custom_types
from .base import Base


def init_model(engine):
    """
    Provide a sqlalchemy engine for the model to perform operations with.  Call
    before using any of the tables or classes in this model.
    """
    sm = orm.sessionmaker(bind=engine, expire_on_commit=engine)
    meta.engine = engine
    meta.metadata.bind = engine
    meta.Session = orm.scoped_session(sm)


class Visitor(Base):
    __tablename__ = 'visitors'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    visitor_id = Column(types.BINARY(40), primary_key=True)
    bot = Column(types.Boolean, nullable=False, default=True)
    first_timestamp = Column(types.Integer, nullable=False)
    last_timestamp = Column(types.Integer, nullable=False)

    @classmethod
    def find_or_create(cls, visitor_id, timestamp):
        try:
            vis = meta.Session.query(cls).\
                    filter_by(visitor_id=visitor_id).one()
        except NoResultFound:
            vis = cls(visitor_id=visitor_id,
                      first_timestamp=timestamp)
            meta.Session.add(vis)
        vis.last_timestamp = timestamp
        return vis


class Request(Base):
    __tablename__ = 'requests'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    visitor_id = Column(None, ForeignKey('visitors.visitor_id'),
                        unique=False, index=True)
    timestamp = Column(types.Integer, nullable=False, index=True, unique=False)
    url = Column(types.String(255), nullable=False)
    ip = Column(custom_types.IP, nullable=False)
    method = Column(types.CHAR(5), nullable=False)

    visitor = orm.relationship('Visitor')


class Goal(Base):
    __tablename__ = 'goals'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    name = Column(types.String(255), unique=True)
    value_type = Column(types.CHAR(1), nullable=True)
    value_format = Column(types.CHAR(1), nullable=True)


class Conversion(Base):
    __tablename__ = 'conversions'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    goal_id = Column(None, ForeignKey('goals.id'), primary_key=True)
    visitor_id = Column(None, ForeignKey('visitors.visitor_id'),
                        primary_key=True)
    goal = orm.relationship('Goal')
    visitor = orm.relationship('Visitor')


class VariantConversion(Base):
    __tablename__ = 'variant_conversions'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    goal_id = Column(None, ForeignKey('goals.id'), primary_key=True)
    variant_id = Column(None, ForeignKey('variants.id'), primary_key=True)
    visitor_id = Column(None, ForeignKey('visitors.visitor_id'),
                        primary_key=True)
    goal = orm.relationship('Goal')
    variant = orm.relationship('Variant')
    visitor = orm.relationship('Visitor')


class Test(Base):
    __tablename__ = "tests"
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    name = Column(types.String(255), nullable=False)


class Variant(Base):
    __tablename__ = 'variants'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    test_id = Column(None, ForeignKey('tests.id'), nullable=False)
    name = Column(types.String(255), nullable=False)
    test = orm.relationship('Test', backref='variants')


class Impression(Base):
    __tablename__ = 'impressions'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    variant_id = Column(None, ForeignKey('variants.id'), primary_key=True)
    visitor_id = Column(None, ForeignKey('visitors.visitor_id'),
                        primary_key=True)
    variant = orm.relationship('Variant', backref='impressions')
    visitor = orm.relationship('Visitor')