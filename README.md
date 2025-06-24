# DCCaída de palabras

Proyecto de ejemplo para un juego cliente-servidor simple. Incluye una
implementación mínima de las estructuras solicitadas para el curso
IIC2233 - Programación Avanzada (PUC, 2025-1).

## Uso

### Servidor

```bash
python3 T4/servidor/main.py
```

Esto levanta el servidor del juego junto a una pequeña API Flask en el
puerto configurado en `T4/servidor/conexion.json`.

### Cliente

En otra terminal, se ejecuta el cliente con:

```bash
python3 T4/cliente/main.py
```

Se mostrará una ventana de inicio de sesión donde se debe ingresar el
nombre de usuario. Luego se abre la ventana del juego, en la cual el
servidor enviará palabras cada 2 segundos. El jugador debe escribir las
palabras antes de que cambien.

## Datos

La carpeta `T4/servidor/data` contiene archivos CSV/JSON que se
actualizarán con la información de los usuarios y partidas.
