export const clamp = (value, min, max) =>
    Math.max(min, Math.min(max, value));

export const normalize = (value, min, max) => {
    if (max === min) return 0;
    return (value - min) / (max - min);
};

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

export function createSeededRandom(seed) {
    let h = 1779033703 ^ seed.length;

    for (let i = 0; i < seed.length; i++) {
        h = Math.imul(h ^ seed.charCodeAt(i), 3432918353);
        h = (h << 13) | (h >>> 19);
    }

    return () => {
        h = Math.imul(h ^ (h >>> 16), 2246822507);
        h = Math.imul(h ^ (h >>> 13), 3266489909);
        h ^= h >>> 16;

        return (h >>> 0) / 4294967296;
    };
}

export function randomInt(random, min, max) {
    return Math.floor(random() * (max - min + 1)) + min;
}

export function randomFloat(random, min, max) {
    return random() * (max - min) + min;
}

export function randomBetween(random, min, max) {
    return min + random() * (max - min);
}

export function randomChoice(random, array) {
    return array[randomInt(random, 0, array.length - 1)];
}

export function shuffle(random, array) {
    const result = [...array];

    for (let i = result.length - 1; i > 0; i--) {
        const j = randomInt(random, 0, i);
        [result[i], result[j]] = [result[j], result[i]];
    }

    return result;
}

export function generatePosition(
    random,
    level,
    community,
    layout
) {
    const levelGap =
        layout?.levelGap ?? 180;

    const nodeGap =
        layout?.nodeGap ?? 250;

    const communityGap =
        layout?.communityGap ?? 450;

    return {
        x:
            (community - 1) *
                communityGap +
            (random() - 0.5) *
                nodeGap,
        y:
            level * levelGap +
            (random() - 0.5) * 40
    };
}

export function distributeNodes(totalNodes, depth) {
    const weights = [];
    let remaining = totalNodes - 1;

    for (let i = 1; i <= depth; i++) {
        weights.push(Math.pow(i, 1.4));
    }

    const totalWeight = weights.reduce(
        (sum, weight) => sum + weight,
        0
    );

    return weights.map(weight =>
        Math.max(
            1,
            Math.round(
                (weight / totalWeight) * remaining
            )
        )
    );
}