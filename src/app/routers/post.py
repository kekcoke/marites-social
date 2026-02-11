import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, logger, Response, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.auth import oauth2
from app import models, schemas
from app.db.session import get_db_session

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)
logger = logging.getLogger(__name__)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(
    post: schemas.CreatePost, 
    db: Session = Depends(get_db_session),
    user_id: UUID = Depends(oauth2.get_current_user)
):
    """Create a new post in the database.
    
    Args:
        post: Post creation data
        db: Database session
        user_id: Current authenticated user's ID
        
    Returns:
        Created post object
        
    Raises:
        HTTPException 401: If user not authenticated
        HTTPException 422: If validation fails
        HTTPException 500: If database error occurs
    """
    logger.info(f"User {user_id} creating post with title: {post.title}")

    try:

        new_post = models.Post(
            user_id=user_id,
            **post.model_dump()
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        logger.info(f"Created new post with id: {new_post.id}")
        return new_post

    except Exception as e:
        logger.error(f"Unexpected error creating post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/latest", response_model=schemas.PostResponse)
def get_latest_post(
    db: Session = Depends(get_db_session),
    user_id: UUID = Depends(oauth2.get_current_user)
):
    """Get the most recently created post from the database.
    
    Args:
        db: Database session
        user_id: Current authenticated user's ID
        
    Returns:
        Most recent post object
        
    Raises:
        HTTPException 404: If no posts found
        HTTPException 500: If database error occurs
    """
    try:
        post = db.query(models.Post)\
            .order_by(
                models.Post.created_at.desc(),
                models.Post.id.desc()
            ).first()
        
        if not post:
            logger.info("No posts found in database")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No posts found"
            )
        
        logger.info(f"Retrieved latest post: {post.id}")
        return post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving latest post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the latest post"
        )

    
@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(
    db: Session = Depends(get_db_session), 
    user_id: UUID = Depends(oauth2.get_current_user), 
    limit: int = Query(100, ge=1, le=100), 
    skip: int = Query(0, ge=0),
    title: Optional[str]= Query(
        None,
        description="Filter posts by title"
    )
):
    """Get a specific post by ID from the database.
    
    Args:
        id: Post ID
        db: Database session
        user_id: Current authenticated user's ID
        
    Returns:
        Post object with vote count
        
    Raises:
        HTTPException 404: If post not found
        HTTPException 500: If database error occurs
    """
    logger.info(f"User {user_id} retrieving post {id}")
    
    try:
        # First check if post exists
        post = db.query(models.Post).filter(models.Post.id == id).first()
        
        if not post:
            logger.warning(f"Post not found: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id {id} was not found"
            )
        
        # Get post with vote count
        result = (
            db.query(
                models.Post,
                func.count(models.Vote.post_id).label("votes")
            )
            .join(
                models.Vote,
                models.Vote.post_id == models.Post.id,
                isouter=True
            )
            .filter(models.Post.id == id)
            .group_by(models.Post.id)
            .first()
        )
        
        logger.info(f"Successfully retrieved post {id} with {result.votes} votes")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving post {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the post"
        )


@router.get("/{id}", response_model=schemas.PostResponse)
def get_post(
    id: int, 
    db: Session = Depends(get_db_session),
    user_id: UUID = Depends(oauth2.get_current_user)
):
    """Get a specific post by ID from the database."""
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")

    # Join posts with votes
    result = (
        db.query(
            models.Post,
            func.count(models.Vote.post_id).label("votes")
        )
        .join(
            models.Vote,
            models.Vote.post_id == models.Post.id,
            isouter=True
        )
        .group_by(models.Post.id)
        .first()
    )

    post.votes = result[1]

    return post

@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(
    id: int, 
    post: schemas.UpdatePost, 
    db: Session = Depends(get_db_session),
    user_id: UUID = Depends(oauth2.get_current_user)
):
    """Update a specific post by ID in the database.
    
    Args:
        id: Post ID
        post: Post update data
        db: Database session
        user_id: Current authenticated user's ID
        
    Returns:
        Updated post object
        
    Raises:
        HTTPException 404: If post not found
        HTTPException 403: If user doesn't own the post
        HTTPException 500: If database error occurs
    """
    logger.info(f"User {user_id} updating post {id}")
    
    try:
        post_query = db.query(models.Post).filter(models.Post.id == id)
        existing_post = post_query.first()
        
        if existing_post is None:
            logger.warning(f"Post not found for update: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id {id} does not exist"
            )
        
        # SECURITY FIX: Check ownership
        if existing_post.user_id != user_id:
            logger.warning(f"User {user_id} attempted to update post {id} owned by {existing_post.user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this post"
            )
        
        # Update post
        update_data = post.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_post, key, value)
        
        existing_post.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(existing_post)
        
        logger.info(f"Successfully updated post {id}")
        return existing_post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating post {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int, 
    db: Session = Depends(get_db_session),
    user_id: UUID = Depends(oauth2.get_current_user)
):
    """Delete a specific post by ID from the database."""
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )
    
    if post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )

    post_query.delete(synchronize_session=False)
    db.commit()
    logger.info(f"Deleted post with id: {id}")

    return Response(status_code=status.HTTP_204_NO_CONTENT)