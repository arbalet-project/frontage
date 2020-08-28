import datetime

from uuid import uuid4
from db.base import Base
from sqlalchemy import table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class ArtnetModel(Base):
    __tablename__ = 'artnet_model'

    uniqid = Column(String(36), primary_key=True)
    row = Column(Integer)
    column = Column(Integer)
    children = relationship("DMXModel")

    def __init__(self):
        self.uniqid = str(uuid4())
        self.column = 0
        self.row = 0

class DMXModel(Base):
    __tablename__ = 'dmx_model'

    uniqid = Column(String(36), primary_key=True)
    address = Column(Integer)
    universe = Column(Integer)
    artnet = Column(String, ForeignKey('artnet_model.uniqid'))

    def __init__(self):
        self.uniqid = str(uuid4())
        self.address = 0
        self.universe = 0