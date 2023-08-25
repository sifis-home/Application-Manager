# syntax=docker/dockerfile:1
FROM python:3.8

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

ADD application_manager/*.py /
ADD application_manager/get-labels.sh /

ADD run_application_manager/run_manager.sh /
ADD sifis-xacml /
#ADD services/leader_file.txt /  uncomment this to test the run_manager

RUN chmod +x /run_manager.sh
ENTRYPOINT ["./run_manager.sh"]



