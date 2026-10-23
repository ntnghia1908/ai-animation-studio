#!/usr/bin/env python3
"""Token audit: Claude Code cost (main session vs subagents), context waste and cost per merged PR, from local transcripts.

Usage: python3 scripts/token-audit.py --project SUBSTR --repo PATH [--since YYYY-MM-DD] [--until YYYY-MM-DD]
Reads ~/.claude/projects/*/*.jsonl (main) and */*/subagents/*.jsonl, ~/.codex/sessions; prints aggregates only.
Both project and repo are required: Claude directory names and Codex session cwd match SUBSTR.
PATH is used only for merged-PR counts; project matching includes sibling worktrees and moved repositories.
Cost uses fixed API-price comparison coefficients, not the subscription bill or a live price quote.
Policy and periodic measurement: docs/ai/workflow.md §10 (core/docs/ai/workflow.md in the kit).
Cold resumes are gaps >1h (main) or >5m (subagent); large rewrites after those gaps are a heuristic,
not proof of cache expiry. Context percentage is excess tokens above the threshold / all main input tokens.
$/PR uses first-parent merge commits on --merge-ref; squash/rebase merges need an external task count.
"""
import argparse
import datetime
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Fixed $/MTok coefficients ported from the source audit: input, cache read, output.
# Review coefficients before comparing periods with different models/pricing; unknown families are skipped.
# Cache write = input × 2 (1h TTL) or × 1.25 (5m TTL).
PRICES = {"opus": (4.0, 0.2, 20.0), "sonnet": (2.0, 0.2, 10.0), "haiku": (0.1, 0.01, 0.5)}
BIG_REWRITE = 50_000  # Large writes after a cold gap are heuristic full-context rewrites.


def family(model):
    return next((f for f in PRICES if f in (model or "")), None)


def turns(path: Path):
    """One record per API message (streamed chunks share a message id; output_tokens grows, keep the max)."""
    msgs = {}
    for index, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines()):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        message = event.get("message") if event.get("type") == "assistant" else None
        usage = message.get("usage") if isinstance(message, dict) else None
        if not usage or not family(message.get("model")):
            continue
        rec = msgs.setdefault(message.get("id") or event.get("uuid") or index, {"model": family(message["model"]), "usage": usage, "out": 0,
                                                   "ts": event.get("timestamp", "")})
        rec["out"] = max(rec["out"], usage.get("output_tokens", 0))
    return sorted(msgs.values(), key=lambda r: r["ts"])


def cache_written(usage):
    return usage.get("cache_creation_input_tokens", sum((usage.get("cache_creation") or {}).values()))


def cost(rec, is_main=True):
    price_in, price_read, price_out = PRICES[rec["model"]]
    u = rec["usage"]
    split = u.get("cache_creation") or {}
    write_1h = split.get("ephemeral_1h_input_tokens", 0)
    write_5m = split.get("ephemeral_5m_input_tokens", 0)
    if not split:
        # Older transcripts omit the TTL split; infer the adapter default by role.
        write_1h = cache_written(u) if is_main else 0
        write_5m = 0 if is_main else cache_written(u)
    return (u.get("input_tokens", 0) * price_in + write_1h * price_in * 2 + write_5m * price_in * 1.25
            + u.get("cache_read_input_tokens", 0) * price_read + rec["out"] * price_out) / 1e6


def context(rec):
    u = rec["usage"]
    return u.get("input_tokens", 0) + cache_written(u) + u.get("cache_read_input_tokens", 0)


def timestamp(value):
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.replace(tzinfo=parsed.tzinfo or datetime.timezone.utc)
    except (ValueError, TypeError, AttributeError):
        return None


def cold_gap(previous, current, ttl):
    before = timestamp(previous["ts"]) if previous else None
    after = timestamp(current["ts"])
    return bool(before and after and (after - before).total_seconds() > ttl)


def agent_type(path: Path):
    if path.parent.name != "subagents":
        return "MAIN"
    meta = path.with_suffix(".meta.json")
    try:
        return "subagent:" + json.loads(meta.read_text()).get("agentType", "?")
    except (OSError, ValueError):
        return "subagent:?"


def merged_prs(repo: Path, since, until, ref):
    result = subprocess.run(["git", "-C", str(repo), "log", "--merges", "--first-parent", "--format=%cs",
                             ref, "--"], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"cannot count merges on {ref}: {result.stderr.strip()}")
    return sum(since <= day <= until for day in result.stdout.split())


