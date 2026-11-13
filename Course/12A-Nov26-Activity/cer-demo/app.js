'use strict';

const examples = {
  'two-edits': { reference: 'plant', prediction: 'blat', title: 'Two edits', explanation: 'Replace “p” with “b” and remove “n”. Two edits ÷ five reference characters = 40%.' },
  insertion: { reference: 'cat', prediction: 'chats', title: 'Extra letters', explanation: 'The letters “h” and “s” are extra. Two insertions ÷ three reference characters ≈ 66.67%.' },
  'over-100': { reference: 'a', prediction: 'abcd', title: 'Above 100%', explanation: 'Three extra characters, but only one reference character: 3 ÷ 1 = 300%. CER is an error ratio, so it can exceed 100%.' },
  fact: { reference: 'The card is valid for 4 years.', prediction: 'The card is valid for 5 years.', title: 'One wrong fact', explanation: 'Only “4” becomes “5”: one edit across 30 reference characters ≈ 3.33%. A low CER can still contain a wrong fact. This is a made-up teaching example.' },
  khmer: { reference: 'សួស្តី', prediction: 'សួស្តី!', title: 'Khmer text', explanation: 'One exclamation mark is added. We count Unicode code points, not visible symbols. Khmer vowel signs and other marks can be separate code points.' },
};

const byId = (id) => document.getElementById(id);
const referenceInput = byId('reference');
const predictionInput = byId('prediction');
const panel = document.querySelector('.result-panel');
const exampleButtons = Array.from(document.querySelectorAll('[data-example]'));
let latestResult = null;
let activeExample = 'two-edits';

function visibleCharacter(character) {
  if (character === null) return '∅';
  if (character === ' ') return '␠';
  if (character === '\n') return '↵';
  if (character === '\r') return '␍';
  if (character === '\t') return '⇥';
  return character;
}

function updateLengths() {
  for (const [input, countId] of [[referenceInput, 'reference-count'], [predictionInput, 'prediction-count']]) {
    const length = Array.from(input.value).length;
    byId(countId).textContent = `${length.toLocaleString()} character${length === 1 ? '' : 's'}`;
  }
}

function handleInput() {
  activeExample = null;
  exampleButtons.forEach((button) => button.setAttribute('aria-pressed', 'false'));
  calculate();
}

function renderAlignment(result) {
  const fragment = document.createDocumentFragment();
  const symbols = { match: '·', substitution: 'S', deletion: 'D', insertion: 'I' };
  for (const item of result.alignment) {
    const pair = document.createElement('div');
    pair.className = 'character-pair';
    pair.setAttribute('role', 'listitem');
    const description = `${item.type}: reference ${JSON.stringify(item.reference)}, prediction ${JSON.stringify(item.prediction)}`;
    pair.setAttribute('aria-label', description);
    pair.title = description;
    const label = document.createElement('span');
    label.className = 'operation-label';
    label.textContent = symbols[item.type];
    label.setAttribute('aria-hidden', 'true');
    pair.append(label);
    for (const character of [item.reference, item.prediction]) {
      const cell = document.createElement('span');
      cell.className = `character-cell ${item.type}${character === null ? ' gap' : ''}`;
      cell.textContent = visibleCharacter(character);
      cell.setAttribute('aria-hidden', 'true');
      pair.append(cell);
    }
    fragment.append(pair);
  }
  byId('alignment').replaceChildren(fragment);
  document.querySelector('.alignment-box').scrollLeft = 0;
}

function calculate() {
  updateLengths();
  try {
    const result = CER.compareTexts(referenceInput.value, predictionInput.value);
    latestResult = result;
    byId('score').textContent = (result.cer * 100).toFixed(2);
    byId('result-tag').textContent = `${result.errors} edit${result.errors === 1 ? '' : 's'}`;
    byId('result-description').textContent = `${result.errors} character edit${result.errors === 1 ? '' : 's'} across ${result.referenceLength} reference character${result.referenceLength === 1 ? '' : 's'}.`;
    byId('formula-numerator').textContent = `${result.substitutions} + ${result.deletions} + ${result.insertions}`;
    byId('formula-denominator').textContent = result.referenceLength;
    byId('formula-result').textContent = result.cer.toFixed(4);
    for (const count of ['substitutions', 'deletions', 'insertions']) byId(count).textContent = result[count];
    renderAlignment(result);
    byId('example-explanation').textContent = activeExample
      ? examples[activeExample].explanation
      : 'S = replaced, D = missing, I = added. CER = (S + D + I) ÷ reference characters. Matching characters add no errors.';
    byId('result-status').textContent = activeExample
      ? `Showing the “${examples[activeExample].title}” example.`
      : 'Updates as you type. Nothing is sent to a server.';
    byId('download-button').disabled = false;
    byId('error-message').hidden = true;
    panel.classList.remove('is-stale');
  } catch (error) {
    // An invalid input has no current score; do not leave an old result visible.
    latestResult = null;
    byId('score').textContent = '—';
    byId('result-tag').textContent = 'No result';
    byId('result-description').textContent = 'Enter valid text to see the live result.';
    byId('formula-numerator').textContent = 'S + D + I';
    byId('formula-denominator').textContent = 'N';
    byId('formula-result').textContent = '—';
    for (const count of ['substitutions', 'deletions', 'insertions']) byId(count).textContent = '—';
    byId('alignment').replaceChildren();
    byId('example-explanation').textContent = 'CER needs at least one reference character. An empty prediction is allowed.';
    byId('error-message').textContent = error.message;
    byId('error-message').hidden = false;
    panel.classList.add('is-stale');
    byId('result-status').textContent = 'Check the message below the text boxes. Results update automatically when the input is valid.';
    byId('download-button').disabled = true;
    referenceInput.setAttribute('aria-invalid', String(Array.from(referenceInput.value).length === 0 || Array.from(referenceInput.value).length > CER.MAX_CHARACTERS));
    predictionInput.setAttribute('aria-invalid', String(Array.from(predictionInput.value).length > CER.MAX_CHARACTERS));
    return;
  }
  referenceInput.removeAttribute('aria-invalid');
  predictionInput.removeAttribute('aria-invalid');
}

function loadExample(key) {
  referenceInput.value = examples[key].reference;
  predictionInput.value = examples[key].prediction;
  activeExample = key;
  exampleButtons.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.example === key)));
  calculate();
}

byId('compare-form').addEventListener('submit', (event) => { event.preventDefault(); calculate(); });
referenceInput.addEventListener('input', handleInput);
predictionInput.addEventListener('input', handleInput);
exampleButtons.forEach((button) => button.addEventListener('click', () => loadExample(button.dataset.example)));
document.querySelector('[data-load-fact]').addEventListener('click', () => {
  loadExample('fact');
  byId('calculator').scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
  referenceInput.focus({ preventScroll: true });
});
byId('clear-button').addEventListener('click', () => {
  referenceInput.value = '';
  predictionInput.value = '';
  handleInput();
  referenceInput.focus();
});
byId('download-button').addEventListener('click', () => {
  if (!latestResult || byId('download-button').disabled) return;
  const report = {
    title: 'CER Lab — character comparison',
    rules: { unit: 'Unicode code points', textCleanup: 'none', emptyReference: 'rejected', alignment: 'one minimum-edit alignment' },
    ...latestResult,
  };
  const url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = 'cer-result.json';
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

calculate();
