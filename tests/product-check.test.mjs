import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const NEW_CHECKER = path.join(ROOT, 'scripts/product-check.mjs');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'product-check-'));
test.after(() => fs.rmSync(tmp, { recursive: true, force: true }));

const SECTIONS = ['## 1. Problem', '## 2. Goal', '## 3. Actors', '## 4. Current workflow / context',
  '## 5. Desired workflow / outcome', '## 6. Functional requirements', '## 10. Acceptance criteria',
  '## 11. Out of scope'];

function req({ status = 'READY', frontmatter = true, openQuestions = 'None', unchecked = false } = {}) {
  const fm = frontmatter ? `---\nid: REQ-009\nstatus: ${status}\n---\n` : '';
  return `${fm}# REQ\n\n${SECTIONS.join('\n\nx\n\n')}\n\n### FR-001 a\n\n### AC-001 b\n\n` +
    `## 13. Open questions\n\n${openQuestions}\n\n## 14. Readiness\n\n- [${unchecked ? ' ' : 'x'}] done\n\n## 15. Traceability\n\nx\n`;
}

function write(name, content) {
  const p = path.join(tmp, name);
  fs.writeFileSync(p, content);
  return p;
}

function run(checker, file) {
  return spawnSync(process.execPath, [checker, file], { encoding: 'utf8' });
}

test('valid READY requirement passes', () => {
  const r = run(NEW_CHECKER, write('REQ-009-ok.md', req()));
  assert.equal(r.status, 0, r.stderr);
});

test('missing frontmatter fails', () => {
  const r = run(NEW_CHECKER, write('REQ-010-nofm.md', req({ frontmatter: false })));
  assert.equal(r.status, 1);
  assert.match(r.stderr, /missing YAML frontmatter/);
});

test('READY with open question fails', () => {
  const r = run(NEW_CHECKER, write('REQ-011-oq.md', req({ openQuestions: 'Q1: what?' })));
  assert.equal(r.status, 1);
  assert.match(r.stderr, /Open questions = None/);
});

test('READY with unchecked readiness item fails', () => {
  const r = run(NEW_CHECKER, write('REQ-012-unchecked.md', req({ unchecked: true })));
  assert.equal(r.status, 1);
  assert.match(r.stderr, /unchecked readiness/);
});

test('bad filename fails', () => {
  const r = run(NEW_CHECKER, write('requirement.md', req()));
  assert.equal(r.status, 1);
  assert.match(r.stderr, /filename must match/);
});

test('old checker (76abae8) falsely fails a valid requirement, new one passes', () => {
  const old = spawnSync('git', ['show', '76abae8:scripts/product-check.mjs'], { cwd: ROOT, encoding: 'utf8' });
  if (old.status !== 0) return; // shallow clone without that commit: nothing to compare
  const oldPath = path.join(tmp, 'old-product-check.mjs');
  fs.writeFileSync(oldPath, old.stdout);
  const file = write('REQ-013-regress.md', req());
  assert.equal(run(oldPath, file).status, 1);
  assert.equal(run(NEW_CHECKER, file).status, 0);
});
