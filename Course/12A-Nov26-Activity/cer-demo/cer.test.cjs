const { test } = require('node:test');
const assert = require('node:assert/strict');
const { compareTexts, MAX_CHARACTERS } = require('./cer.js');

const cases = [
  ['cat', 'cat', 0], ['cat', 'cut', 1], ['cat', 'ct', 1],
  ['cat', 'cart', 1], ['plant', 'blat', 2], ['cat', 'chats', 2],
  ['cat', '', 3], ['a', 'abcd', 3], ['cat', 'Cat', 1],
  ['cat', 'cat!', 1], ['cat', ' cat', 1], ['cat', 'cat ', 1],
  ['a cat', 'acat', 1], ['😀a', '😀b', 1], ['😀', '', 1],
  ['line\nbreak', 'linebreak', 1], ['សួស្តី', 'សួស្តី!', 1],
];

for (const [reference, prediction, expected] of cases) {
  test(`${JSON.stringify(reference)} → ${JSON.stringify(prediction)}`, () => {
    const r = compareTexts(reference, prediction);
    assert.equal(r.errors, expected);
    assert.equal(r.cer, expected / Array.from(reference).length);
    assert.equal(r.substitutions + r.deletions + r.insertions, r.errors);
    assert.equal(r.matches + r.substitutions + r.deletions, r.referenceLength);
    assert.equal(r.matches + r.substitutions + r.insertions, r.predictionLength);
    assert.equal(r.alignment.map((a) => a.reference ?? '').join(''), reference);
    assert.equal(r.alignment.map((a) => a.prediction ?? '').join(''), prediction);
  });
}

test('Worked example error types', () => {
  const r = compareTexts('plant', 'blat');
  assert.deepEqual([r.substitutions, r.deletions, r.insertions], [1, 1, 0]);
  assert.equal(compareTexts('a', 'abcd').cer, 3);
});
test('Do not silently normalize Unicode', () => {
  assert.notEqual(compareTexts('\u00e9', 'e\u0301').cer, 0);
});
test('Reject invalid inputs and excessive lengths', () => {
  assert.throws(() => compareTexts('', ''), /reference/);
  assert.throws(() => compareTexts('', 'cat'), /reference/);
  assert.throws(() => compareTexts(12, 'cat'), /text/);
  assert.throws(() => compareTexts('cat', null), /text/);
  assert.throws(() => compareTexts('a'.repeat(MAX_CHARACTERS + 1), 'a'), /2,000/);
  assert.throws(() => compareTexts('a', 'a'.repeat(MAX_CHARACTERS + 1)), /2,000/);
});
test('Alternative optimal alignments keep the distance and reconstruct the texts', () => {
  for (const [reference, prediction] of [['ab', 'ba'], ['aaaa', 'aa'], ['abc', 'cba']]) {
    const r = compareTexts(reference, prediction);
    assert.equal(r.errors, 2);
    assert.equal(r.alignment.map((a) => a.reference ?? '').join(''), reference);
    assert.equal(r.alignment.map((a) => a.prediction ?? '').join(''), prediction);
  }
});
