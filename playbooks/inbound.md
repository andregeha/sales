# Inbound

> ⚠ **Honest position: we have almost no inbound surface today, so there is very little to run.**
> This playbook says what inbound would mean for OFS and what it would take — it is a plan awaiting
> a decision, not a motion we are currently executing. Treating it as live would be pretending.

## What exists now
- The OFS website (`omega-financial-solutions.com`) — a brochure site. Unknown whether it has any
  form, tracking, or analytics we can see. **Open question for Andre.**
- The Gaia brochure and the deck library in `ofs-marketing`.
- Andre's own network and LinkedIn presence.

That is the whole surface. There is no blog, no content cadence, no lead-capture form we control,
no newsletter, and no visibility into who visits. **So "inbound" today means roughly zero leads**,
and no amount of process in this repo changes that.

## What inbound would actually be worth
Our buyers — a bank COO, a family-office principal, a head of operations at an asset manager — do
not fill in "request a demo" forms. What reaches them is:
1. **Being findable at the moment of need.** When someone searches for a portfolio management system
   that handles CMA Lebanon constraints, or fund NAV with multi-share classes, or a client portal in
   Arabic, we should be the result. That is a small number of very specific searches with very high
   intent — and almost no competition on the long tail.
2. **Credible substance, not marketing.** A clear public explanation of how pre-trade compliance
   actually works, or what migrating off a legacy portfolio system really involves, does more than
   any campaign. Our knowledge base already contains most of this material.
3. **Presence where they already are** — industry associations, regulator-adjacent events, private
   wealth and asset management conferences in Dubai, Riyadh, Beirut and Paris.
4. **Andre's own voice on LinkedIn.** By far the highest-leverage, lowest-cost channel available:
   he is credible, senior, and already in these markets.

## What we would need to decide
1. **Do we control the website** enough to add pages, a form, and analytics?
2. **Will Andre publish** — under his own name, at a sustainable cadence? Without that, content
   inbound does not start.
3. **Is there budget** for events or paid search, or is this organic only?
4. **Who handles a form fill within an hour?** An inbound lead that waits a day is a lost one.

All four are in `memory/open-questions.md`.

## The honest recommendation
**Do not start a content programme yet.** Outbound is where the leverage is right now: we know the
four markets, the registers are public, the segments are defined, and every lead can be personalised
on a real trigger. Inbound compounds, but slowly, and it needs a sustained commitment that has not
been made.

The one exception worth doing immediately, because it costs almost nothing:
**a short, regular LinkedIn presence from Andre**, reusing what is already in `knowledge/` — how
pre-trade compliance works, what the CMA/BDL pack covers, what a no-migration re-platform means.
It warms every outbound touch we send, and it is the same material we have already written.

## If and when inbound starts
Any inbound enquiry is a CRM record like any other — `crm.py add` with source `inbound`, scored
against the ICP, and with a next action **the same day**. Inbound leads decay in hours, not weeks,
and would jump the queue in `playbooks/daily-run.md` accordingly.
