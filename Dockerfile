FROM python:2

RUN useradd -u 999 -ms /bin/bash appuser

RUN apt-get update && \
   apt-get install -y python curl unzip nginx
ENV PYTHONUNBUFFERED 1
RUN mkdir /boxee
WORKDIR /boxee

ADD ./requirements.txt /boxee
RUN pip install -r requirements.txt
ADD . /boxee

RUN mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled /var/cache/nginx

ENTRYPOINT ["./docker-entrypoint.sh"]
