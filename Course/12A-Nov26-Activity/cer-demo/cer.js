/* Character Error Rate on Unicode code points, matching the notebook's rules. */
(function (root) {
  'use strict';
  const MAX_CHARACTERS = 2000;

  function compareTexts(reference, prediction) {
    if (typeof reference !== 'string' || typeof prediction !== 'string') {
      throw new TypeError('Both inputs must be text.');
    }
    const ref = Array.from(reference);
    const pred = Array.from(prediction);
    const m = ref.length;
    const n = pred.length;
    if (m === 0) throw new Error('Add at least one character to the reference text.');
    if (m > MAX_CHARACTERS || n > MAX_CHARACTERS) {
      throw new Error(`Use up to ${MAX_CHARACTERS.toLocaleString()} characters in each text for this demo.`);
    }

    // Keep two rows of costs and one compact direction per comparison cell.
    // Direction: 0 = diagonal (match/replace), 1 = deletion, 2 = insertion.
    const width = n + 1;
    const directions = new Uint8Array((m + 1) * width);
    let previous = Uint32Array.from({ length: width }, (_, j) => j);
    for (let j = 1; j <= n; j += 1) directions[j] = 2;
    for (let i = 1; i <= m; i += 1) {
      const current = new Uint32Array(width);
      current[0] = i;
      directions[i * width] = 1;
      for (let j = 1; j <= n; j += 1) {
        const diagonal = previous[j - 1] + (ref[i - 1] === pred[j - 1] ? 0 : 1);
        const deletion = previous[j] + 1;
        const insertion = current[j - 1] + 1;
        const best = Math.min(diagonal, deletion, insertion);
        current[j] = best;
        // A stable tie rule selects one of possibly several optimal alignments.
        directions[i * width + j] = best === diagonal ? 0 : best === deletion ? 1 : 2;
      }
      previous = current;
    }

    const alignment = [];
    const counts = { substitutions: 0, deletions: 0, insertions: 0, matches: 0 };
    let i = m;
    let j = n;
    while (i > 0 || j > 0) {
      const direction = directions[i * width + j];
      if (i > 0 && j > 0 && direction === 0) {
        const type = ref[i - 1] === pred[j - 1] ? 'match' : 'substitution';
        counts[type === 'match' ? 'matches' : 'substitutions'] += 1;
        alignment.push({ type, reference: ref[--i], prediction: pred[--j] });
      } else if (i > 0 && (j === 0 || direction === 1)) {
        counts.deletions += 1;
        alignment.push({ type: 'deletion', reference: ref[--i], prediction: null });
      } else {
        counts.insertions += 1;
        alignment.push({ type: 'insertion', reference: null, prediction: pred[--j] });
      }
    }
    alignment.reverse();
    return {
      reference, prediction, referenceLength: m, predictionLength: n,
      ...counts, errors: previous[n], cer: previous[n] / m, alignment,
    };
  }

  const api = { compareTexts, MAX_CHARACTERS };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.CER = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
