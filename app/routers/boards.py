from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
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
    row = board_service.get_mapping(db, group_id)
    if not row:
        raise HTTPException(status_code=404, detail="BOARD_NOT_MAPPED")
    url = board_service.build_url(row.mid)
    exists = await board_service.head_ok(url)
    return BoardMapOut(groupId=group_id, mid=row.mid, url=url, exists=exists)
