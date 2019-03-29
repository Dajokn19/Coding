import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

Base = declarative_base()
encryptionKey = ''

class Location(Base):
    __tablename__='Location'
    latitude = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    longitude = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    streetaddress = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    neighborhood = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    city = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    state = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    zip = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    id = Column(Integer, primary_key = True)

class Event(Base):
    __tablename__='Event'
    date = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    title = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    description =Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    id = Column(Integer, primary_key = True)

# ADD IP ADDRESS ENTITY

class Note(Base):
    __tablename__='Note'
    title = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    description = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    id = Column(Integer, primary_key = True)

class Individual(Base):
    __tablename__ = 'Individual'
    id = Column(Integer, primary_key=True)
    firstname = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    lastname = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    workplace = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    violentincidents = Column(Integer, nullable=False)
    notes = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    email = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    phone = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    facebookurl = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    linkedinurl = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    twitterurl = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    organization = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))

class Vehicle(Base):
    __tablename__='Vehicle'
    plate = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    color = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    make_model = Column(EncryptedType(String ,encryptionKey, AesEngine,'pkcs5'))
    id = Column(Integer, primary_key = True)

class ImageEvent(Base):
    __tablename__='ImageEvent'
    id = Column(Integer, primary_key=True)
    image = Column(BLOB)
    event_id = Column(Integer, ForeignKey('Event.id'))
    event = relationship(Event)

class ImageIndividual(Base):
    __tablename__='ImageIndividual'
    id = Column(Integer, primary_key=True)
    image = Column(BLOB)
    individual_id = Column(Integer, ForeignKey('Individual.id'))
    individual = relationship(Individual)

class ImageVehicle(Base):
    __tablename__='ImageVehicle'
    id = Column(Integer, primary_key=True)
    image = Column(BLOB)
    vehicle_id = Column(Integer, ForeignKey('Vehicle.id'))
    vehicle = relationship(Vehicle)

class IndividualToEvent(Base):
    __tablename__='IndividualToEvent'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('Event.id'))
    event = relationship(Event)
    individual_id = Column(Integer, ForeignKey('Individual.id'))
    individual = relationship(Individual)

class IndividualToLocation(Base):
    __tablename__='IndividualToLocation'
    id = Column(Integer, primary_key=True)
    individual_id = Column(Integer, ForeignKey('Individual.id'))
    individual = relationship(Individual)
    location_id = Column(Integer, ForeignKey('Location.id'))
    location = relationship(Location)

class VehicleToEvent(Base):
    __tablename__='VehicleToEvent'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('Event.id'))
    event = relationship(Event)
    vehicle_id = Column(Integer, ForeignKey('Vehicle.id'))
    vehicle = relationship(Vehicle)

class VehicleToIndividual(Base):
    __tablename__='VehicleToIndividual'
    id = Column(Integer, primary_key=True)
    individual_id = Column(Integer, ForeignKey('Individual.id'))
    individual = relationship(Individual)
    vehicle_id = Column(Integer, ForeignKey('Vehicle.id'))
    vehicle = relationship(Vehicle)

class LocationToEvent(Base):
    __tablename__='LocationToEvent'
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('Location.id'))
    location = relationship(Location)
    event_id = Column(Integer, ForeignKey('Event.id'))
    event = relationship(Event)

class LocationToVehicle(Base):
    __tablename__='LocationToVehicle'
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('Location.id'))
    location = relationship(Location)
    vehicle_id = Column(Integer, ForeignKey('Vehicle.id'))
    vehicle = relationship(Vehicle)

class IndividualToIndividual(Base):
    __tablename__='IndividualToIndividual'
    id = Column(Integer, primary_key=True)
    individual1_id = Column(Integer)
    individual2_id = Column(Integer)

class KeyCheck(Base):
    __tablename__='KeyCheck'
    hash = Column(String(200),nullable = False)
    id = Column(Integer, primary_key = True)

    def setkey(e,key):
        global encryptionKey
        encryptionKey = key

class DefaultImages(Base):
    __tablename__='DefaultImages'
    id = Column(Integer, primary_key=True)
    image = Column(BLOB)
