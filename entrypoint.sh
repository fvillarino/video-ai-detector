#!/bin/sh
set -e

CONFIG=/app/config.yaml

if [ -d "$CONFIG" ]; then
    echo ""
    echo "ERROR: '$CONFIG' es un directorio en el host, no un archivo."
    echo "Esto ocurre cuando Docker crea el directorio automáticamente antes de montar el archivo."
    echo ""
    echo "Solución en el server:"
    echo "  docker compose down"
    echo "  rm -rf $CONFIG"
    echo "  cp config.yaml.example config.yaml   # editar con tus credenciales"
    echo "  docker compose up -d"
    echo ""
    exit 1
fi

if [ ! -f "$CONFIG" ]; then
    echo "WARN: No se encontró config.yaml, usando config.yaml.example como base."
    cp /app/config.yaml.example "$CONFIG"
fi

exec python main.py
