FROM bitnami/python:3.9-debian-11


RUN  apt update \
    && apt-get -y install netcat \
    && apt-get -y install telnet


# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# run entrypoint.prod.sh
ENTRYPOINT ["sh", "/usr/src/app/entrypoint.sh"]