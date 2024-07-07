from sqlalchemy.orm import Session
from . import models, schema
from fastapi import HTTPException, status
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user: schema.UserCreate):
    db_user = models.User(
        userId=str(uuid.uuid4()),
        firstName=user.firstName,
        lastName=user.lastName,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create default organisation
    org_name = f"{user.firstName}'s Organisation"
    db_org = models.Organisation(
        orgId=str(uuid.uuid4()),
        name=org_name
    )
    db.add(db_org)
    db.commit()
    db.refresh(db_org)

    # Link user and organisation
    user_org = models.UserOrganisation(
        user_id=db_user.userId,
        org_id=db_org.orgId
    )
    db.add(user_org)
    db.commit()

    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_organisation(db: Session, org: schema.OrganisationCreate, user_id: str):
    db_org = models.Organisation(
        orgId=str(uuid.uuid4()),
        name=org.name,
        description=org.description
    )
    db.add(db_org)
    db.commit()
    db.refresh(db_org)

    user_org = models.UserOrganisation(
        user_id=user_id,
        org_id=db_org.orgId
    )
    db.add(user_org)
    db.commit()

    return db_org

def get_organisations_by_user_id(db: Session, user_id: str):
    return db.query(models.Organisation).join(models.UserOrganisation).filter(models.UserOrganisation.user_id == user_id).all()

def get_organisation(db: Session, org_id: str):
    return db.query(models.Organisation).filter(models.Organisation.orgId == org_id).first()
