import React, { useState, useEffect, useRef } from "react";

const PLANET_RADIUS = 290; 
const GRAVITY = 40;       
const MAX_POWER = 150;    
const EXPLOSION_DURATION_MS = 1400;

function App() {
  const [playerId, setPlayerId] = useState("");
  const [ws, setWs] = useState(null);

  // Stan gry z serwera (rakiety, HP baz).
  const [rockets, setRockets] = useState([]);
  const [baseHP, setBaseHP] = useState({ player1: 100, player2: 100 });

  // Ref do obsługi Canvas
  const canvasRef = useRef(null);

  // Obsługa celowania
  const [isAiming, setIsAiming] = useState(false);
  const [basePosCanvas, setBasePosCanvas] = useState({ x: 0, y: 0 });
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [predictedPath, setPredictedPath] = useState([]);

  // Obsługa wybuchów
  const prevRocketsRef = useRef([]);
  const explosionsRef = useRef([]);

  // 
  // WEBSOCKET
  //
  const connectWebSocket = () => {
    if (!playerId) {
      alert("Podaj playerId (np. player1 lub player2)!");
      return;
    }
    const url = `wss://tough-pugs-grab.loca.lt//ws/${playerId}`;
    const socket = new WebSocket(url);

    socket.onopen = () => {
      console.log("WS connected as", playerId);
      setWs(socket);
    };

    socket.onmessage = (evt) => {
      const msg = JSON.parse(evt.data);
      if (msg.type === "state") {
        setRockets(msg.rockets);
        console.log(rockets)
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


  useEffect(() => {
    return () => {
      if (ws) ws.close();
    };
  }, [ws]);

  //
  // WYBUCH RAKIET
  //
  useEffect(() => {
    const prevRockets = prevRocketsRef.current;
    const currentRockets = rockets;

    // Rakiety z poprzedniej klatki, których nie ma w obecnej, to te, które zniknęły
    const vanished = prevRockets.filter(
      (prevRocket) => !currentRockets.some((r) => r.id === prevRocket.id)
    );

    // Dodajemy boom boom tam gdzie rakiety zniknęły
    vanished.forEach((vr) => {
      explosionsRef.current.push({
        x: vr.pos.x,
        y: vr.pos.y,
        startTime: performance.now(),
      });
    });

    // Zapisujemy aktualną listę rakiet jako poprzednią
    prevRocketsRef.current = currentRockets;
  }, [rockets]);

  //
  // WYLICZANIE POZYCJI BAZY W CANVAS
  //
  const getBaseCanvasPos = (canvas) => {
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    if (playerId === "player1") {
      // Baza gracza 1 po prawej
      return { x: centerX + 300, y: centerY };
    } else {
      // Baza gracza 2 po lewej (domyślnie)
      return { x: centerX - 300, y: centerY };
    }
  };

  // 
  // OBSŁUGA MYSZKI
  // 
  const handleMouseDown = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const bPos = getBaseCanvasPos(canvas);

    // Sprawdzamy, czy kliknięto w pobliżu bazy (promień 20px)
    const dist = Math.sqrt((mouseX - bPos.x) ** 2 + (mouseY - bPos.y) ** 2);
    if (dist < 20) {
      setIsAiming(true);
      setBasePosCanvas({ x: bPos.x, y: bPos.y });
      setMousePos({ x: mouseX, y: mouseY });
      setPredictedPath([]);
    }
  };

  const handleMouseMove = (e) => {
    if (!isAiming) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    setMousePos({ x: mouseX, y: mouseY });

    // Obliczanie siły
    const dx = mouseX - basePosCanvas.x;
    const dy = mouseY - basePosCanvas.y;
    let distance = Math.sqrt(dx * dx + dy * dy);
    if (distance > MAX_POWER) distance = MAX_POWER;


    let angleRad = Math.atan2(-dy, dx) + Math.PI;

    // Wyliczamy lokalną trajektorię 
    const localTrajectory = simulateTrajectory(
      angleRad,
      distance,
      GRAVITY,
      0.05,
      50
    );

    // Przekształcenie punktów na koordy Canvas
    const canvasPoints = localTrajectory.map((p) => ({
      x: basePosCanvas.x + p.x,
      y: basePosCanvas.y - p.y,
    }));
    setPredictedPath(canvasPoints);
  };

  const handleMouseUp = () => {
    if (!isAiming) return;
    setIsAiming(false);

    // Ostateczne wyliczenie kąta i mocy, analogicznie jak w handleMouseMove
    const dx = mousePos.x - basePosCanvas.x;
    const dy = mousePos.y - basePosCanvas.y;
    let distance = Math.sqrt(dx * dx + dy * dy);
    if (distance > MAX_POWER) distance = MAX_POWER;

    let angleRad = Math.atan2(-dy, dx) + Math.PI;
    const angleDeg = (angleRad * 180) / Math.PI;

    fireRocket(angleDeg, distance);
  };

  //
  // WYSYŁANIE KOMENDY "fire" DO SERWERA
  // 
  const fireRocket = (angleDeg, power) => {
    if (!ws) return;
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "fire", angle: angleDeg, power: power }));
      console.log("Rakieta wystrzelona!");
    }
  };

  // 
  // FUNKCJA SYMULUJĄCA TRAJEKTORIĘ (LOKALNIE) (NIE DZIAŁA :())
  // 
  function simulateTrajectory(angleRad, power, gravity, dt, steps) {
    let points = [];
    let pos = { x: 0, y: 0 };
    let vx = power * Math.cos(angleRad);
    let vy = power * Math.sin(angleRad);

    for (let i = 0; i < steps; i++) {
      points.push({ x: pos.x, y: pos.y });

      const dist = Math.sqrt(pos.x * pos.x + pos.y * pos.y) / 2;
      let ax = 0;
      let ay = 0;

      if (dist > 0) {
        const nx = -pos.x / dist;
        const ny = -pos.y / dist;
        ax = nx * gravity;
        ay = ny * gravity;
      }

      vx += ax * dt;
      vy += ay * dt;
      pos.x += vx * dt;
      pos.y += vy * dt;
    }
    return points;
  }

  //
  // RYSOWANIE NA CANVAS
  //
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      // Planeta
      drawPlanet(ctx, centerX, centerY);

      // Bazy
      drawBase(ctx, centerX + 300, centerY, "red");   // Player1
      drawBase(ctx, centerX - 300, centerY, "blue");  // Player2

      // Rakiety z serwera
      rockets.forEach((rocket) => {
        const rx = centerX + rocket.pos.x;
        const ry = centerY - rocket.pos.y;
        drawRocket(ctx, rx, ry, rocket.owner_id);
      });

      // Trajektoria celowania (predictedPath)
      if (predictedPath.length > 0 && isAiming) {
        drawPredictedPath(ctx, predictedPath);
      }

      // Linia bazowa -> mysz (celowanie)
      if (isAiming) {
        drawAimLine(ctx, basePosCanvas, mousePos);
      }

      // Wybuchy
      drawExplosions(ctx, centerX, centerY);

      requestAnimationFrame(draw);
    };

    requestAnimationFrame(draw);
  }, [rockets, predictedPath, isAiming, mousePos, basePosCanvas]);

  // -------------------------
  // FUNKCJE RYSUJĄCE
  // -------------------------
  function drawPlanet(ctx, centerX, centerY) {
    ctx.beginPath();
    ctx.arc(centerX, centerY, PLANET_RADIUS, 0, 2 * Math.PI);
    ctx.strokeStyle = "green";
    ctx.stroke();
  }

  function drawBase(ctx, x, y, color) {
    ctx.beginPath();
    ctx.arc(x, y, 10, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
  }
  function drawRocket(ctx, x, y, ownerId) {
    const color = ownerId === "player1" ? "red" : "blue";

    ctx.save();
    ctx.fillStyle = color;

    ctx.beginPath();

  
    ctx.moveTo(x, y - 8);

    ctx.lineTo(x - 3, y + 4);

    ctx.lineTo(x + 3, y + 4);

    ctx.closePath();
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(x - 3, y + 2);
    ctx.lineTo(x - 6, y + 6);
    ctx.lineTo(x - 3, y + 4);
    ctx.closePath();
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(x + 3, y + 2);
    ctx.lineTo(x + 6, y + 6);
    ctx.lineTo(x + 3, y + 4);
    ctx.closePath();
    ctx.fill();

    ctx.restore();
  }

  function drawPredictedPath(ctx, path) {
    ctx.strokeStyle = "black";
    ctx.beginPath();
    ctx.moveTo(path[0].x, path[0].y);
    for (let i = 1; i < path.length; i++) {
      ctx.lineTo(path[i].x, path[i].y);
    }
    ctx.stroke();
  }


  function drawPredictedPath(ctx, path) {
    ctx.strokeStyle = "black";
    ctx.beginPath();
    ctx.moveTo(path[0].x, path[0].y);
    for (let i = 1; i < path.length; i++) {
      ctx.lineTo(path[i].x, path[i].y);
    }
    ctx.stroke();
  }

  function drawAimLine(ctx, basePos, mousePos) {
    ctx.strokeStyle = "black";
    ctx.beginPath();
    ctx.moveTo(basePos.x, basePos.y);
    ctx.lineTo(mousePos.x, mousePos.y);
    ctx.stroke();

    const dx = mousePos.x - basePos.x;
    const dy = mousePos.y - basePos.y;
    let dist = Math.sqrt(dx * dx + dy * dy);
    if (dist > MAX_POWER) dist = MAX_POWER;

    ctx.save();
    ctx.fillStyle = "black";
    ctx.fillText(`Power: ${dist.toFixed(0)}`, mousePos.x + 10, mousePos.y);
    ctx.restore();
  }

  function drawExplosions(ctx, centerX, centerY) {
    const now = performance.now();
    const updatedExplosions = [];

    explosionsRef.current.forEach((expl) => {
      const age = now - expl.startTime;
      if (age < EXPLOSION_DURATION_MS) {
        const progress = age / EXPLOSION_DURATION_MS;
        const radius = 30 * progress;
        const alpha = 1 - progress;

        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.beginPath();

        const ex = centerX + expl.x;
        const ey = centerY - expl.y;
        ctx.arc(ex, ey, radius, 0, 2 * Math.PI);
        ctx.fillStyle = "orange";
        ctx.fill();
        ctx.restore();

        updatedExplosions.push(expl);
      }
    });

    explosionsRef.current = updatedExplosions;
  }

  //
  // RENDER
  // 
  return (
    <div style={{ textAlign: "center" }}>
      <h1>✨RAKIETOMANIA✨</h1>

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
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      />
    </div>
  );
}

export default App;
