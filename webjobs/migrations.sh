#!/bin/bash

echo "== cd ~/site/wwwroot/env/Scripts; ls =="
cd ~/site/wwwroot/env/Scripts
ls

echo "== pwd =="
pwd

echo "== source activate =="
source activate

echo "== cd ~/site/wwwroot; pwd == " 
cd ~/site/wwwroot

python manage.py makemigrations
python manage.py migrate
