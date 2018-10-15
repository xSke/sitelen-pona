FROM python:alpine

# App/Python dependencies
RUN apk add --no-cache build-base freetype-dev harfbuzz-dev fribidi-dev zlib-dev jpeg-dev

# Alpine doesn't have a package for libraqm, so we build it ourselves
WORKDIR /raqm
RUN apk add --no-cache autoconf automake gtk-doc libtool git \
    && git clone https://github.com/HOST-Oman/libraqm/ . \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install \
    && rm -r /raqm \
    && apk del --no-cache autoconf automake gtk-doc libtool git

# The app itself
WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt && pip install gunicorn

ADD . /app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "sitelen:app"]