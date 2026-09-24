# GLEIF as a Saudi source — measured, and deliberately not used yet

> Measured live 2026-09-24, while the regulator and family-office investigations were running.

## What is there

| | |
|---|---:|
| Saudi legal entities in GLEIF | **6,045** |
| …categorised `FUND` | **16** |
| Active, financial-sounding names not in our CRM | **222** |

**The fund route is exhausted.** GLEIF's genuinely high-precision Saudi play — walking a fund's
`fund-manager` relationship to its managing entity — was already run: all 16 Saudi funds were swept,
and that is where SNB Capital, Jadwa Investment, Alinma and AlJazira Capital came from. There is
nothing left in it.

## What the remaining 222 actually look like

GLEIF carries **no industry classification at all**, so the only filter available is the firm's own
name. Scanning 6,000 Saudi entities for financial words yields 222 active names we do not hold —
and the sample is the problem:

> Mourina Co for Investment and Development · Metal Crest Investment Company · Oak eagle
> International Investment Company · Aviation Services Company · Fund Me Finance · Abdulqader Nasser
> AlObaikan & Partners Holding Company

208 of the 222 are GLEIF category `GENERAL` — an ordinary legal entity, nothing more. "X for
Investment and Development" is a standard Saudi holding-company name, and an aviation services
company is not an asset manager whatever its LEI says.

⚠ **This is the French NAF `64.20Z` problem in Arabic.** A name is not a business model, and we have
already established what happens when a broad self-descriptive filter is treated as a source: the
CRM fills with entities whose only qualification is a word.

## Why it is not being used yet, which is a decision and not an oversight

1. **The precision is wrong for the moment.** The regulator investigations now running are looking
   for the CMA's other 206 authorised persons and SAMA's licensed banks — populations that are
   *definitionally* in our segments. 222 maybes are worth less than 242 certainties, and doing the
   noisy one first would be doing the easy thing rather than the useful one.
2. **The queue is already the constraint.** 731 candidates sit unreviewed. Adding 222 weak ones
   makes the queue worse, not the CRM better — review capacity is what is scarce, not names.
3. **It stays available.** If the regulator routes come back blocked, this is a real fallback: it
   would enter as candidates carrying an explicit weak signal, never as records.

**Revisit when:** the CMA and SAMA routes are resolved, and the existing candidate queue is worked
down far enough that 222 more would be reviewed rather than buried.
