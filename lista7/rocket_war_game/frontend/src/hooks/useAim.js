import { useState, useRef } from "react";

// Stałe do symulacji
const gravity = 40;
const maxPowerDefault = 150;
const stepsInTrajectory = 50;
const dt = 0.05;

export default function useAim({ playerId, fireRocket, addExplosion }) {
  const [isAiming, setIsAiming] = useState(false);
  const [basePosCanvas, setBasePosCanvas] = useState({ x: 0, y: 0 });
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [predictedPath, setPredictedPath] = useState([]);

  const maxPower = maxPowerDefault;

  // Funkcja pomocnicza do pobierania pozycji bazy w Canvas
  function getBaseCanvasPos(canvas) {
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Zakładamy, że "player1" stoi po prawej, a reszta po lewej
    if (playerId === "player1") {
      return { x: centerX + 300, y: centerY };
    } else {
      return { x: centerX - 300, y: centerY };
    }
  }

  // Rozpoczęcie celowania
  function handleMouseDown(e) {
    const canvas = e.currentTarget;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const bPos = getBaseCanvasPos(canvas);
    const dist = Math.sqrt((mouseX - bPos.x) ** 2 + (mouseY - bPos.y) ** 2);

    // Jeśli kliknięto w pobliżu bazy
    if (dist < 20) {
      setIsAiming(true);
      setBasePosCanvas({ x: bPos.x, y: bPos.y });
      setMousePos({ x: mouseX, y: mouseY });
      setPredictedPath([]);
    }
  }

  // Ruch myszy (aktualizacja wektora)
  function handleMouseMove(e) {
    if (!isAiming) return;
    const canvas = e.currentTarget;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    setMousePos({ x: mouseX, y: mouseY });

    // Obliczanie trajektorii
    const dx = mouseX - basePosCanvas.x;
    const dy = mouseY - basePosCanvas.y;

    let distance = Math.sqrt(dx * dx + dy * dy);
    if (distance > maxPower) distance = maxPower;

    let angleRad = Math.atan2(-dy, dx);
    angleRad += Math.PI; // rakieta leci w przeciwną stronę

    const localTrajectory = simulateTrajectory(
      angleRad,
      distance,
      gravity,
      dt,
      stepsInTrajectory
    );

    // zamiana współrzędnych "serwerowych" na Canvas
    const canvasPoints = localTrajectory.map((p) => ({
      x: basePosCanvas.x + p.x,
      y: basePosCanvas.y - p.y,
    }));
    setPredictedPath(canvasPoints);
  }

  // Puszczenie myszy – wystrzał
  function handleMouseUp() {
    if (!isAiming) return;
    setIsAiming(false);

    const dx = mousePos.x - basePosCanvas.x;
    const dy = mousePos.y - basePosCanvas.y;

    let distance = Math.sqrt(dx * dx + dy * dy);
    if (distance > maxPower) distance = maxPower;

    let angleRad = Math.atan2(-dy, dx);
    angleRad += Math.PI;
    const angleDeg = (angleRad * 180) / Math.PI;

    fireRocket(angleDeg, distance);
  }

  return {
    isAiming,
    mousePos,
    basePosCanvas,
    predictedPath,
    maxPower,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
    startAiming: () => setIsAiming(true),
    stopAiming: () => setIsAiming(false),
  };
}

// Symulacja lokalna trajektorii
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
