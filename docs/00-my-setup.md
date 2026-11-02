# 00 – My Setup (decided)

> iPad = remote control. Mac mini = engine room. GitHub = single source of truth.
> Python first. Everything runs for me only, on my private network.

## Decisions

| Area | Choice | Not doing (for now) |
|------|--------|---------------------|
| Hardware | **Mac mini** (M-series, ≥16 GB, 24–32 GB if local models), always on | GPU rig, second laptop |
| Daily device | **iPad + keyboard** | |
| Coding agent | **Claude Code** – cloud sessions on iPad, CLI on Mac mini, Remote Control between them | Paying for Copilot at home (stays at work) |
| Second opinion | **OpenAI Codex** (already in my ChatGPT Business plan) for comparing approaches | Learning a third agent tool |
| Editor | **VS Code** on the Mac mini (Remote-SSH / browser) | |
| Network | **Tailscale** – iPad, phone, Mac mini in one private network | Port forwarding, public servers |
| Terminal on iPad | **Blink Shell** or **Termius** (SSH/mosh via Tailscale) | |
| Language | **Python** (`uv` for everything) | TypeScript until a UI really needs React |
| Agents | **Claude Agent SDK (Python)** – orchestrator + subagents + MCP | LangChain & co. |
| Connectors | **MCP servers** written with the official Python SDK (`mcp`, FastMCP) | |
| UI | **Streamlit** for quick custom interfaces (FastAPI when another app needs an API) | Next.js (later, maybe) |
| Hosting | **The Mac mini itself**, reachable via `tailscale serve` | Vercel/Railway/Fly (only if something becomes public) |

## Accounts & money – two separate things

| What | Pays for | Where |
|------|----------|-------|
| Claude / ChatGPT **Business** seats | *Me* using Claude Code, Claude app, ChatGPT, Codex | already have |
| **API keys** (Anthropic Console, OpenAI Platform) | *My apps and agents* calling models | platform.claude.com / platform.openai.com – separate billing |

- Set a **monthly spend limit** on each API key on day one (e.g. €20 to start).
- If the business seats belong to my employer: check that personal projects are allowed,
  and keep work and personal repos/keys strictly separate.
- Keys live in `.env` files on the Mac mini, never in git.

## Mac mini – one-evening setup checklist

**System**
- [ ] macOS updated, FileVault on
- [ ] System Settings → Energy: prevent automatic sleep, start up after power failure
- [ ] System Settings → General → Sharing: **Remote Login (SSH)** on

**Network**
- [ ] Tailscale installed on Mac mini, iPad and phone; all signed in to the same account
- [ ] From the iPad: SSH into the Mac mini via its Tailscale name (Blink/Termius)

**Dev tools** (in Terminal on the Mac mini)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git gh tmux
curl -LsSf https://astral.sh/uv/install.sh | sh     # Python + packages
gh auth login                                        # GitHub
# Claude Code: install per https://code.claude.com/docs, then:
claude                                               # log in with the Business account
```
- [ ] VS Code installed (+ Python extension)
- [ ] `~/code/` folder; clone this repo into it

**Bridge iPad ↔ Mac mini**
- [ ] Claude Code **Remote Control** on for `~/code` (Claude desktop app → Settings → Claude Code →
      Remote Control, or run `claude remote-control` in the folder). Now sessions started on the iPad
      can work directly on the Mac mini.
- [ ] Long jobs run inside `tmux` so they survive a closed iPad

**Personal Claude config**
- [ ] `~/.claude/CLAUDE.md` with my personal rules (Python + uv, explain like a junior,
      small commits, tests before commit) – applies to every project

## How a working session looks

```
iPad ── Claude app / claude.ai/code ──► Remote Control ──► Mac mini (~/code/<repo>)
  │                                                          ├─ Claude Code edits, runs tests
  └── Safari ── http://mac-mini.<tailnet>:8501 ◄─────────────┘  Streamlit UI / agent running
```

- **Planning/reading on the go:** cloud session on the repo (no Mac needed).
- **Building:** Remote Control session on the Mac mini (real files, real tools, MCP servers).
- **Using what I built:** open the Streamlit app over Tailscale in Safari.

## Target architecture

```
Streamlit UI (custom interface)
      │
Orchestrator agent  (Claude Agent SDK, Python)
      ├── subagent: researcher
      ├── subagent: coder / reviewer
      └── MCP servers (my connectors): notes, calendar, own APIs, DBs …
```

## Build order (each step = one small finished project)

| # | Project | New concept |
|---|---------|-------------|
| 01 | `projects/01-tool-agent` (exists) | API call, function calling, agent loop by hand |
| 02 | **My first MCP server** – e.g. a notes or to-do connector; use it from Claude Code | MCP, tools as a reusable service |
| 03 | **Agent SDK orchestrator** – uses the MCP server from 02 + one subagent | Agent SDK, subagents, permissions |
| 04 | **Streamlit UI** for the orchestrator, served over Tailscale | Custom interface, streaming |
| 05 | **Make it always-on** – runs on schedule / as a service on the Mac mini | Ops: logs, restarts, costs |

Rule: don't start N+1 before N works and I can explain it.
