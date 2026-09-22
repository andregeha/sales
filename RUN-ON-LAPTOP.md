# Running this on your laptop — the primary way to run this workspace

> **Decided 2026-09-22: the laptop is where this runs.** The cloud environment blocks every
> regulator register and tender portal, which is most of the job. The laptop has normal internet.
>
> **Git is the spine.** Both environments use the same repository and the same branch, so nothing is
> tied to a machine — commit and push, and any session anywhere picks up exactly where you left off.
> That is why moving is cheap and reversible.

## Easiest route — the Claude Code desktop app
Claude Code ships as a **desktop app for Windows and Mac** — same tool, no terminal.
Get it at https://claude.com/claude-code, open it, and point it at the `sales` folder.
Then paste the prompt below. That's it.

The desktop app runs **on your machine**, so it has your internet connection — which is the entire
reason for doing this.

## Or the terminal, if you prefer
```bash
git clone https://github.com/andregeha/sales
cd sales
git checkout claude/dreamy-rubin-v70dkq
claude
```

## ⚠ Windows: Python
The CRM tooling needs Python, and Windows does not ship it. If you see
*"Python was not found; run without arguments to install from the Microsoft Store"*, that is this.
**You do not need to fix it yourself** — the prompt below tells the session to sort it out.
If you would rather do it once and forget: install from https://www.python.org/downloads/ and tick
**"Add Python to PATH"** during setup. Note that on Windows the command is `python`, not `python3`.

## Then paste this

```
Read CLAUDE.md, memory/ and tools/connectors/README.md.

First: this is a Windows machine and Python may not be installed. Check, and if it is
missing, install it (and PyYAML) so tools/crm.py runs. On Windows the command is
usually `python`, not `python3` — if you add any scripts or docs, make them work on
both.

You are running on Andre's laptop, which has full internet access — unlike the cloud
environment, where regulator and tender websites are blocked. That is the whole reason
this session exists.

Do these, in order:

1. Verify you really can reach the sources. Try geco.amf-france.org, data.gouv.fr,
   cma.org.sa, etimad.sa, boamp.fr and ted.europa.eu. Report honestly which work.

2. Build and TEST the regulator register connectors described in
   tools/connectors/README.md. Start with France (AMF GECO — a downloadable dataset,
   the easiest) and Saudi (CMA licensed institutions). Run them for real, against the
   live sources, and show the output.

3. Run a proper RFP radar pass now that you can actually open Etimad, BOAMP and TED —
   search inside the portals rather than guessing from search snippets. Record anything
   real in the CRM with its deadline.

4. Commit and push everything to this branch.

Rules that do not change: never invent a company, contact, deadline or metric; never
contact anyone — Andre approves and sends; log everything in the CRM; update memory/.
```

## What you get out of it
- **Automatic new-licence detection.** Every morning the connectors pull each regulator's list of
  licensed firms, compare it to yesterday's, and create a CRM record for anything new. A firm that
  just got licensed needs a portfolio system and has no incumbent — the best lead signal we have.
- **A real RFP radar.** Searching *inside* Etimad, BOAMP and TED instead of hoping a search engine
  indexed them.

## Setting up the daily run here
The cloud schedule was **disabled on 2026-09-22** when the laptop became primary, so nothing runs
automatically right now. To get the daily cycle back, ask the laptop session:

> *"Set up the daily run on this machine — weekday mornings, running the /daily-run skill.
> Use Windows Task Scheduler or whatever is most reliable here, and tell me how to check it ran."*

It only fires when the laptop is on and awake. That is the trade-off of running locally, and it is
why the cloud schedule existed. If the cloud network policy is ever widened, re-enable that schedule
and you get unattended runs back.

## The old catch (now historical)
This mattered while the cloud ran the schedule. It is now disabled, so it is moot — but the design
requirement stands: **a connector that cannot reach its source must fail loudly**, saying so in the
brief, never returning an empty result that reads as a quiet day.

If the cloud network restriction is ever lifted
(https://code.claude.com/docs/en/claude-code-on-the-web), re-enable the schedule and you get
unattended daily runs back on top of the laptop work.
