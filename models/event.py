from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    location = Column(String)
    attendees = Column(Integer)
    notes = Column(String)

    # lien vers le contrat
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    contract = relationship("Contract", back_populates="event")

    # lien vers le client
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship("Client", back_populates="events")

    # lien vers le support (utilisateur)
    support_id = Column(Integer, ForeignKey('users.id'))
    support = relationship("User", back_populates="events")
