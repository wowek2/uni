import { useRef, useEffect, useState } from "react";

export default function useExplosions(rockets = []) {
  const explosionsRef = useRef([]);
  const prevRocketsRef = useRef([]);

  useEffect(() => {
    const prevRockets = prevRocketsRef.current;
    const currentRockets = rockets;

    // 1. znajdź zniknięte
    const vanished = prevRockets.filter(
      (prevRocket) => !currentRockets.some((r) => r.id === prevRocket.id)
    );

    // 2. dodaj eksplozje do stanu
    if (vanished.length > 0) {
      setExplosions((old) => [
        ...old,
        ...vanished.map((vr) => ({
          x: vr.pos.x,
          y: vr.pos.y,
          startTime: performance.now(),
        })),
      ]);
    }

    // zapisz nową listę
    prevRocketsRef.current = currentRockets;
  }, [rockets]);

  function addExplosion(x, y) {
    explosionsRef.current.push({
      x, y,
      startTime: performance.now()
    });
  }

  // Funkcja do odfiltrowywania starych
  function updateExplosions() {
    const now = performance.now();
    const explosionDuration = 1000;
    setExplosions((old) =>
      old.filter((e) => now - e.startTime < explosionDuration)
    );
  }

  return { explosions, updateExplosions };
}
