#!/usr/bin/env bash

aoa_path="/home/he/aoa/aoa-upgrade"
if [[ "$UID" -eq 0 && $(uname -s) == "Linux" ]]
then
    site_packages="/home/he/.local/lib/python3.6/site-packages"
    PYTHONPATH=${aoa_path}:${site_packages} python3 -B ${1}
else
    PYTHONPATH=${aoa_path} python3 -B ${1}
fi
