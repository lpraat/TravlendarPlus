FROM python:3

WORKDIR /eventservice

ADD . /eventservice

RUN pip install -r requirements.txt

EXPOSE 8004

CMD ["uwsgi",  "--http", ":8004",  "--wsgi-file", "eventservice.py", "--enable-threads", "--callable", "eventservice"]