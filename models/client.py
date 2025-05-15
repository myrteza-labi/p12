from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String)
    company_name = Column(String)
    created_date = Column(Date)
    last_contact_date = Column(Date)

    # le commercial (utilisateur) qui gère ce client
    commercial_id = Column(Integer, ForeignKey('users.id'))
    commercial = relationship("User", back_populates="clients")

    contracts = relationship("Contract", back_populates="client")
    events = relationship("Event", back_populates="client")
