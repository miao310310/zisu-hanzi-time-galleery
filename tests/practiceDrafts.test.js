import test from 'node:test';
import assert from 'node:assert/strict';
import {
  MAX_POINTS_PER_STROKE,
  loadPracticeDraft,
  normalizePracticeStrokes,
  practiceDraftKey,
  savePracticeDraft
} from '../src/services/practiceDrafts.js';

function createStorage() {
  const values = new Map();
  return {
    getItem: key => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value),
    removeItem: key => values.delete(key)
  };
}

test('normalizes practice strokes without allowing malformed or oversized points', () => {
  const longStroke = Array.from({ length: MAX_POINTS_PER_STROKE + 120 }, (_, index) => ({ x: index, y: -2 }));
  const strokes = normalizePracticeStrokes([
    [{ x: -8, y: 480 }, { x: 20.04, y: 31.06 }],
    [{ x: 'invalid', y: 1 }],
    longStroke
  ]);

  assert.deepEqual(strokes[0], [{ x: 0, y: 360 }, { x: 20, y: 31.1 }]);
  assert.equal(strokes.length, 2);
  assert.ok(strokes[1].length <= MAX_POINTS_PER_STROKE + 1);
});

test('saves, restores and clears a character draft independently', () => {
  const storage = createStorage();
  const original = [[{ x: 1, y: 2 }, { x: 3, y: 4 }]];

  const result = savePracticeDraft(storage, '日', original);
  assert.equal(result.saved, true);
  assert.ok(storage.getItem(practiceDraftKey('日')));
  assert.deepEqual(loadPracticeDraft(storage, '日').strokes, original);
  assert.deepEqual(loadPracticeDraft(storage, '山').strokes, []);

  savePracticeDraft(storage, '日', []);
  assert.equal(storage.getItem(practiceDraftKey('日')), null);
});

test('degrades safely when browser storage is unavailable', () => {
  const brokenStorage = {
    getItem() { throw new Error('blocked'); },
    setItem() { throw new Error('blocked'); },
    removeItem() { throw new Error('blocked'); }
  };

  assert.equal(loadPracticeDraft(brokenStorage, '日').available, false);
  assert.equal(savePracticeDraft(brokenStorage, '日', []).saved, false);
});
