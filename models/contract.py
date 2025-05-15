from sqlalchemy import Column, Integer, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class Contract(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    total_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)
    created_date = Column(Date)
    is_signed = Column(Boolean, default=False)

    # lien vers le client
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship("Client", back_populates="contracts")

    # lien vers le commercial
    commercial_id = Column(Integer, ForeignKey('users.id'))
    commercial = relationship("User", back_populates="contracts")

    # un contrat peut être lié à un événement
    event = relationship("Event", uselist=False, back_populates="contract")
