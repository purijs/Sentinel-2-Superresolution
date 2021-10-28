#!/bin/bash

source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
cd /home/ubuntu/digisat
conda activate tensorflow2_p37
export FLASK_APP=app.py
nohup flask run --host 0.0.0.0 &