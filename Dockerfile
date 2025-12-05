# Python 3.11 slim 이미지 사용
FROM python:3.11-slim

# 컨테이너 안 작업 디렉토리
WORKDIR /app

# 파이썬이 .pyc 안 만들고, 버퍼링 없이 로그 찍도록
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 파이썬 라이브러리 설치
COPY requirements.txt .
RUN pip install --upgrade pip &&  pip install --no-cache-dir -r requirements.txt

# OS 패키지 먼저 설치 (tzdata + Postgres용 라이브러리)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tzdata \
        build-essential \
        libpq-dev && \
    ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 실제 프로젝트 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONPATH=/app/src

# FastAPI 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
