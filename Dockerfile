FROM python:3.8.1

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

RUN mkdir -p /vol/web/media
Run mkdir -p /vol/web/static
RUN chmod -R 755 /vol/web
