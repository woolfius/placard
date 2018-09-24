FROM python:3

MAINTAINER Reverenda Marian


RUN  mkdir /bm_hr_portal
WORKDIR /bm_hr_portal
COPY requirements.txt .

RUN  pip install --upgrade pip && \
     pip install -r requirements.txt
RUN  sed -ie 's/socket \%s:\%d/socket \%s:\%s/g' /usr/local/lib/python3.6/site-packages/pymysql/connections.py

COPY . /bm_hr_portal

EXPOSE 5555

CMD python3 -u server.py

