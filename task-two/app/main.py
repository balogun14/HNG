from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schema, crud, database, utils
from .database import engine, get_db
from fastapi.security import OAuth2PasswordRequestForm

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/auth/register", response_model=schema.User)
def register_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/auth/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=schema.User)
def read_users_me(current_user: schema.User = Depends(utils.get_current_user)):
    return current_user

@app.post("/api/organisations", response_model=schema.Organisation)
def create_organisation(org: schema.OrganisationCreate, current_user: schema.User = Depends(utils.get_current_user), db: Session = Depends(get_db)):
    return crud.create_organisation(db=db, org=org, user_id=current_user.userId)

@app.get("/api/organisations", response_model=List[schema.Organisation])
def read_organisations(current_user: schema.User = Depends(utils.get_current_user), db: Session = Depends(get_db)):
    return crud.get_organisations_by_user_id(db=db, user_id=current_user.userId)

@app.get("/api/organisations/{org_id}", response_model=schema.Organisation)
def read_organisation(org_id: str, current_user: schema.User = Depends(utils.get_current_user), db: Session = Depends(get_db)):
    org = crud.get_organisation(db=db, org_id=org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return org

@app.post("/api/organisations/{org_id}/users")
def add_user_to_organisation(org_id: str, user_org: schema.UserOrganisationCreate, current_user: schema.User = Depends(utils.get_current_user), db: Session = Depends(get_db)):
    org = crud.get_organisation(db=db, org_id=org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organisation not found")
    user = crud.get_user_by_email(db=db, email=user_org.userId)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_org = models.UserOrganisation(user_id=user.userId, org_id=org.orgId)
    db.add(user_org)
    db.commit()
    return {"message": "User added to organisation successfully"}
