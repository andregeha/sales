# Lead sourcing

> Where new names come from. Depth over breadth: **one market × segment per day**, worked properly,
> beats skimming all twelve — the registers do not change fast enough to justify re-scanning daily.

## The sources, in order of value
1. **Regulator registers** — the single best source. Public, authoritative, complete, and they tell
   you the licence type, which tells you the segment. URLs in `knowledge/market/landscape.md`.
   UAE (SCA, DFSA/DIFC, FSRA/ADGM) · Saudi Arabia (CMA, SAMA) · Lebanon (CMA, Banque du Liban) ·
   France (AMF, ACPR — GECO and REGAFI).
2. **New-licence announcements** — the same registers, but *what changed*. A firm that just got
   licensed needs systems now and has no incumbent. The highest-value lead there is.
3. **Fund launches and new mandates** — a new fund means NAV, subscriptions/redemptions, a
   shareholder registry and fee calculation. That is our fund-administration module, precisely.
4. **Senior hires** — a new COO, CIO, Head of Operations or Head of Compliance is hired to change
   something, and usually has 12 months to show it. They are the easiest senior person to reach and
   the most likely to replace a system.
5. **Published tenders** — see `playbooks/rfp-radar.md`. Also a map of who has a buying centre.
6. **Industry press and associations** — launches, spin-outs, acquisitions, expansions.
7. **Events and conferences** — attendee and speaker lists are effectively a qualified list.
8. **Existing-client adjacency** — who do our clients' people know, and where have they moved to?
   ⚠ Using a client's name in any way needs **Andre's explicit approval**.

## Family offices — the hard case
Family offices are largely **unregulated and therefore invisible in registers**, yet they are one of
our best-fitting segments. They surface through: DIFC and ADGM foundation and holding structures,
multi-family offices (which *are* often regulated and *are* in the registers), industry associations
and networks, private-wealth events, press coverage of family businesses that have professionalised,
and single-family offices hiring their first CIO or Head of Investments.
Expect this to be slower and more manual than the other segments. That is fine — the fit is strong
enough to justify the effort, and the competition is thinner.

## Working a name
1. **Check for duplicates first** — `crm.py list` and search the slug. Re-finding the same firm is
   the most common waste in this loop.
2. **Add the record** with the source and the date we found it. Provenance matters; in six months
   nobody will remember where a name came from.
3. **Score it** against `knowledge/market/icp.md` — and **write the reasoning**. The number is for
   sorting; the reasoning is what a human actually reads.
4. **Enrich** with `ofs-researcher`: what they do, size signals, systems, people, language.
5. **Find the route in** — a named person and a real contact route. No route means no outreach,
   however good the fit.
6. **Look for the trigger.** No trigger → `nurture` with a note on what to watch for. That is a
   perfectly good outcome; a forced cold email is not.

## Standards
- **Never invent a company, a person, an email or a phone number.** Unknown is `null`.
  A guessed email pattern is not research; it is a bounce and a burned contact.
- **Every record carries its source and the date.**
- **Disqualify out loud**, with the reason — so we do not spend the same hour again next quarter.
- **Quality over volume.** Ten researched, well-scored, genuinely-triggered leads are worth more
  than two hundred names scraped from a directory, and they are what actually convert.
