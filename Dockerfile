# pull official base image
FROM python:3.8-alpine
CMD pwd && ls
# set work directory
WORKDIR /AIS_backend/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev python3-dev gcc  musl-dev libffi-dev


RUN apk add --no-cache geos gdal
RUN apk add --no-cache gdal-dev
RUN apk add --no-cache build-base
RUN apk add --no-cache zlib

RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal
RUN export LDFLAGS="-L/usr/local/opt/zlib/lib"
RUN export CPPFLAGS="-I/usr/local/opt/zlib/include"
# install dependencies





RUN pip install --upgrade pip
COPY ./requirement.txt .
RUN pip install -r requirement.txt

# copy project
CMD ["python","manage.py", "migrate", "0:8000"]
COPY . .