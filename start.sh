#!/bin/bash

set -exo pipefail

source defense_venv/bin/activate

pushd DefenseLab
    echo "Logging DefenseLab.py output to defense_log.txt"
    nohup python DefenseLab.py >> defense_log.txt 2>&1 &
popd

pushd DefenseLab/FileServer
    echo "Logging FileServer serve.py output to fileserver_log.txt"
    nohup python serve.py >> ../fileserver_log.txt 2>&1 &
popd
