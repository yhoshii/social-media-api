from fastapi import status, HTTPException, Depends, APIRouter
from app import models, schemas, utils
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/users",
                   tags=['Users'])

@router.post(
        "/",
        status_code=status.HTTP_201_CREATED,
        response_model=schemas.UserResponce
        )

def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user.password = utils.hash_password(user.password)
    new_user = models.User(**user.model_dump())

    user_query = db.query(models.User).filter(models.User.email == new_user.email)
    if user_query.first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="A user with this email already exists")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


#retrieving info about a user based on theur id
@router.get('/{id}', response_model=schemas.UserResponce)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")

    return user
