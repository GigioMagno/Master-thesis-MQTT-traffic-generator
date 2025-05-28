#!/bin/bash

N=5  # Numero di processi da avviare in parallelo

cleanup() {
    echo "Stopping generators"
    # Uccidi tutti i processi figli di questo script
    pkill -P $$
    exit 1
}

# Cleanup SIGINT (Ctrl+C)
trap cleanup SIGINT

for ((i=1; i<=N; i++))
do
  echo "Running process: $i"
  python Headless_Generator.py -csv ./quadDosHeavyPyaload.csv -b "127.0.0.1" -p 1883 -i "en0" &
done

wait
echo "All processes stopped"
