FROM python:3.8.13

ARG DB_PASSWORD

ENV DB_PASSWORD $DB_PASSWORD

WORKDIR /app

RUN pip install uv && \
    uv pip install --system beautifulsoup4==4.12.3 \
    selenium==4.25.0 \
    webdriver-manager==4.0.2 \
    loguru==0.7.2 \
    sqlalchemy==2.0.36 \
    psycopg2-binary==2.9.9 \
    fastapi==0.115.2 \
    uvicorn==0.32.0 

COPY . .    

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1"]