FROM python:3.6-alpine
COPY . /app
WORKDIR /app
RUN apk add gcc musl-dev libffi-dev libressl-dev
RUN pip install pipenv
RUN pipenv install
CMD pipenv run prod
