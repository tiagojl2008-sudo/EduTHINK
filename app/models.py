from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id       = Column(Integer, primary_key=True, index=True)
    name     = Column(String, nullable=False)
    email    = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role     = Column(String, default="user")
    avatar   = Column(String, default="")  # Caminho para a foto de perfil

    reservations = relationship("Reservation", back_populates="user", cascade="all, delete-orphan")



class Room(Base):
    __tablename__ = "rooms"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    capacity   = Column(Integer, nullable=False)
    location   = Column(String, nullable=False)
    color      = Column(String, default="#e85d04")
    start_time = Column(String, nullable=False)        # ex: "08:00"
    end_time   = Column(String, nullable=False)        # ex: "18:00"
    work_days  = Column(String, default="1,2,3,4,5")  # dias da semana separados por vírgula

    reservations = relationship("Reservation", back_populates="room", cascade="all, delete-orphan")
    equipment = relationship("Equipment", back_populates="room", cascade="all, delete-orphan")


class Reservation(Base):
    __tablename__ = "reservations"

    id         = Column(Integer, primary_key=True, index=True)
    title      = Column(String, nullable=False)
    date       = Column(String, nullable=False, index=True)  # ex: "2026-02-23"
    start_time = Column(String, nullable=False)        # ex: "09:00"
    end_time   = Column(String, nullable=False)        # ex: "10:00"

    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    room = relationship("Room", back_populates="reservations")
    user = relationship("User", back_populates="reservations")


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")

    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    room = relationship("Room", back_populates="equipment")


class UserEquipment(Base):
    """Equipamentos atribuídos a utilizadores"""
    __tablename__ = "user_equipment"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, index=True)
    assigned_date = Column(String, nullable=False)
    notes = Column(String, default="")

    user = relationship("User", backref="assigned_equipment")
    equipment = relationship("Equipment")
