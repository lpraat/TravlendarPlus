FROM python:3

WORKDIR /computeservice

ADD . /computeservice

RUN pip install -r requirements.txt

EXPOSE 8006

CMD ["uwsgi",  "--http", ":8006",  "--wsgi-file", "__main__.py", "--enable-threads", "--callable", "app"]
