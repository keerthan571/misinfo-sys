/**
 * Common utility functions used across the Graph Generation Engine.
 */

export const clamp = (value, min, max) =>
  Math.max(min, Math.min(max, value));

export const normalize = (value, min, max) => {
  if (max === min) return 0;
  return (value - min) / (max - min);
};

export const randomInt = (min, max) =>
  Math.floor(Math.random() * (max - min + 1)) + min;

export const randomFloat = (min, max) =>
  Math.random() * (max - min) + min;

export const shuffle = (array) => {
  const result = [...array];

  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }

  return result;
};

export const choice = (array) =>
  array[Math.floor(Math.random() * array.length)];

export const uuid = (prefix = "node") =>
  `${prefix}_${crypto.randomUUID()}`;

export const calculateDistance = (a, b) =>
  Math.hypot(a.x - b.x, a.y - b.y);

export const polarToCartesian = (
  radius,
  angle,
  centerX = 0,
  centerY = 0
) => ({
  x: centerX + radius * Math.cos(angle),
  y: centerY + radius * Math.sin(angle),
});

/**
 * Deterministic pseudo-random generator.
 * Same seed -> same graph.
 */
export function createSeededRandom(seed) {
  let h = 1779033703 ^ seed.length;

  for (let i = 0; i < seed.length; i++) {
    h = Math.imul(h ^ seed.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }

  return function () {
    h = Math.imul(h ^ (h >>> 16), 2246822507);
    h = Math.imul(h ^ (h >>> 13), 3266489909);
    h ^= h >>> 16;

    return (h >>> 0) / 4294967296;
  };
}

export function distributeNodes(totalNodes, depth) {
  const levels = [];
  let remaining = totalNodes - 1;

  for (let level = 1; level <= depth; level++) {
    const weight = Math.pow(level, 1.4);
    levels.push(weight);
  }

  const totalWeight = levels.reduce((a, b) => a + b, 0);

  return levels.map((weight) =>
    Math.max(1, Math.round((weight / totalWeight) * remaining))
  );
}