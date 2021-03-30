FROM ubuntu:18.04

# Install dependencies

RUN apt-get update && apt-get install -y \
    software-properties-common
ENV DEBIAN_FRONTEND noninteractive
RUN add-apt-repository universe
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y \
    apache2 \
    curl \
    git \
    python3.7.2 \
    python3-pip


# Install chinese fonts, then update the font-cache.
# Based on: http://cnedelcu.blogspot.com/2015/04/wkhtmltopdf-chinese-character-support.html
RUN apt-get update && apt-get install --no-install-recommends -yq \
    fonts-wqy-microhei \
    ttf-wqy-microhei \
    fonts-wqy-zenhei \
    ttf-wqy-zenhei
RUN fc-cache -f -v


RUN sed 's/main$/main universe/' -i /etc/apt/sources.list
RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y build-essential xorg libssl-dev libxrender-dev wget gdebi

RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb
RUN gdebi --n wkhtmltox_0.12.5-1.bionic_amd64.deb





RUN mkdir -p /zendesk-utils
COPY requirements.txt /zendesk-utils
RUN pip3 install -r /zendesk-utils/requirements.txt

ENV PYTHONPATH /zendesk-utils:/zendesk-utils/helpcenter_to_pdf:/zendesk-utils/to_json:/zendesk-utils/localize:$PYTHONPATH

ENV LC_ALL=en_CA.UTF-8
ENV LANG=en_CA.UTF-8
ENV LANGUAGE=en_CA.UTF-8

COPY . /zendesk-utils
WORKDIR /zendesk-utils

CMD [ "python3", "./starter.py", "run"]
