# syntax=docker/dockerfile:1
FROM python:3.8

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

ADD application_manager/*.py /

ADD run_application_manager/run_manager.sh /
ADD services/leader_file.txt /

RUN chmod +x /run_manager.sh
ENTRYPOINT ["./run_manager.sh"]

#ENTRYPOINT ["/usr/local/bin/python3", "/catch_topic.py"]


