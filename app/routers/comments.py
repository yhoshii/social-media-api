from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import database, models, oauth2, schemas

router = APIRouter(tags=["Comments"])


@router.get("/post/{post_id}/comment", response_model=list[schemas.CommentResponse])
def get_comments(
    post_id: int,
    db: Session = Depends(database.get_db),
    limit: int = 10,
    curr_user=Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {post_id} was not found",
        )

    comments = (
        db.query(models.Comment)
        .filter(models.Comment.post_id == post_id)
        .limit(limit)
        .all()
    )

    return comments


@router.post(
    "/post/{post_id}/comment",
    response_model=schemas.CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_comment(
    post_id: int,
    comment: schemas.Comment,
    db: Session = Depends(database.get_db),
    curr_user=Depends(oauth2.get_current_user),
):
    new_comment = models.Comment(
        owner_id=curr_user.id, post_id=post_id, **comment.model_dump()
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@router.delete("/comment/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    id: int,
    db: Session = Depends(database.get_db),
    curr_user=Depends(oauth2.get_current_user),
):
    comment_query = db.query(models.Comment).filter(models.Comment.id == id)
    comment = comment_query.first()

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {id} does not exist",
        )

    if comment.owner_id != curr_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    comment_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
