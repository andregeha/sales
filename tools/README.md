# Tools

Scripts this workspace builds for itself. Owned by the **`ofs-builder`** agent.

## Rules
- Standard library first; dependency-light.
- Every tool has a `--help` and a header saying what it does and who it is for.
- **Read-only against anything client-related.** Gaia can place real orders, post accounting and
  send SMS/email — a write is never acceptable from here.
- **No credentials, connection strings, server names or client data** in this repo, ever.
- Deck building lives in the `ofs-marketing` repo with its brand kit and QA gates — not here.

*(Empty for now — tools get built as real needs appear, not speculatively.)*
