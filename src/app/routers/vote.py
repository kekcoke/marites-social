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
    """Vote or unvote on a post.
    
    Args:
        vote: Vote data (post_id and direction: 1 for upvote, 0 for remove vote)
        db: Database session
        current_user: Current authenticated user object
        
    Returns:
        Success message
        
    Raises:
        HTTPException 404: If post not found or vote doesn't exist (when removing)
        HTTPException 409: If user already voted (when adding)
        HTTPException 422: If invalid vote direction
        HTTPException 500: If database error occurs
    """
    logger.info(f"User {current_user} voting on post {vote.post_id} with direction {vote.dir}")
    
    try:
        # Validate vote direction
        if vote.dir not in [0, 1]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Vote direction must be 0 (remove) or 1 (add)"
            )
        
        # Check if post exists
        post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
        if not post:
            logger.warning(f"Post not found: {vote.post_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id {vote.post_id} does not exist"
            )
        
        # FIX: Use current_user.id instead of current_user directly
        vote_query = db.query(models.Vote).filter(
            models.Vote.post_id == vote.post_id,
            models.Vote.user_id == current_user
        )
        
        found_vote = vote_query.first()
        
        # Adding a vote
        if vote.dir == 1:
            if found_vote:
                logger.warning(f"User {current_user} already voted on post {vote.post_id}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User has already voted on post {vote.post_id}"
                )
            
            # FIX: Use current_user.id instead of current_user
            new_vote = models.Vote(
                post_id=vote.post_id,
                user_id=current_user
            )
            db.add(new_vote)
            db.commit()
            
            logger.info(f"Vote added by user {current_user} on post {vote.post_id}")
            return {"message": "Successfully added vote"}
        
        # Removing a vote
        else:
            if not found_vote:
                logger.warning(f"Vote not found for user {current_user} on post {vote.post_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vote does not exist"
                )
            
            vote_query.delete(synchronize_session=False)
            db.commit()
            
            logger.info(f"Vote removed by user {current_user} from post {vote.post_id}")
            return {"message": "Successfully deleted vote"}
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during vote operation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
