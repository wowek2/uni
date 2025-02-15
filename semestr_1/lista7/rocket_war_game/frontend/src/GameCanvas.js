import React, { useRef, useEffect } from "react";

const planetRadius = 290;

export default function GameCanvas({
  playerId,
  rockets,
  explosions,
  updateExplosions,
  isAiming,
  mousePos,
  basePosCanvas,
  predictedPath,
  maxPower,
  onMouseDown,
  onMouseMove,
  onMouseUp,
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Rysowanie planety
      drawPlanet(ctx, centerX, centerY, planetRadius);

      // Baza player1 (po prawej)
      drawBase(ctx, centerX + 300, centerY, "red");
      // Baza player2 (po lewej)
      drawBase(ctx, centerX - 300, centerY, "blue");

      // Rakiety
      drawRockets(ctx, rockets, centerX, centerY);

      // Potencjalna trajektoria podczas celowania
      if (isAiming) {
        drawPredictedPath(ctx, predictedPath);
        drawAimingLine(ctx, basePosCanvas, mousePos, maxPower);
      }

      // Wybuchy
      updateExplosions(); // odfiltrowuje stare wybuchy
      drawExplosions(ctx, explosions, centerX, centerY);

      requestAnimationFrame(draw);
    }

    requestAnimationFrame(draw);
  }, [
    rockets,
    explosions,
    predictedPath,
    isAiming,
    mousePos,
    basePosCanvas,
    updateExplosions,
  ]);

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={600}
      style={{ border: "1px solid black" }}
      onMouseDown={onMouseDown}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
    />
  );
}

/* --- Funkcje pomocnicze do rysowania --- */

function drawPlanet(ctx, x, y, radius) {
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.strokeStyle = "green";
  ctx.stroke();
}

function drawBase(ctx, x, y, color) {
  ctx.beginPath();
  ctx.arc(x, y, 10, 0, 2 * Math.PI);
  ctx.fillStyle = color;
  ctx.fill();
}

function drawRockets(ctx, rockets, centerX, centerY) {
  rockets.forEach((rocket) => {
    const rx = centerX + rocket.pos.x;
    const ry = centerY - rocket.pos.y;
    ctx.beginPath();
    ctx.arc(rx, ry, 4, 0, 2 * Math.PI);
    ctx.fillStyle = rocket.owner_id === "player1" ? "red" : "blue";
    ctx.fill();
  });
}

function drawPredictedPath(ctx, predictedPath) {
  if (predictedPath.length > 0) {
    ctx.strokeStyle = "black";
    ctx.beginPath();
    ctx.moveTo(predictedPath[0].x, predictedPath[0].y);
    for (let i = 1; i < predictedPath.length; i++) {
      ctx.lineTo(predictedPath[i].x, predictedPath[i].y);
    }
    ctx.stroke();
  }
}

function drawAimingLine(ctx, basePosCanvas, mousePos, maxPower) {
  const dx = mousePos.x - basePosCanvas.x;
  const dy = mousePos.y - basePosCanvas.y;
  let dist = Math.sqrt(dx * dx + dy * dy);
  if (dist > maxPower) dist = maxPower;

  // linia
  ctx.strokeStyle = "black";
  ctx.beginPath();
  ctx.moveTo(basePosCanvas.x, basePosCanvas.y);
  ctx.lineTo(mousePos.x, mousePos.y);
  ctx.stroke();

  // tekst
  ctx.save();
  ctx.fillStyle = "black";
  ctx.fillText(`Power: ${dist.toFixed(0)}`, mousePos.x + 10, mousePos.y);
  ctx.restore();
}

function drawExplosions(ctx, explosions, centerX, centerY) {
  const explosionDuration = 1000; // ms

  const now = performance.now();
  explosions.forEach((expl) => {
    const age = now - expl.startTime;
    const progress = age / explosionDuration; // 0..1
    const radius = 30 * progress;
    const alpha = 1 - progress;
    const ex = centerX + expl.x;
    const ey = centerY - expl.y;

    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.arc(ex, ey, radius, 0, 2 * Math.PI);
    ctx.fillStyle = "orange";
    ctx.fill();
    ctx.restore();
  });
}