def codex_tokens(since, until, project):
    total, cached = 0, 0
    for log in (Path.home() / ".codex" / "sessions").glob("*/*/*/*.jsonl"):
        previous = {"input_tokens": 0, "cached_input_tokens": 0}
        matches = False
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if not isinstance(event, dict):
                continue
            payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
            if event.get("type") == "session_meta" and payload.get("cwd"):
                matches = project in payload["cwd"]
            if payload.get("type") == "token_count" and payload.get("info"):
                current = payload["info"].get("total_token_usage")
                if not current:
                    continue
                if matches and since <= event.get("timestamp", "")[:10] <= until:
                    total += max(0, current.get("input_tokens", 0) - previous.get("input_tokens", 0))
                    cached += max(0, current.get("cached_input_tokens", 0) - previous.get("cached_input_tokens", 0))
                previous = current
    return total, cached


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", default="2000-01-01", help="inclusive YYYY-MM-DD (default: all history)")
    parser.add_argument("--until", default="2999-12-31", help="inclusive YYYY-MM-DD (default: all history)")
    parser.add_argument("--project", required=True, help="required nonempty substring of the ~/.claude/projects directory name and Codex session cwd; no default")
    parser.add_argument("--repo", required=True, type=Path, help="required local Git repository for merged-PR counts only; no default")
    parser.add_argument("--merge-ref", default="main", help="branch/ref whose first-parent merges represent PRs (default: main)")
    parser.add_argument("--context-threshold", type=int, default=250_000, help="context budget in tokens (default: 250000; match project-profile)")
    args = parser.parse_args()
    try:
        datetime.date.fromisoformat(args.since)
        datetime.date.fromisoformat(args.until)
    except ValueError:
        parser.error("--since and --until must be YYYY-MM-DD dates")
    if args.since > args.until or not args.project.strip() or args.context_threshold <= 0:
        parser.error("require since <= until, nonempty --project and positive --context-threshold")
    repo = args.repo.expanduser().resolve()
    try:
        prs = merged_prs(repo, args.since, args.until, args.merge_ref)
    except (OSError, RuntimeError) as exc:
        parser.exit(1, f"token-audit: {exc}\n")

    root = Path.home() / ".claude" / "projects"
    paths = [p for p in list(root.glob("*/*.jsonl")) + list(root.glob("*/*/subagents/*.jsonl"))
             if args.project in p.relative_to(root).parts[0]]
    by_agent = defaultdict(lambda: [0, 0.0])  # (agent, model) -> turns, $
    main_input, above = 0, {t: 0 for t in sorted({150_000, args.context_threshold})}
    rewrites = {"MAIN": [0, 0], "subagent": [0, 0]}  # count, tokens
    resumes = {"MAIN": [0, 0], "subagent": [0, 0]}  # cold gaps, cache-write tokens on return
    peaks = []
    for path in paths:
        agent, prev, peak = agent_type(path), None, 0
        is_main = path.parent.name != "subagents"
        kind, ttl = ("MAIN", 3600) if is_main else ("subagent", 300)
        for rec in turns(path):
            cold = cold_gap(prev, rec, ttl)
            prev = rec  # Keep history before --since to detect a cold return inside the period.
            day = rec["ts"][:10]
            if not args.since <= day <= args.until:
                continue
            by_agent[(agent, rec["model"])][0] += 1
            by_agent[(agent, rec["model"])][1] += cost(rec, is_main)
            ctx, u = context(rec), rec["usage"]
            written = cache_written(u)
            if cold:
                resumes[kind][0] += 1
                resumes[kind][1] += written
            if cold and written > BIG_REWRITE and u.get("cache_read_input_tokens", 0) < written:
                rewrites[kind][0] += 1
                rewrites[kind][1] += written
            if is_main:
                main_input += ctx
                for t in above:
                    above[t] += max(0, ctx - t)
                peak = max(peak, ctx)
        if is_main and peak:
            peaks.append(peak)

    total = sum(v[1] for v in by_agent.values())
    print(f"period {args.since} .. {args.until}, projects matching '{args.project}': ${total:.2f} (fixed API-price equivalent)")
    print(f"matched Claude transcript files: {len(paths)}; unknown model families excluded")
    for (agent, model), (n, usd) in sorted(by_agent.items(), key=lambda kv: -kv[1][1]):
        print(f"  {agent:24} {model:7} turns {n:6}  ${usd:7.2f}  {100 * usd / max(total, 1e-9):5.1f}%")
    sub = sum(v[1] for k, v in by_agent.items() if k[0] != "MAIN")
    print(f"subagent share: {100 * sub / max(total, 1e-9):.0f}%")
    for t in above:
        print(f"main input above {t} tokens context (excess / total): {100 * above[t] / max(main_input, 1):.1f}%")
    if peaks:
        peaks.sort()
        print(f"main session peak context: median {peaks[len(peaks) // 2] // 1000}k, p90 {peaks[int(.9 * len(peaks))] // 1000}k"
              f" ({len(peaks)} sessions)")
    for kind, (n, tok) in rewrites.items():
        print(f"{kind} cache-expired rewrites (heuristic): {n} ({tok / 1e6:.1f}M tokens)")
    for kind, (n, tok) in resumes.items():
        ttl = "1h" if kind == "MAIN" else "5m"
        print(f"{kind} cold resumes (>{ttl}): {n} ({tok / 1e6:.1f}M cache-write tokens)")
    print(f"merged PRs on {args.merge_ref} (merge commits): {prs}  -> "
          + (f"${total / prs:.2f}/PR" if prs else "$/PR: N/A (no merges)"))
    codex_in, codex_cached = codex_tokens(args.since, args.until, args.project)
    print(f"codex input tokens: {codex_in / 1e6:.1f}M ({100 * codex_cached / max(codex_in, 1):.0f}% cached; separate subscription)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
