# app/services/post_service.py
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.post import Post, PostLike, PostComment
from app.models.group import Group
from app.models.user import User
from app.schemas.post import (
    PostCreate,
    PostSummaryOut,
    PostDetailOut,
    CommentCreate,
    CommentOut,
    LikeOut,
    AuthorInfo,
)


def _build_author_info(user: User) -> AuthorInfo:
    return AuthorInfo(
        id=user.id,
        name=user.name,
        profile_image_url=user.profile_image_url,
    )


def _build_comment_out(comment: PostComment) -> CommentOut:
    return CommentOut(
        id=comment.id,
        author=_build_author_info(comment.author),
        content=comment.content,
        created_at=comment.created_at,
    )


def _get_group_or_404(db: Session, group_id: int) -> Group:
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


# ─────────────────────────────
# 게시글 목록
# ─────────────────────────────
def list_posts(
    db: Session,
    user: User,
    group_id: int,
    from_: int,
    to: int,
) -> List[PostSummaryOut]:
    _get_group_or_404(db, group_id)

    limit = max(0, to - from_ + 1)

    posts: List[Post] = (
        db.query(Post)
        .options(
            joinedload(Post.author),
            joinedload(Post.likes),
            joinedload(Post.comments),
        )
        .filter(Post.group_id == group_id)
        .order_by(Post.created_at.desc())
        .offset(from_)
        .limit(limit)
        .all()
    )

    result: List[PostSummaryOut] = []
    for p in posts:
        like_count = len(p.likes)
        comment_count = len(p.comments)
        is_liked = any(l.user_id == user.id for l in p.likes)

        result.append(
            PostSummaryOut(
                id=p.id,
                group_id=p.group_id,
                title=p.title,
                content=p.content,
                author=_build_author_info(p.author),
                created_at=p.created_at,
                like_count=like_count,
                comment_count=comment_count,
                is_liked=is_liked,
            )
        )

    return result


# ─────────────────────────────
# 게시글 생성
# ─────────────────────────────
def create_post(
    db: Session,
    user: User,
    group_id: int,
    body: PostCreate,
) -> PostDetailOut:
    _get_group_or_404(db, group_id)

    post = Post(
        group_id=group_id,
        author_id=user.id,
        title=body.title,
        content=body.content,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return PostDetailOut(
        id=post.id,
        group_id=post.group_id,
        title=post.title,
        content=post.content,
        author=_build_author_info(user),
        created_at=post.created_at,
        like_count=0,
        is_liked=False,
        comments=[],
    )


# ─────────────────────────────
# 게시글 상세
# ─────────────────────────────
def get_post_detail(
    db: Session,
    user: User,
    group_id: int,
    post_id: int,
) -> PostDetailOut:
    post: Post | None = (
        db.query(Post)
        .options(
            joinedload(Post.author),
            joinedload(Post.likes),
            joinedload(Post.comments).joinedload(PostComment.author),
        )
        .filter(Post.group_id == group_id, Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    like_count = len(post.likes)
    is_liked = any(l.user_id == user.id for l in post.likes)
    comments_out = [_build_comment_out(c) for c in post.comments]

    return PostDetailOut(
        id=post.id,
        group_id=post.group_id,
        title=post.title,
        content=post.content,
        author=_build_author_info(post.author),
        created_at=post.created_at,
        like_count=like_count,
        is_liked=is_liked,
        comments=comments_out,
    )


# ─────────────────────────────
# 좋아요 토글
# ─────────────────────────────
def toggle_like(
    db: Session,
    user: User,
    group_id: int,
    post_id: int,
) -> LikeOut:
    post = (
        db.query(Post)
        .filter(Post.group_id == group_id, Post.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = (
        db.query(PostLike)
        .filter(PostLike.post_id == post_id, PostLike.user_id == user.id)
        .first()
    )

    if existing:
        db.delete(existing)
        liked = False
    else:
        like = PostLike(post_id=post_id, user_id=user.id)
        db.add(like)
        liked = True

    db.commit()

    like_count = (
        db.query(PostLike).filter(PostLike.post_id == post_id).count()
    )

    return LikeOut(liked=liked, like_count=like_count)


# ─────────────────────────────
# 댓글 생성
# ─────────────────────────────
def create_comment(
    db: Session,
    user: User,
    group_id: int,
    post_id: int,
    body: CommentCreate,
) -> CommentOut:
    post = (
        db.query(Post)
        .filter(Post.group_id == group_id, Post.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = PostComment(
        post_id=post_id,
        author_id=user.id,
        content=body.content,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return _build_comment_out(comment)


# ─────────────────────────────
# 댓글 목록
# ─────────────────────────────
def list_comments(
    db: Session,
    user: User,   # 사용 여부 상관없이 형태 통일용
    group_id: int,
    post_id: int,
) -> List[CommentOut]:
    post = (
        db.query(Post)
        .filter(Post.group_id == group_id, Post.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comments: List[PostComment] = (
        db.query(PostComment)
        .options(joinedload(PostComment.author))
        .filter(PostComment.post_id == post_id)
        .order_by(PostComment.created_at.asc())
        .all()
    )

    return [_build_comment_out(c) for c in comments]


# ─────────────────────────────
# 댓글 삭제
# ─────────────────────────────
def delete_comment(
    db: Session,
    user: User,
    group_id: int,
    post_id: int,
    comment_id: int,
) -> None:
    comment: PostComment | None = (
        db.query(PostComment)
        .join(Post, Post.id == PostComment.post_id)
        .filter(
            Post.group_id == group_id,
            Post.id == post_id,
            PostComment.id == comment_id,
        )
        .first()
    )

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this comment",
        )

    db.delete(comment)
    db.commit()
