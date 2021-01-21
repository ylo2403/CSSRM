FROM python:3.6.5

WORKDIR /usr/src/bloxlink

ADD . /usr/src/bloxlink

RUN apt-get update

RUN wget -O - https://github.com/jemalloc/jemalloc/releases/download/5.2.1/jemalloc-5.2.1.tar.bz2 | tar -xj && \
    cd jemalloc-5.2.1 && \
    ./configure && \
    make && \
    make install

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt
RUN apt install dumb-init

ENV LD_PRELOAD="lib/libjemalloc.so.2"
#/usr/local/lib
# lib/libjemalloc.so.2

ENTRYPOINT ["dumb-init", "-v", "--", "python3", "src/bot.py"]