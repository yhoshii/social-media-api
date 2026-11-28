from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, update
from sqlalchemy.orm import Session

from app import models, oauth2, schemas
from app.database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


# get a post
@router.get("/", response_model=list[schemas.PostResponce])
def get_posts(
    db: Session = Depends(get_db),
    curr_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
    search: str | None = "",
):
    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .all()
    )
    return posts


@router.get("/{id}", response_model=schemas.PostResponce)
def get_post(
    id: int, db: Session = Depends(get_db), curr_user=Depends(oauth2.get_current_user)
):
    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found",
        )
    return post


# post a post
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,  # just a convention, by defult it would be 200
    response_model=schemas.Post,
)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    curr_user=Depends(oauth2.get_current_user),
):
    new_post = models.Post(owner_id=curr_user.id, **post.model_dump())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # refresh will store the newest data in new_post variable
    return new_post


# deleting the post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int, db: Session = Depends(get_db), curr_user=Depends(oauth2.get_current_user)
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} does not exist",
        )

    if post.owner_id != curr_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# updating
@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    curr_user=Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    to_update = post_query.first()

    if to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} does not exist",
        )

    if to_update.owner_id != curr_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    db.execute(
        update(models.Post).where(models.Post.id == id).values(**post.model_dump())
    )
    db.commit()
    return post_query.first()
