import json
from pathlib import Path

with open(Path(__file__).resolve().parent / 'conexion.json', 'r', encoding='utf-8') as f:
    CONEXION = json.load(f)

HOST = CONEXION.get('host', 'localhost')
PORT = int(CONEXION.get('port', 5000))
