from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.group import Group
from app.schemas.board import BoardMapIn, BoardMapOut
from app.services import board_service
from fastapi.responses import JSONResponse
# from app.security import require_role  # 프로젝트에 권한 데코레이터 있으면 사용

router = APIRouter(prefix="/boards", tags=["boards"])

@router.put("/groups/{group_id}/mapping", response_model=BoardMapOut, status_code=201)
async def put_mapping(group_id: int, body: BoardMapIn, db: Session = Depends(get_db)):
    row, code = await board_service.upsert_mapping(db, group_id, body.mid)
    url = board_service.build_url(row.mid)
    exists = await board_service.url_exists(url)  # 여전히 선택적 검사
    return JSONResponse(
        status_code=code,
        content={"groupId": group_id, "mid": row.mid, "url": url, "exists": exists},
    )
# 권한 필요하면: dependencies=[Depends(require_role(["SERVICE_ADMIN", "OWNER"]))]

@router.get("/groups/{group_id}/url", response_model=BoardMapOut)
async def get_url(group_id: int, db: Session = Depends(get_db)):
   # 1) 그룹이 실제로 존재하는지만 확인
    exists = db.scalar(
        select(func.count()).select_from(Group).where(Group.id == group_id)
    )
    if not exists:
        raise HTTPException(status_code=404, detail="Group not found")

    # 2) group_id 기반으로 mid / url 계산
    mid = board_service.build_mid(group_id)
    url = board_service.build_url_from_group_id(group_id)
    exists_flag = await board_service.url_exists(url)

    return BoardMapOut(groupId=group_id, mid=mid, url=url, exists=exists_flag)