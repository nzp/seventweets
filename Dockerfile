FROM python:3

RUN mkdir -p /usr/src/app/seventweets
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt
COPY seventweets /usr/src/app/seventweets/
COPY gunicorn_config.py /usr/src/app/

ENV GUNICORN_CMD_ARGS "-c /usr/src/app/gunicorn_config.py"

CMD ["gunicorn", "seventweets.node:app"]
