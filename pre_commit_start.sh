#!/bin/bash

# If the script fail it stop
set -e

echo "Pre-commit install..."

if [ ! -d ".venv" ]; then
    echo "Creation of the python environment"
    python3 -m venv .venv
else
    echo "python environment already exist"
fi

echo "Activation of the python environment"
# shellcheck source=/dev/null
source .venv/bin/activate

echo "update of pip (necessary for the installation of all the hooks)"
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    echo "Installation of the dependencies in the requirements.txt"
    pip install -r requirements.txt
else
    echo "requirements.txt not found"
fi

echo "Installation of pre-comit hooks"
pre-commit install

echo "pre-commit hooks update"
pre-commit autoupdate

echo "Installation finished"
exec bash --rcfile <(echo "source ~/.bashrc; source .venv/bin/activate")
