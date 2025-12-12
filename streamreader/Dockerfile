# currently under development
# C. Lechner, 2025-12

FROM ubuntu:24.04

ARG GIT_INFO=unspecified

# Ubuntu 24.04 enforces PEP 668, which prevents system-wide pip installations.
# Prevents system-wide installations with pip3 (a good idea...), solutions are
# (a) virtual environment or
# (b) pip3 argument --break-system-packages

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# create virtual environment and activate it
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . /app/

# Write git commit ID only quite late in the process (in Docker's layering approach every RUN generates another layer). The git commit ID is expected to change more often than (for instance) Debian packages...
RUN echo "$GIT_INFO" > /app/git_info.txt

# safe default UID
USER nobody

WORKDIR /app

VOLUME ["/data"]
EXPOSE 8080

ENV PYTHONUNBUFFERED=1

# CMD ["/bin/bash"]
CMD ["./wikistreamreader.py", "--outdir=/data/", "--status_port=8080"]
