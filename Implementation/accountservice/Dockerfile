FROM python:3

WORKDIR /accountservice

ADD . /accountservice

RUN pip install -r requirements.txt

EXPOSE 8002

CMD ["uwsgi",  "--http", ":8002",  "--wsgi-file", "accountservice.py", "--enable-threads", "--callable", "accountservice"]