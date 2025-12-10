FROM ubuntu:24.04


# Ubuntu 24.04 enforces PEP 668, which prevents system-wide pip installations.
# Prevents system-wide installations with pip3 (a good idea...), solutions are
# (a) virtual environment or
# (b) pip3 argument --break-system-packages

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-venv

# create virtual environment and activate it
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . /app/

# safe default UID
USER nobody

WORKDIR /app

VOLUME ["/data"]
EXPOSE 8080


# CMD ["/bin/bash"]
CMD ["./wikistreamreader.py", "--outdir=/data/", "--status_port=8080"]
