FROM python:3

WORKDIR /instructionsservice

ADD . /instructionsservice

RUN pip install -r requirements.txt

EXPOSE 8005

CMD ["uwsgi",  "--http", ":8005",  "--wsgi-file", "__main__.py", "--enable-threads", "--callable", "app"]
