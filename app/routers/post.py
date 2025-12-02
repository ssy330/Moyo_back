# app/routers/post.py
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.deps.auth import current_user
from app.schemas.post import (
    PostCreate,
    PostSummaryOut,
    PostDetailOut,
    CommentCreate,
    CommentOut,
    LikeOut,
)
from app.services import post_service

router = APIRouter(prefix="/groups/{group_id}/posts", tags=["posts"])


# 게시글 목록
@router.get("", response_model=List[PostSummaryOut])
def list_posts(
    group_id: int,
    from_: int = 0,
    to: int = 19,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return post_service.list_posts(
        db=db,
        user=user,
        group_id=group_id,
        from_=from_,
        to=to,
    )


# 게시글 생성
@router.post("", response_model=PostDetailOut, status_code=status.HTTP_201_CREATED)
def create_post(
    group_id: int,
    body: PostCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return post_service.create_post(
        db=db,
        user=user,
        group_id=group_id,
        body=body,
    )


# 게시글 상세 조회
@router.get("/{post_id}", response_model=PostDetailOut)
def get_post_detail(
    group_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return post_service.get_post_detail(
        db=db,
        user=user,
        group_id=group_id,
        post_id=post_id,
    )


# 좋아요 토글
@router.post("/{post_id}/likes", response_model=LikeOut)
def toggle_like(
    group_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return post_service.toggle_like(
        db=db,
        user=user,
        group_id=group_id,
        post_id=post_id,
    )


# 댓글 생성
@router.post(
    "/{post_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    group_id: int,
    post_id: int,
    body: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return post_service.create_comment(
        db=db,
        user=user,
        group_id=group_id,
        post_id=post_id,
        body=body,
    )


# 댓글 목록
@router.get("/{post_id}/comments", response_model=List[CommentOut])
def list_comments(
    group_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return post_service.list_comments(
        db=db,
        user=user,
        group_id=group_id,
        post_id=post_id,
    )


# 댓글 삭제
@router.delete(
    "/{post_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    group_id: int,
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    post_service.delete_comment(
        db=db,
        user=user,
        group_id=group_id,
        post_id=post_id,
        comment_id=comment_id,
    )

# 게시글 삭제
@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_post(
    group_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    post_service.delete_post(
        db=db,
        user=user,
        group_id=group_id,
        post_id=post_id,
    )
