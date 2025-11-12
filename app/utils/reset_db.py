# DB 데이터 다 날리고 재생성 하는 유틸 스크립트 입니다.

from app.database import Base, engine
# ⚠️ 모든 모델 모듈을 import 해서 메타데이터에 등록되게 해야 함
from app.models import user, group, group_member, board_registry, invite, email_verification

if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("DB reset & recreated ✅")
