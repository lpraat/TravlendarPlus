FROM python:3

WORKDIR /calendarservice

ADD . /calendarservice

RUN pip install -r requirements.txt

EXPOSE 8003

CMD ["uwsgi",  "--http", ":8003",  "--wsgi-file", "calendarservice.py", "--enable-threads", "--callable", "calendarservice"]