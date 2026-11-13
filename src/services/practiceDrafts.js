export const PRACTICE_DRAFT_PREFIX = 'zisu.practice-draft.v1.';
export const MAX_DRAFT_STROKES = 50;
export const MAX_POINTS_PER_STROKE = 480;

function validCharacter(character) {
  const value = typeof character === 'string' ? character.trim() : '';
  return Array.from(value).length === 1 ? value : '';
}

function isStorageLike(storage) {
  return Boolean(
    storage
      && typeof storage.getItem === 'function'
      && typeof storage.setItem === 'function'
      && typeof storage.removeItem === 'function'
  );
}

function normalizePoint(point) {
  const x = Number(point?.x);
  const y = Number(point?.y);

  if (!Number.isFinite(x) || !Number.isFinite(y)) {
    return null;
  }

  return {
    x: Math.round(Math.min(360, Math.max(0, x)) * 10) / 10,
    y: Math.round(Math.min(360, Math.max(0, y)) * 10) / 10
  };
}

function compressStroke(points) {
  const validPoints = points.map(normalizePoint).filter(Boolean);

  if (validPoints.length < 2) {
    return [];
  }

  const step = Math.max(1, Math.ceil(validPoints.length / MAX_POINTS_PER_STROKE));
  const compressed = validPoints.filter((_, index) => index % step === 0);
  const lastPoint = validPoints.at(-1);

  if (compressed.at(-1) !== lastPoint) {
    compressed.push(lastPoint);
  }

  return compressed;
}

export function practiceDraftKey(character) {
  const normalized = validCharacter(character);
  return `${PRACTICE_DRAFT_PREFIX}${encodeURIComponent(normalized || 'unknown')}`;
}

export function normalizePracticeStrokes(strokes) {
  if (!Array.isArray(strokes)) {
    return [];
  }

  return strokes
    .slice(0, MAX_DRAFT_STROKES)
    .filter(Array.isArray)
    .map(compressStroke)
    .filter(points => points.length >= 2);
}

export function loadPracticeDraft(storage, character) {
  if (!isStorageLike(storage)) {
    return { available: false, found: false, strokes: [] };
  }

  try {
    const raw = storage.getItem(practiceDraftKey(character));

    if (!raw) {
      return { available: true, found: false, strokes: [] };
    }

    const payload = JSON.parse(raw);
    return {
      available: true,
      found: true,
      strokes: normalizePracticeStrokes(payload?.strokes)
    };
  } catch {
    return { available: false, found: false, strokes: [] };
  }
}

export function savePracticeDraft(storage, character, strokes) {
  const normalized = normalizePracticeStrokes(strokes);

  if (!isStorageLike(storage)) {
    return { available: false, saved: false, strokes: normalized };
  }

  try {
    const key = practiceDraftKey(character);

    if (!normalized.length) {
      storage.removeItem(key);
      return { available: true, saved: true, strokes: [] };
    }

    storage.setItem(key, JSON.stringify({
      version: 1,
      updatedAt: new Date().toISOString(),
      strokes: normalized
    }));

    return { available: true, saved: true, strokes: normalized };
  } catch {
    return { available: false, saved: false, strokes: normalized };
  }
}
