# Running this on your laptop

> **Why:** the cloud environment blocks access to regulator websites, so the register pulls and the
> RFP radar can't work there. Your laptop has normal internet, so they can.
> **Who this is for:** Andre. Five minutes, once.

## What you need once
1. **Claude Code on your laptop** — https://claude.com/claude-code (if you already use it, skip).
2. **Git** — almost certainly already installed.

## The five steps
Open a terminal and run these, one at a time:

```bash
git clone https://github.com/andregeha/sales
cd sales
git checkout claude/dreamy-rubin-v70dkq
python3 -m pip install pyyaml
claude
```

That last command starts Claude Code inside the project. It will read `CLAUDE.md` automatically and
know the whole mission, the territory, the rules and everything decided so far.

## Then paste this

```
Read CLAUDE.md, memory/ and tools/connectors/README.md.

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

## The one catch, so it isn't a surprise
The **7am scheduled run still happens in the cloud**, where the sites stay blocked. So:
- Connectors run properly **when you run them on your laptop**.
- In the cloud they will **say clearly in your brief that the registers were unreachable** — they
  will not fail silently or pretend they found nothing.

If you later get the cloud environment's network restriction lifted
(https://code.claude.com/docs/en/claude-code-on-the-web), everything runs unattended and the laptop
stops being necessary.
