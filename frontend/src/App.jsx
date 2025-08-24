import React, { useState, useEffect } from 'react';

// URL del WebSocket, asegúrate de que esta sea la IP real de tu ESP32
const WEBSOCKET_URL = 'ws://192.168.100.15:80'; 
const RECONNECT_TIMEOUT = 3000; // Intenta reconectar cada 3 segundos

function WebSocketClient() {
    const [messages, setMessages] = useState([]);
    const [socket, setSocket] = useState(null);
    const [status, setStatus] = useState('Desconectado');

    useEffect(() => {
        const connect = () => {
            console.log('🌐 Intentando conectar al servidor WebSocket...');
            setStatus('Conectando...');
            const ws = new WebSocket(WEBSOCKET_URL);

            ws.onopen = () => {
                console.log('✅ Conectado al servidor WebSocket');
                setStatus('Conectado');
                setSocket(ws);
            };

            ws.onmessage = (event) => {
                console.log('💌 Mensaje recibido:', event.data);
                setMessages(prevMessages => [...prevMessages, event.data]);
            };

            ws.onclose = () => {
                console.log('❌ Desconectado del servidor WebSocket');
                setStatus('Desconectado');
                // Intenta reconectar automáticamente después de un tiempo
                setTimeout(connect, RECONNECT_TIMEOUT);
            };

            ws.onerror = (error) => {
                console.error('⚠️ Error de WebSocket:', error);
                setStatus('Error');
                ws.close(); // Cierra la conexión para forzar la reconexión
            };
        };

        connect(); // Inicia la conexión
        
        // Limpia al desmontar el componente
        return () => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.close();
            }
        };
    }, []); // El array de dependencias vacío asegura que se ejecute solo una vez

    const sendMessage = () => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            const message = '¡Hola desde React!';
            socket.send(message);
            console.log('🚀 Mensaje enviado:', message);
        } else {
            console.log('⚠️ Conexión WebSocket no lista.');
        }
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>WebSocket con ESP32 y React</h1>
            <p>Estado: <strong>{status}</strong></p>
            <p>Asegúrate de que tu computadora y el ESP32 estén en la misma red Wi-Fi.</p>
            <button 
                onClick={sendMessage} 
                disabled={status !== 'Conectado'}
                style={{
                    padding: '10px 20px', 
                    fontSize: '16px', 
                    cursor: status === 'Conectado' ? 'pointer' : 'not-allowed'
                }}
            >
                Enviar mensaje
            </button>
            <hr />
            <h2>Mensajes Recibidos:</h2>
            <ul style={{ listStyleType: 'none', padding: 0 }}>
                {messages.map((msg, index) => (
                    <li key={index} style={{
                        padding: '8px', 
                        borderBottom: '1px solid #eee'
                    }}>
                        {msg}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default WebSocketClient;