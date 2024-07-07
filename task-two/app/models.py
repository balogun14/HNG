from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    userId = Column(String, primary_key=True, index=True, unique=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    organisations = relationship("Organisation", secondary="user_organisations")

class Organisation(Base):
    __tablename__ = "organisations"

    orgId = Column(String, primary_key=True, index=True, unique=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    users = relationship("User", secondary="user_organisations")

class UserOrganisation(Base):
    __tablename__ = "user_organisations"

    user_id = Column(String, ForeignKey("users.userId"), primary_key=True)
    org_id = Column(String, ForeignKey("organisations.orgId"), primary_key=True)
