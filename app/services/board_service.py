import os
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.board_registry import BoardRegistry
#from app.core.config import settings


RHYMIX_BASE = os.getenv("RHYMIX_BASE_URL", "http://localhost:3000").rstrip("/")

def build_url(mid: str) -> str:
    # 짧은 주소 기준
    return f"{RHYMIX_BASE}/{mid}"

async def head_ok(url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.head(url, follow_redirects=True)
            return r.status_code < 400
    except Exception:
        return False

def upsert_mapping(db: Session, group_id: int, mid: str) -> BoardRegistry:
    row = db.scalar(select(BoardRegistry).where(BoardRegistry.group_id == group_id))
    if row:
        row.mid = mid
    else:
        row = BoardRegistry(group_id=group_id, mid=mid)
        db.add(row)
    db.commit()
    db.refresh(row)
    return row

def get_mapping(db: Session, group_id: int) -> BoardRegistry | None:
    return db.scalar(select(BoardRegistry).where(BoardRegistry.group_id == group_id))

async def url_exists(url: str) -> bool:
    timeout = httpx.Timeout(connect=3.0, read=3.0, write=3.0, pool=3.0)
    headers = {"User-Agent": "moyo/board-check"}
    
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
            # 1) 먼저 HEAD
            r = await client.head(url)
            if r.status_code in (200, 204, 206, 301, 302, 304, 307, 308):
                return True
            # 일부 PHP/Apache가 HEAD를 405/403으로 막는 경우
            if r.status_code in (403, 405):
                r = await client.get(url, headers={**headers, "Range": "bytes=0-0"})
                if r.status_code in (200, 206, 301, 302, 304, 307, 308):
                    return True
            # 4xx라도 404가 아니면 페이지는 존재하는데 접근 제약일 수 있음 → 존재로 간주
            if 400 <= r.status_code < 500 and r.status_code != 404:
                return True
            return False
    except httpx.RequestError:
        return False