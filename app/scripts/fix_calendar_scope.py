from app.database import SessionLocal
from app.models.calendar import UserEvent  # 너가 올린 UserEvent 모델 그대로

def main() -> None:
    db = SessionLocal()

    # 소문자 'personal' -> 대문자 'PERSONAL'
    db.query(UserEvent).filter(UserEvent.scope == "personal").update(
        {UserEvent.scope: "PERSONAL"},
        synchronize_session=False,
    )

    # 혹시 'group'도 소문자로 남아 있다면 같이 정리
    db.query(UserEvent).filter(UserEvent.scope == "group").update(
        {UserEvent.scope: "GROUP"},
        synchronize_session=False,
    )

    db.commit()
    db.close()
    print("calendar_event_scope 정리 완료")

if __name__ == "__main__":
    main()
