# syntax=docker/dockerfile:1
FROM python:3.8

# Install python packages
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Install jq
RUN apt-get -y update && \
    apt-get -y install jq

# Install Rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y && \
    echo 'source $HOME/.cargo/env' >> $HOME/.bashrc
    
# Build sifis-xacml
ADD sifis-xacml /sifis-xacml
RUN cd sifis-xacml && \
    cargo build && \
    cd ..

ADD application_manager /application_manager

ADD run_application_manager/run_manager.sh /
#ADD services/leader_file.txt /  uncomment this to test the run_manager

RUN chmod +x /run_manager.sh
ENTRYPOINT ["./run_manager.sh"]
