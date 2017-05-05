FROM python:3

RUN mkdir -p /usr/src/app/seventweets
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt
COPY seventweets /usr/src/app/seventweets/

ENV GUNICORN_CMD_ARGS "--bind=0:8000 --worker-class=gthread --threads=10"

CMD ["gunicorn", "seventweets.node:app"]
