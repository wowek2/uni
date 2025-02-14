import { useState, useEffect } from "react";

export default function useGameWebSocket(playerId) {
  const [ws, setWs] = useState(null);
  const [rockets, setRockets] = useState([]);
  const [baseHP, setBaseHP] = useState({ player1: 100, player2: 100 });

  useEffect(() => {
    // Zwracamy funkcję czyszczącą przy odpięciu komponentu
    return () => {
      if (ws) ws.close();
    };
  }, [ws]);

  const connectWebSocket = () => {
    if (!playerId) {
      alert("Podaj playerId (np. player1 lub player2)!");
      return;
    }
    const url = `ws://localhost:8000/ws/${playerId}`;
    const socket = new WebSocket(url);

    socket.onopen = () => {
      console.log("WS connected as", playerId);
      setWs(socket);
    };

    socket.onmessage = (evt) => {
      const msg = JSON.parse(evt.data);
      if (msg.type === "state") {
        setRockets(msg.rockets);
        setBaseHP(msg.baseHP);
      }
    };

    socket.onclose = () => {
      console.log("WS closed");
      setWs(null);
    };

    socket.onerror = (err) => {
      console.error("WS error", err);
    };
  };

  const fireRocket = (angleDeg, power) => {
    if (!ws) return;
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "fire", angle: angleDeg, power: power }));
      console.log("Rakieta wystrzelona!");
    }
  };

  return {
    ws,
    connectWebSocket,
    rockets,
    baseHP,
    fireRocket,
  };
}
