#!/bin/bash
set -e

# Запуск виртуального дисплея
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
export DISPLAY=:99

# Ждем инициализации Xvfb
sleep 2

# Запуск команды (pytest)
exec "$@"
