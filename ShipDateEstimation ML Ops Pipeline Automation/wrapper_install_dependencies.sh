#! /bin/bash
VIRTUAL_ENVIRONMENT_DIRECTORY="$1"
cd ~
sudo cp /home/TimeZoneFetchByLatLong.py .
sudo chmod 755 *
sudo apt-get update
sudo apt-get install python3.8
python3 --version
sudo apt-get -o Dpkg::Options::=--force-confnew -y --allow-downgrades --allow-remove-essential --allow-change-held-packages install python3-requests
sudo apt-get -o Dpkg::Options::=--force-confnew -y --allow-downgrades --allow-remove-essential --allow-change-held-packages install python3-pip
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip --version
python3 -m venv ${VIRTUAL_ENVIRONMENT_DIRECTORY}
source ${VIRTUAL_ENVIRONMENT_DIRECTORY}/bin/activate
python3 -m pip install --upgrade 'google-cloud-bigquery[bqstorage,pandas]'
python3 -m pip install --upgrade timezonefinder
python3 TimeZoneFetchByLatLong.py