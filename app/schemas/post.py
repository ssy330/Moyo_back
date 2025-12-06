# app/schemas/post.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


# ▶ 기존 PostCreate 그대로 두고 써도 됨
class PostCreate(BaseModel):
    title: str
    content: str
    # 이미지 URL 여러 개를 미리 받을 거라면:
    image_urls: Optional[List[str]] = None


class PostOut(BaseModel):
    id: int
    group_id: int
    author_id: int
    title: str
    content: str
    created_at: datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)


# 👤 작성자 정보 (UI용)
class AuthorInfo(BaseModel):
    id: int
    name: str
    profile_image_url: Optional[str] = None


# 💬 댓글
class CommentCreate(BaseModel):
    content: str


class CommentOut(BaseModel):
    id: int
    author: AuthorInfo
    content: str
    created_at: datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)


# ❤️ 좋아요
class LikeOut(BaseModel):
    liked: bool
    like_count: int


# 📝 게시글 목록용(요약)
class PostSummaryOut(BaseModel):
    id: int
    group_id: int
    title: str
    content: str  # or snippet
    author: AuthorInfo
    created_at: datetime
    like_count: int
    comment_count: int
    is_liked: bool = False  # 현재 로그인 유저가 좋아요 눌렀는지
    image_urls: List[str] = []

    class Config:
        model_config = ConfigDict(from_attributes=True)


# 📄 게시글 상세용
class PostDetailOut(BaseModel):
    id: int
    group_id: int
    title: str
    content: str
    author: AuthorInfo
    created_at: datetime
    like_count: int
    is_liked: bool
    comments: List[CommentOut] = []
    image_urls: List[str] = []

    class Config:
        model_config = ConfigDict(from_attributes=True)
