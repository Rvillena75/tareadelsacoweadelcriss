"""Servidor de DCCaída de palabras"""
import socket
import threading
import json
import csv
from pathlib import Path
from flask import Flask, jsonify

from parametros import HOST, PORT

# Datos
DATA_PATH = Path(__file__).resolve().parent / 'data'
USUARIOS_CSV = DATA_PATH / 'usuarios.csv'
PARTIDAS_CSV = DATA_PATH / 'partidas.csv'
PARTIDAS_USUARIOS = DATA_PATH / 'partidas_usuarios.json'


class Cliente(threading.Thread):
    """Maneja un cliente conectado al servidor"""

    def __init__(self, socket_cliente, addr, servidor):
        super().__init__(daemon=True)
        self.socket = socket_cliente
        self.addr = addr
        self.servidor = servidor
        self.nombre = None

    def run(self):
        try:
            self.enviar({'mensaje': 'bienvenido'})
            while True:
                data = self.socket.recv(1024)
                if not data:
                    break
                mensaje = json.loads(data.decode())
                if mensaje.get('comando') == 'login':
                    self.nombre = mensaje.get('nombre')
                    self.servidor.registrar_usuario(self.nombre)
                    self.enviar({'estado': 'ok'})
                elif mensaje.get('comando') == 'pedir_palabra':
                    palabra = self.servidor.obtener_palabra()
                    self.enviar({'palabra': palabra})
        finally:
            self.socket.close()
            self.servidor.eliminar_cliente(self)

    def enviar(self, data):
        try:
            self.socket.sendall(json.dumps(data).encode())
        except OSError:
            pass


class Servidor:
    """Servidor principal"""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clientes = []
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        self.socket_servidor.bind((self.host, self.port))
        self.socket_servidor.listen()
        print(f'Servidor escuchando en {self.host}:{self.port}')
        threading.Thread(target=self.aceptar_clientes, daemon=True).start()

    def aceptar_clientes(self):
        while True:
            try:
                socket_cliente, addr = self.socket_servidor.accept()
            except OSError:
                break
            cliente = Cliente(socket_cliente, addr, self)
            cliente.start()
            self.clientes.append(cliente)

    def registrar_usuario(self, nombre):
        if not USUARIOS_CSV.exists():
            with open(USUARIOS_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['nombre'])
        with open(USUARIOS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([nombre])

    def eliminar_cliente(self, cliente):
        if cliente in self.clientes:
            self.clientes.remove(cliente)

    def obtener_palabra(self):
        return 'palabra'


# Flask API
app = Flask(__name__)
servidor = Servidor(HOST, PORT)


@app.route('/ping')
def ping():
    return jsonify({'pong': True})


def main():
    servidor.start()
    app.run(host=HOST, port=PORT + 1, debug=False)


if __name__ == '__main__':
    main()
