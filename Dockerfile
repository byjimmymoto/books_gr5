FROM python:3.7-slim

RUN apt-get -y update && apt-get install -y --no-install-recommends libpq-dev gcc g++ build-essential openssl screen
RUN mkdir /book_gr5

COPY ./app /book_gr5/app

COPY ./service.sh /book_gr5/app/service.sh

RUN chmod +x /book_gr5/app/service.sh

WORKDIR /book_gr5/app

COPY ./requirements.txt /book_gr5/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /book_gr5/requirements.txt

CMD ["/book_gr5/app/service.sh"]
