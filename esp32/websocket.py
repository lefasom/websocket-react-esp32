# websocket.py

# Importa las librerías necesarias para el protocolo WebSocket
import hashlib
import ubinascii as binascii
import struct
import ure as re

def handle_websocket_connection(conn):
    """
    Función principal para manejar una conexión WebSocket.
    Se encarga del handshake y luego entra en un bucle para recibir mensajes.
    """
    try:
        # --- Paso 1: El WebSocket Handshake ---
        # Lee la primera solicitud HTTP del cliente.
        request = conn.recv(1024).decode('utf-8')
        
        # Verifica si es una solicitud de WebSocket (handshake).
        if "Upgrade: websocket" in request and "Connection: Upgrade" in request:
            # Extrae la clave especial que el cliente envía para el handshake.
            key_start = request.find("Sec-WebSocket-Key:") + len("Sec-WebSocket-Key:")
            key_end = request.find("\r\n", key_start)
            client_key = request[key_start:key_end].strip()

            # Genera la clave de respuesta usando SHA1 y Base64.
            # Esta es una parte crítica del protocolo WebSocket.
            guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
            handshake_input = (client_key + guid).encode('utf-8')
            sha1_hash = hashlib.sha1(handshake_input)
            response_key = binascii.b2a_base64(sha1_hash.digest()).decode('utf-8').strip()

            # Construye y envía la respuesta al cliente.
            response_headers = "HTTP/1.1 101 Switching Protocols\r\n"
            response_headers += "Upgrade: websocket\r\n"
            response_headers += "Connection: Upgrade\r\n"
            response_headers += "Sec-WebSocket-Accept: {}\r\n".format(response_key)
            response_headers += "\r\n"
            conn.send(response_headers.encode('utf-8'))
            
            print("Handshake completado. Conexión WebSocket establecida.")

            # --- Paso 2: Bucle para recibir y procesar mensajes ---
            while True:
                # Llama a la función para leer el siguiente mensaje del socket.
                message = read_websocket_message(conn)
                if message is None:
                    # Si la función devuelve None, significa que la conexión se cerró.
                    break
                
                # Procesa el mensaje recibido (en este caso, solo lo imprime).
                handle_message(message)

        else:
            conn.close()
            print("Conexión no es un WebSocket. Cerrada.")

    except Exception as e:
        print("Error en la conexión WebSocket:", e)

def read_websocket_message(conn):
    """
    Lee y decodifica un mensaje completo del socket WebSocket.
    """
    try:
        # Lee los primeros 2 bytes del encabezado del frame.
        header = conn.recv(2)
        if not header:
            return None # Si no hay datos, la conexión se cerró.

        byte1, byte2 = struct.unpack('!BB', header)
        
        # Extrae el opcode (tipo de mensaje) y la bandera de máscara.
        opcode = byte1 & 0x0f
        mask = bool(byte2 & 0x80)
        
        # Extrae la longitud de los datos.
        length = byte2 & 0x7f

        # Si la longitud es un valor especial, lee bytes adicionales.
        if length == 126:
            length = struct.unpack('!H', conn.recv(2))[0]
        elif length == 127:
            length = struct.unpack('!Q', conn.recv(8))[0]
            
        # Lee la máscara de 4 bytes si el mensaje está enmascarado.
        mask_bits = conn.recv(4) if mask else None
        
        # Lee los datos del mensaje.
        data = conn.recv(length)
        
        # Aplica la máscara a los datos si es necesario.
        if mask and data:
            data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))
            
        # Retorna el mensaje decodificado.
        if opcode == 0x1: # Si es un mensaje de texto
            return data.decode('utf-8')
        
    except Exception as e:
        print("Error al leer el mensaje:", e)
        return None

def handle_message(message):
    """
    Procesa un mensaje recibido del cliente.
    Aquí puedes añadir tu lógica (ej. controlar un LED, enviar un dato a un sensor).
    """
    print("Mensaje recibido:", message)