FROM python:3.11.10 as builder-base

RUN apt-get update -y && curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.8.4 python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /root/sa_naver_rlhf
COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && poetry lock --no-update
RUN poetry install

# 최종 애플리케이션 빌드 스테이지
FROM builder-base AS app

ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


RUN apt-get update -y
WORKDIR /root/sa_naver_rlhf

# 의존성 설치 스테이지에서 설치한 의존성 복사
COPY ./web /root/sa_naver_rlhf

ARG DATASET_API_URL
ENV DATASET_API_URL=$DATASET_API_URL

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/_stcore/health

CMD ["streamlit", "run", "main.py", "--server.port", "8000", "--server.address", "0.0.0.0", "--client.toolbarMode", "minimal", "--theme.base", "light"]
