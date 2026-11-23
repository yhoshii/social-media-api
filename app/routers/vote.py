from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app import models, schemas, oauth2, database

router = APIRouter(prefix="/vote", tags=['Vote'])

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), 
         curr_user = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {vote.post_id} does not exist")

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,
                                                      models.Vote.user_id == curr_user.id)
    found_vote = vote_query.first()

    if vote.dir == 1:
        if found_vote is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"User {curr_user.id} has already voted on post {vote.post_id}")

        new_vote = models.Vote(post_id=vote.post_id, user_id=curr_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "successfully added new vote"}

    if vote.dir == 0:
        if found_vote is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"User {curr_user.id} has already voted on post {vote.post_id}")

        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "successfully deleted vote"}
