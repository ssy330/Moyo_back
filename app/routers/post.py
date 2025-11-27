# app/routers/post.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.post import Post
from app.models.group import Group
from app.models.user import User
from app.schemas.post import PostCreate, PostOut
from app.deps.auth import current_user  # 이미 로그인용 의존성 있을 거라 가정

router = APIRouter(prefix="/groups/{group_id}/posts", tags=["posts"])


@router.get("", response_model=List[PostOut])
def list_posts(
    group_id: int,
    from_: int = 0,
    to: int = 19,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    # (선택) 이 유저가 이 그룹에 속해있는지 체크하고 싶으면 여기서 검사

    limit = max(0, to - from_ + 1)

    query = (
        db.query(Post)
        .filter(Post.group_id == group_id)
        .order_by(Post.created_at.desc())
        .offset(from_)
        .limit(limit)
    )

    return query.all()


@router.post("", response_model=PostOut, status_code=201)
def create_post(
    group_id: int,
    body: PostCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    # (선택) group 존재 여부 확인
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    post = Post(
        group_id=group_id,
        author_id=user.id,
        title=body.title,
        content=body.content,
    )

    db.add(post)
    db.commit()
    db.refresh(post)
    return post
