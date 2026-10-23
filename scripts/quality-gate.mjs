#!/usr/bin/env node
// Quality gate: one command for local and CI. Node stdlib only.
// Usage: node scripts/quality-gate.mjs
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const MB = 1024 * 1024;
const MEDIA_EXT = ['.mp4', '.mov', '.wav', '.mp3'];
const MEDIA_LIMIT = 1 * MB;
const FILE_LIMIT = 5 * MB;
const FORBIDDEN_BASENAMES = ['.env', 'config.toml'];

// entries: [{ path, size }] -> list of violation messages.
export function findForbidden(entries) {
  const out = [];
  for (const { path: p, size } of entries) {
    const base = p.split('/').pop() ?? '';
    if (FORBIDDEN_BASENAMES.includes(base)) out.push(`tracked forbidden file: ${p}`);
    if (MEDIA_EXT.includes(path.extname(base).toLowerCase()) && size > MEDIA_LIMIT) out.push(`media > 1 MB: ${p} (${size} bytes)`);
    if (size > FILE_LIMIT) out.push(`file > 5 MB: ${p} (${size} bytes)`);
  }
  return out;
}

function main() {
  const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
  const results = [];
  const record = (name, ok, detail = '') => {
    results.push(ok);
    console.log(`${ok ? 'PASS' : 'FAIL'}: ${name}`);
    if (!ok && detail) console.log(detail.trimEnd().split('\n').map((l) => `  ${l}`).join('\n'));
  };
  const run = (name, cmd, args) => {
    const r = spawnSync(cmd, args, { cwd: root, encoding: 'utf8' });
    record(name, r.status === 0, `${r.stdout ?? ''}${r.stderr ?? ''}${r.error ? r.error.message : ''}`);
  };

  run('framework-check', process.execPath, ['scripts/framework-check.mjs']);

  const reqDir = path.join(root, 'docs/product/requirements');
  const reqs = fs.existsSync(reqDir)
    ? fs.readdirSync(reqDir).filter((f) => /^REQ-.*\.md$/.test(f)).sort() : [];
  for (const f of reqs) run(`product-check ${f}`, process.execPath, ['scripts/product-check.mjs', `docs/product/requirements/${f}`]);

  const tests = fs.existsSync(path.join(root, 'tests'))
    ? fs.readdirSync(path.join(root, 'tests')).filter((f) => f.endsWith('.test.mjs')).sort().map((f) => `tests/${f}`) : [];
  if (tests.length) run('node --test', process.execPath, ['--test', ...tests]);
  else record('node --test', false, 'no tests/*.test.mjs found');

  if (fs.existsSync(path.join(root, 'pyproject.toml'))) run('pytest', 'python', ['-m', 'pytest', '-q']);

  const ls = spawnSync('git', ['ls-files', '-z'], { cwd: root, encoding: 'utf8', maxBuffer: 64 * MB });
  if (ls.status !== 0) record('forbidden files', false, ls.stderr ?? 'git ls-files failed');
  else {
    const entries = ls.stdout.split('\0').filter(Boolean).flatMap((p) => {
      const abs = path.join(root, p);
      return fs.existsSync(abs) ? [{ path: p, size: fs.statSync(abs).size }] : [];
    });
    const bad = findForbidden(entries);
    record('forbidden files', bad.length === 0, bad.join('\n'));
  }

  const ok = results.every(Boolean);
  console.log(ok ? 'QUALITY GATE: PASS' : 'QUALITY GATE: FAIL');
  process.exit(ok ? 0 : 1);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
