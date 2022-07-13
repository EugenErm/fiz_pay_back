FROM bitnami/python:3.9-debian-11

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN ["chmod", "+x", "/usr/src/app/entrypoint.sh"]
/usr/src/app/entrypoint.sh

# copy project
COPY . .
# run entrypoint.prod.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]