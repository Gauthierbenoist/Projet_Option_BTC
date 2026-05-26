#!/usr/bin/env bash
# Installe une entrée cron quotidienne pour la pipeline Deribit
# Usage : bash data/scripts/install_linux_cron.sh
#         bash data/scripts/install_linux_cron.sh --uninstall

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CRON_TIME="${PIPELINE_SCHEDULE_TIME:-00:15}"
HOUR="${PIPELINE_SCHEDULE_HOUR:-${CRON_TIME%%:*}}"
MINUTE="${PIPELINE_SCHEDULE_MINUTE:-${CRON_TIME##*:}}"
MARKER="# deribit-btc-options-etl"

PYTHON="${PROJECT_ROOT}/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="$(command -v python3 || command -v python)"
fi

CRON_LINE="$MINUTE $HOUR * * * cd \"$PROJECT_ROOT\" && \"$PYTHON\" data/scripts/run_daily_pipeline.py --scheduled >> data/logs/scheduler.log 2>&1 $MARKER"

if [[ "${1:-}" == "--uninstall" ]]; then
  crontab -l 2>/dev/null | grep -v "$MARKER" | crontab - || true
  echo "Entrée cron supprimée."
  exit 0
fi

mkdir -p "$PROJECT_ROOT/data/logs"
(crontab -l 2>/dev/null | grep -v "$MARKER"; echo "$CRON_LINE") | crontab -
echo "Cron installé : $CRON_LINE"
echo "Logs : $PROJECT_ROOT/data/logs/scheduler.log"
