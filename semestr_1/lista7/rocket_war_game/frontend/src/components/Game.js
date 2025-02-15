import React, { useState, useEffect, useRef } from "react";

function App() {
  const [playerId, setPlayerId] = useState("");
  const [ws, setWs] = useState(null);

  // Stan gry odbierany z serwera
  const [rockets, setRockets] = useState([]);
  const [baseHP, setBaseHP] = useState({ player1: 100, player2: 100 });

  // Canvas do renderowania
  const canvasRef = useRef(null);

  // Użytkownik może wybrać kąt i moc
  const [angle, setAngle] = useState(45);
  const [power, setPower] = useState(50);

  // -------------------------
  // 1) Połączenie WebSocket
  // -------------------------
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
        // Ustawiamy rakiety i HP baz z wiadomości
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

  // Gdy komponent się unmountuje, zamykamy socket
  useEffect(() => {
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);

  // -------------------------
  // 2) Rysowanie na Canvas
  // -------------------------
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      // Planeta
      const planetRadius = 290; // musi pasować do planu w Pythonie
      ctx.beginPath();
      ctx.arc(centerX, centerY, planetRadius, 0, 2 * Math.PI);
      ctx.strokeStyle = "green";
      ctx.stroke();

      // Baza player1 (x=+300, y=0 => canvasX = centerX+300, canvasY = centerY)
      drawBase(ctx, centerX + 300, centerY, "red");

      // Baza player2 (x=-300, y=0 => canvasX = centerX-300, canvasY = centerY)
      drawBase(ctx, centerX - 300, centerY, "blue");

      // Rakiety
      rockets.forEach((rocket) => {
        // W Pythonie (0,0) to środek, Y rośnie w górę
        // W Canvas (0,0) jest w lewym górnym rogu, Y rośnie w dół
        const x = centerX + rocket.pos.x;
        const y = centerY - rocket.pos.y;
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fillStyle = rocket.owner_id === "player1" ? "red" : "blue";
        ctx.fill();
      });

      requestAnimationFrame(draw);
    }

    requestAnimationFrame(draw);
  }, [rockets]);

  function drawBase(ctx, x, y, color) {
    ctx.beginPath();
    ctx.arc(x, y, 10, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
  }

  // -------------------------
  // 3) Wystrzelenie rakiety
  // -------------------------
  const fireRocket = () => {
    if (!ws) {
      console.log("Brak połączenia WebSocket");
      return;
    }
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "fire", angle: Number(angle), power: Number(power) }));
    } else {
      console.log("WebSocket nie jest w stanie OPEN. readyState =", ws.readyState);
    }
  };

  return (
    <div style={{ textAlign: "center" }}>
      <h1>Worms-like 2D Game</h1>

      <div style={{ marginBottom: "1rem" }}>
        <label>Player ID: </label>
        <input
          type="text"
          value={playerId}
          placeholder="player1 / player2"
          onChange={(e) => setPlayerId(e.target.value)}
        />
        <button onClick={connectWebSocket}>Connect</button>
      </div>

      <p>
        HP bazy player1: {baseHP.player1} | HP bazy player2: {baseHP.player2}
      </p>

      <canvas
        ref={canvasRef}
        width={800}
        height={600}
        style={{ border: "1px solid black" }}
      />

      <div style={{ marginTop: "1rem" }}>
        <label>Kąt: </label>
        <input
          type="number"
          value={angle}
          onChange={(e) => setAngle(e.target.value)}
          style={{ width: "60px", marginRight: "10px" }}
        />
        <label>Moc: </label>
        <input
          type="number"
          value={power}
          onChange={(e) => setPower(e.target.value)}
          style={{ width: "60px", marginRight: "10px" }}
        />
        <button onClick={fireRocket}>Fire Rocket</button>
      </div>
    </div>
  );
}

export default App;
