FROM python:3.6-alpine

ENV MYSQL_HOSTNAME=db
ENV MYSQL_PORT=3306
ENV MYSQL_USERNAME=challenges
ENV MYSQL_DATABASE=challenges
ENV SMTP_HOSTNAME=the-morpheus.de
ENV SMTP_PORT=587
ENV SMTP_USERNAME=challenge

EXPOSE 80

COPY . /app
WORKDIR /app
RUN apk add gcc musl-dev libffi-dev libressl-dev
RUN pip install pipenv
RUN pipenv run pip install pip==18.0  # bugfix for pipenv issue #2924
RUN pipenv install
CMD pipenv run prod
