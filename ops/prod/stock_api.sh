#!/usr/bin/env bash
PROJECT_ROOT="/Users/diederickdebuck/Developer/Python/StockAlert"
VENV_PATH="${PROJECT_ROOT}/.venv"

cd ${PROJECT_ROOT}
source "${VENV_PATH}/bin/activate"

set -a
source ${PROJECT_ROOT}/etc/stock_alert.env
set +a

python ${PROJECT_ROOT}/stock_api.py \
--mongo ${PROJECT_ROOT}/etc/prod/mongodb.yml \
--stock_api ${PROJECT_ROOT}/etc/prod/stock_api.yml
  