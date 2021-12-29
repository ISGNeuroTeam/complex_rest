#! /bin/sh

# must be launched from repo root directory with downloaded unit and kafka.tgz

echo Create venv
cd unit
conda create --copy -p ./venv -y
conda install -p ./venv python==3.9.7 -y
conda install -p ./venv redis -y
conda install -p ./venv postgresql==12.9 -y
conda install -p ./venv pcre2 -y
./venv/bin/pip install --no-input  -r ../requirements.txt

# build nginx unit in conda venv
./configure --prefix=venv --no-regex
./configure python --config=venv/bin/python3.9-config --module=python3.9 --lib-path=venv/lib/libpython3.so

make
make install

# kafka
mkdir ./venv/apps
tar zxf ../kafka.tar.gz -C ./venv/apps/

