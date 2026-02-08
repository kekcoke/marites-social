import logging
from uuid import UUID
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app import models, db, schemas, auth

router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)
logger = logging.getLogger(__name__)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: schemas.Vote, 
    db: Session = Depends(db.get_db_session),
    current_user: UUID = Depends(auth.oauth2.get_current_user)
):
    """Vote to post"""
    logger.info(f"Voting as user {current_user}")
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voting with id: {vote.post_id} does not exist"
        )
    
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id  
    )

    found_vote = vote_query.first()

    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {current_user} has already voted on post {vote.post_id}"
            )
        
        new_vote = models.Vote(
            post_id = vote.post_id,
            user_id=current_user
        )
        db.add(new_vote)
        db.commit()

        logger.info(f"Vote added by user {current_user}")
        return { "message": "Successfully added vote"}
    
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vote does not exist"
            )

        vote_query.delete(synchronize_session=False)
        db.commit()

        logger.info(f"Vote removed by user {current_user}")

        return { "message": "Successfully deleted vote" }