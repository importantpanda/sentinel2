// src/hooks/useWebSocket.ts
import { useEffect, useRef } from "react";

const useWebSocket = (url: string, onMessage: (event: MessageEvent) => void) => {
    const socketRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        const socket = new WebSocket(url);
        socketRef.current = socket;

        socket.onopen = () => {
            console.log("WebSocket connection opened");
        };

        socket.onmessage = onMessage;

        socket.onclose = () => {
            console.log("WebSocket connection closed");
        };

        socket.onerror = error => {
            console.error("WebSocket error:", error);
        };

        return () => {
            socket.close();
        };
    }, [url, onMessage]);

    return socketRef.current;
};

export default useWebSocket;
