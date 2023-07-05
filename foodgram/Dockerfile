FROM python:3.9

RUN apt-get update &&\
    apt-get upgrade -y &&\
    apt-get install -y libpq-dev gcc netcat-traditional

WORKDIR /app

COPY requirements.txt .

RUN pip install -U pip &&\
    pip install -r requirements.txt --no-cache-dir

COPY . .

ADD foodgram_entrypoint.sh /foodgram_entrypoint.sh

RUN chmod a+x /foodgram_entrypoint.sh

ENTRYPOINT ["/foodgram_entrypoint.sh"]
