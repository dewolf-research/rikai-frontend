FROM ubuntu:latest

RUN apt-get update && \
    apt-get install --no-install-recommends -y default-jre python3 python3-pip curl unzip && \
    apt-get clean

COPY . /opt/rikai

WORKDIR /opt/rikai

RUN sh /opt/rikai/setup.sh
RUN pip install -r /opt/rikai/requirements.txt

RUN chmod +x /opt/rikai/rikai-cmd.py
ENTRYPOINT ["/bin/bash"]