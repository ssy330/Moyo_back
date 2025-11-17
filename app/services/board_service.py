import os
import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.group import Group
from app.models.board_registry import BoardRegistry
#from app.core.config import settings


RHYMIX_BASE = os.getenv("RHYMIX_BASE_URL", "http://localhost:3000").rstrip("/")

def build_mid(group_id: int) -> str:
    return f"group_{group_id}_board"   # 규칙만 정해두기

def build_url(mid: str) -> str:
    # 짧은 주소 기준
    return f"{RHYMIX_BASE}/{mid}"

def build_url_from_group_id(group_id: int) -> str:
    mid = build_mid(group_id)
    return build_url(mid)

async def head_ok(url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.head(url, follow_redirects=True)
            return r.status_code < 400
    except Exception:
        return False

async def upsert_mapping(db: Session, group_id: int, mid: str) -> tuple[BoardRegistry, int]:
    # 1) 그룹 존재 확인
    exists = db.scalar(select(func.count()).select_from(Group).where(Group.id == group_id))
    if not exists:
        raise HTTPException(status_code=404, detail="Group not found")

    # 2) mid 중복(다른 그룹에서 사용) 방지
    conflict = db.scalar(
        select(func.count()).select_from(BoardRegistry)
        .where(BoardRegistry.mid == mid, BoardRegistry.group_id != group_id)
    )
    if conflict:
        raise HTTPException(status_code=409, detail="This mid is already mapped to another group")

    # 3) upsert
    row = db.scalar(select(BoardRegistry).where(BoardRegistry.group_id == group_id))
    if row:
        row.mid = mid
        db.commit(); db.refresh(row)
        return row, 200  # updated
    else:
        row = BoardRegistry(group_id=group_id, mid=mid)
        db.add(row); db.commit(); db.refresh(row)
        return row, 201  # created

def get_mapping(db: Session, group_id: int) -> BoardRegistry | None:
    return db.scalar(select(BoardRegistry).where(BoardRegistry.group_id == group_id))




async def url_exists(url: str) -> bool:
    timeout = httpx.Timeout(connect=3.0, read=3.0, write=3.0, pool=3.0)
    headers = {"User-Agent": "moyo/board-check"}
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
            r = await client.head(url)
            if r.status_code in (200, 204, 206, 301, 302, 304, 307, 308):
                return True
            if r.status_code in (403, 405):
                r = await client.get(url, headers={**headers, "Range": "bytes=0-0"})
                if r.status_code in (200, 206, 301, 302, 304, 307, 308):
                    return True
            if 400 <= r.status_code < 500 and r.status_code != 404:
                return True
            return False
    except httpx.RequestError:
        return False