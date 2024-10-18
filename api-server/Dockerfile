FROM python:3.8.13

ARG DB_PASSWORD

ENV DB_PASSWORD $DB_PASSWORD
ENV OPENAI_API_KEY $OPENAI_API_KEY
ENV DB_PASSWORD $DB_PASSWORD

WORKDIR /app

RUN pip install uv && \
    uv pip install --system beautifulsoup4==4.12.3 \
    selenium==4.25.0 \
    webdriver-manager==4.0.2 \
    loguru==0.7.2 \
    sqlalchemy==2.0.36 \
    fastapi==0.115.2 \
    uvicorn==0.32.0 \
    asyncpg==0.29.0 \
    greenlet==3.1.1 \
    openai==1.51.2 \
    tqdm==4.62.3 

COPY . .    

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1"]