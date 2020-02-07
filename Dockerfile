FROM ehdgnv/bns-django:1.0


WORKDIR /bns
ADD    . /bns/

RUN    pip3.6 install --no-cache-dir -r requirements.txt


EXPOSE 80 465

CMD ["uwsgi", "--plugins", "http,python", \
              "--http", "0.0.0.0:80", \
              "--wsgi-file", "/bns/buynsell/wsgi.py", \
              "--master", \
              "--die-on-term", \
              "--single-interpreter", \
              "--harakiri", "30", \
              "--reload-on-rss", "512", \
              "--post-buffering-bufsize", "8192", \
              "--enable-threads"]


