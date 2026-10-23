#!/usr/bin/env node

import fs from 'node:fs';
import process from 'node:process';

const file = process.argv[2];
if (!file) { console.error('Usage: node scripts/product-check.mjs <REQ-file>'); process.exit(2); }
if (!fs.existsSync(file)) { console.error(`FAIL: file not found: ${file}`); process.exit(1); }

const source = fs.readFileSync(file, 'utf8');
const errors = [];
const name = file.split('/').pop() ?? '';
if (!/^REQ-[0-9]+-.+\\.md$/.test(name)) errors.push('filename must match REQ-<number>-<slug>.md');

const fm = source.match(/^---\\n([\\s\\S]*?)\\n---/);
if (!fm) errors.push('missing YAML frontmatter');
const status = fm?.[1]?.match(/^status:\\s*(\\S+)\\s*$/m)?.[1];
if (!status) errors.push('frontmatter missing status');
if (status && !['DRAFT','NEEDS_CLARIFICATION','READY','OBSOLETE'].includes(status)) errors.push(`invalid status: ${status}`);

for (const section of [
  '## 1. Problem','## 2. Goal','## 3. Actors','## 4. Current workflow / context',
  '## 5. Desired workflow / outcome','## 6. Functional requirements','## 10. Acceptance criteria',
  '## 11. Out of scope','## 13. Open questions','## 14. Readiness','## 15. Traceability'
]) if (!source.includes(section)) errors.push(`missing section: ${section}`);

if (/<!--\\s*(FILL|TBD|TODO):/i.test(source)) errors.push('unresolved template marker');

if (status === 'READY') {
  if (!/^### FR-\\d{3}/m.test(source)) errors.push('READY requirement needs at least one FR-###');
  if (!/^### AC-\\d{3}/m.test(source)) errors.push('READY requirement needs at least one AC-###');
  const oq = source.match(/## 13\\. Open questions[\\s\\S]*?(?=\\n## 14\\.)/)?.[0] ?? '';
  if (!/\\bNone\\b/i.test(oq)) errors.push('READY requirement must have Open questions = None');
  const rd = source.match(/## 14\\. Readiness[\\s\\S]*?(?=\\n## 15\\.)/)?.[0] ?? '';
  if ((rd.match(/^- \\[ \\]/gm) ?? []).length) errors.push('READY requirement still has unchecked readiness items');
}

if (errors.length) { for (const e of errors) console.error(`FAIL: ${e}`); process.exit(1); }
console.log(`PASS: product requirement ${file}`);