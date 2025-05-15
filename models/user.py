from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    # le rôle de l'utilisateur (gestion, commercial, support)
    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship("Role", back_populates="users")

    # si l'utilisateur est commercial, il peut gérer plusieurs clients
    clients = relationship("Client", back_populates="commercial")

    # si l'utilisateur est commercial, il peut gérer plusieurs contrats
    contracts = relationship("Contract", back_populates="commercial")

    # si l'utilisateur est support, il peut gérer plusieurs événements
    events = relationship("Event", back_populates="support")
