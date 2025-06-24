"""Cliente de DCCaída de palabras"""
import sys
import json
import socket
import threading
from PyQt5 import QtWidgets, QtCore

from parametros import HOST, PORT


class VentanaLogin(QtWidgets.QWidget):
    """Ventana para ingresar nombre"""

    login_realizado = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.layout = QtWidgets.QVBoxLayout(self)
        self.nombre_input = QtWidgets.QLineEdit()
        self.boton = QtWidgets.QPushButton('Ingresar')
        self.layout.addWidget(self.nombre_input)
        self.layout.addWidget(self.boton)
        self.boton.clicked.connect(self.confirmar)

    def confirmar(self):
        nombre = self.nombre_input.text().strip()
        if nombre:
            self.login_realizado.emit(nombre)


class VentanaJuego(QtWidgets.QWidget):
    """Ventana principal de juego"""

    pedir_palabra = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('DCCaída de palabras')
        self.layout = QtWidgets.QVBoxLayout(self)
        self.palabra_label = QtWidgets.QLabel('')
        self.input_palabra = QtWidgets.QLineEdit()
        self.layout.addWidget(self.palabra_label)
        self.layout.addWidget(self.input_palabra)
        self.input_palabra.returnPressed.connect(self.enviar_palabra)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.solicitar_palabra)

    def iniciar(self):
        self.timer.start(2000)

    def solicitar_palabra(self):
        self.pedir_palabra.emit()

    def actualizar_palabra(self, palabra):
        self.palabra_label.setText(palabra)

    def enviar_palabra(self):
        self.input_palabra.clear()


class Cliente(QtCore.QObject):
    """Maneja la conexión con el servidor"""

    palabra_recibida = QtCore.pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.escuchando = False

    def conectar(self):
        self.socket.connect((self.host, self.port))
        self.escuchando = True
        threading.Thread(target=self.escuchar, daemon=True).start()

    def escuchar(self):
        while self.escuchando:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                mensaje = json.loads(data.decode())
                if 'palabra' in mensaje:
                    self.palabra_recibida.emit(mensaje['palabra'])
            except OSError:
                break

    def enviar(self, data):
        try:
            self.socket.sendall(json.dumps(data).encode())
        except OSError:
            pass

    def login(self, nombre):
        self.enviar({'comando': 'login', 'nombre': nombre})

    def pedir_palabra(self):
        self.enviar({'comando': 'pedir_palabra'})


class Aplicacion(QtWidgets.QStackedWidget):
    """Aplicación principal"""

    def __init__(self):
        super().__init__()
        self.cliente = Cliente(HOST, PORT)
        self.login = VentanaLogin()
        self.juego = VentanaJuego()
        self.addWidget(self.login)
        self.addWidget(self.juego)
        self.login.login_realizado.connect(self.procesar_login)
        self.juego.pedir_palabra.connect(self.cliente.pedir_palabra)
        self.cliente.palabra_recibida.connect(self.juego.actualizar_palabra)
        self.cliente.conectar()
        self.setWindowTitle('DCCaída de palabras')

    def procesar_login(self, nombre):
        self.cliente.login(nombre)
        self.setCurrentWidget(self.juego)
        self.juego.iniciar()


def main():
    app = QtWidgets.QApplication(sys.argv)
    aplicacion = Aplicacion()
    aplicacion.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
