import assert from 'node:assert/strict';
import test from 'node:test';
import {practiceCharacters} from '../src/data.js';

test('uses closed brush-style outlines for every practice stroke', () => {
  assert.deepEqual(practiceCharacters.map(item => item.char), ['日', '山', '水', '木']);

  for (const item of practiceCharacters) {
    assert.ok(item.strokes.length >= 3, `${item.char} should include multiple writing steps`);

    for (const stroke of item.strokes) {
      assert.match(stroke.outline, /^M[\s\S]*Z$/, `${item.char} ${stroke.name} should use a closed outline`);
      assert.equal(typeof stroke.origin, 'string', `${item.char} ${stroke.name} should define an animation origin`);
    }
  }
});
