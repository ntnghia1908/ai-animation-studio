import test from 'node:test';
import assert from 'node:assert/strict';
import { findForbidden } from '../scripts/quality-gate.mjs';

const MB = 1024 * 1024;

test('clean entries produce no violations', () => {
  assert.deepEqual(findForbidden([
    { path: 'a.md', size: 100 },
    { path: 'clip.mp4', size: MB },
    { path: 'big.bin', size: 5 * MB },
  ]), []);
});

test('media over 1 MB is flagged', () => {
  for (const ext of ['mp4', 'mov', 'wav', 'mp3']) {
    assert.equal(findForbidden([{ path: `x/a.${ext}`, size: MB + 1 }]).length, 1, ext);
  }
});

test('any file over 5 MB is flagged', () => {
  assert.equal(findForbidden([{ path: 'a.bin', size: 5 * MB + 1 }]).length, 1);
});

test('.env and config.toml by basename are flagged', () => {
  assert.equal(findForbidden([{ path: '.env', size: 1 }, { path: 'sub/config.toml', size: 1 }]).length, 2);
  assert.equal(findForbidden([{ path: 'sub/.env.example', size: 1 }, { path: 'pyproject.toml', size: 1 }]).length, 0);
});
