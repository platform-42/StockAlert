#!/usr/bin/env bash
SCRIPT=$(realpath "$0")
SCRIPT_PATH=$(dirname "$SCRIPT")
VENV_PATH=${SCRIPT_PATH}/.venv

if [ ! -d ${VENV_PATH} ]; then
    python3 -m venv ${VENV_PATH}
fi

cd ${SCRIPT_PATH}
source ${VENV_PATH}/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
