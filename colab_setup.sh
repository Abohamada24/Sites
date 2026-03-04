#!/bin/bash

# Installation Script for Google Colab

# Update package list
sudo apt update

# Install required packages
sudo apt install -y python3 python3-pip

# Optionally, install other dependencies as needed
# For example, if you need TensorFlow and NumPy
pip3 install tensorflow numpy

# Instructions to run this script:
# 1. Open a shell in your Google Colab environment.
# 2. Navigate to the directory where you want to store this script.
# 3. Use the command `bash colab_setup.sh` to execute the setup.

echo "Google Colab setup script executed successfully!"