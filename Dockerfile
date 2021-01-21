FROM python:3.8.1

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
ADD ./dockerfile_requirements.txt /code/
RUN pip install --upgrade pip && \
    pip install -r dockerfile_requirements.txt
ADD . /code/
