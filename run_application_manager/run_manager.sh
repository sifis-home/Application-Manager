#!/bin/bash

#leader_file="leader_file.txt" uncomment this to test the run_manager

leader_file="/services/leader_file.txt"  #uncomment this to test the run_manager
catch_topic_script="/usr/local/bin/python3 /application_manager/catch_topic.py"

if [ -e "$leader_file" ]; then
    $catch_topic_script
else
    echo "Leader file not present."
fi
