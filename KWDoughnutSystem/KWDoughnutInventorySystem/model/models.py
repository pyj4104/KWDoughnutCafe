from pyramid.security import Allow, Everyone
from sqlalchemy import (Column, Integer, Text, String, Float, TIMESTAMP)
from sqlalchemy.dialects import mysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (scoped_session, sessionmaker)
from sqlalchemy.schema import ForeignKey
from zope.sqlalchemy import ZopeTransactionExtension
import datetime

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Page(Base):
    __tablename__ = 'wikipages'
    uid = Column(Integer, primary_key=True)
    title = Column(String(255), unique=True)
    body = Column(Text)

class User(Base):
    __tablename__ = 'usr'
    uid = Column("ID", Integer, primary_key=True, autoincrement=True)
    name = Column("usrName", String(32))
    password = Column("usrPsd", String(256))

class PriceScheme(Base):
    __tablename__ = 'priceScheme'
    tid = Column("ID", Integer, primary_key=True, autoincrement=True)
    boxPrice = Column("boxPrice", mysql.FLOAT(5,2))
    doughnutPrice = Column("doughnutPrice", mysql.FLOAT(4,2))

    def __init__(self, box, doughnut):
        self.boxPrice = box
        self.doughnutPrice = doughnut

class TransHistory(Base):
    __tablename__ = 'transHistory'
    tid = Column("ID", Integer, primary_key=True, autoincrement=True)
    schemeID = Column("schemeID", Integer, ForeignKey("priceScheme.ID"))
    sellerID = Column("sellerID", Integer, ForeignKey("usr.ID"))
    timeSold = Column("timeSold", TIMESTAMP)
    boxesSold = Column("boxesSold", mysql.INTEGER, nullable=False, default=0)
    doughnutsSold = Column("doughnutsSold", mysql.INTEGER, nullable=False, default=0)
    deleted = Column("deleted", mysql.BIT, nullable=False, default=0)
    deferredPayment = Column("deferredPayment", mysql.BIT, nullable=False, default=0)
    deletedUsrInit = Column("deletedUsrInit", mysql.NVARCHAR(20))

    def __init__(self, pschema, seller, boxes, doughnuts, deferredPayment):
        self.schemeID = pschema
        self.sellerID = seller
        self.timeSold = datetime.datetime.now()
        self.boxesSold = boxes
        self.doughnutsSold = doughnuts
        self.deferredPayment = 1 if deferredPayment else 0

class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass