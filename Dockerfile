FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y gnupg\
    && apt-get install -y wget \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -\
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'\
    && apt-get -y update\
    && apt-get install -y google-chrome-stable

COPY . .

RUN pip install -r requirements.txt

CMD [ "python","-m","asos.asos_scraper" ]
