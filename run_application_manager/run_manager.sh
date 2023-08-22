#!/bin/bash

leader_file="services/leader_file.txt"
catch_topic_script="/usr/local/bin/python3 /catch_topic.py"

if [ -e "$leader_file" ]; then
    $catch_topic_script
else
    echo "Leader file not present."
fi
