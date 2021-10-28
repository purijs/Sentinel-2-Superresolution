# Sentinel-2 Band Pan-Sharpening
Deploy the Sentinel-2 Band Enhancement model using Flask and Leaflet

## Introduction

This is a state of the art [Convolutional Neural Network](https://en.wikipedia.org/wiki/Convolutional_neural_network)
algorithm to derive higher resolution images from existing lower resolution images using Sentinel-2 datasets as input.
The code is adapted from https://github.com/lanha/DSen2 and is an extension for GUI interface and model deployment using Flask

**Input**: AOI

**Output**: Sentinel-2 Bands at 10m

![Final Step Output](https://github.com/purijs/Sentinel-2-Superresolution/blob/main/git_view.PNG)

## Requirements

This example requires the **Ubuntu 16**.
 - Tensorflow 2 GPU
 - Python 3.7

Ideal EC2 Instances
 - g4dn.4xlarge
 - p2.xlarge
 
Ideal System Config
 - 64 GB Mem
 - 12 GB GPU

## Instructions

The applications will run through `Flask` and the processing time depends on `Network Speed` and `GPU/RAM`
 - Clone the repo
 - Move `Sentinel_2A_PS` to home directory (`/home/ubuntu`)
 - `mkdir -p /home/ubuntu/digisat`
 - Move the other 3 files from repo to `digisat`
 ` Move `init.sh` to `/home/ubuntu/`
 - Give permissions to `init.sh` using `sudo chmod 755 init.sh`
 - Run `./init.sh`
 
The applications should be hosted at `http://<your_ip>:5000`
