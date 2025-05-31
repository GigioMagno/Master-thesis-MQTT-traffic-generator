#!/bin/bash

cleanup() {
    echo "Stopping generators"
    # Uccidi tutti i processi figli di questo script
    pkill -P $$
    exit 1
}

# Cleanup SIGINT (Ctrl+C)
trap cleanup SIGINT

python Headless_Generator.py -csv ./DoS1.csv -b "127.0.0.1" -p 1883 -i "en0"

wait
echo "All processes stopped"
