# The DFSA register we already read — and the 613 firms we were leaving on it

> Measured live 2026-09-23, before looking at any new source.

## The finding

We hold **319** DIFC records. The DFSA public register is searchable by **financial service**, and it
publishes **~50 service categories**. Our connector queries **four**.

Measured counts, live:

| DFSA financial service | Firms | Taken today | New to our CRM |
|---|---:|:---:|---:|
| Arranging Deals in Investments | 817 | ✗ | not sampled |
| Advising on Financial Products | 810 | ✗ | **273** (of first 420 read) |
| Arranging Custody | 397 | ✗ | not sampled |
| **Managing Assets** | 396 | ✅ | — |
| **Managing a Collective Investment Fund** | **213** | ✗ | **100** |
| **Operating a Representative Office** | **200** | ✗ | **195** |
| Dealing in Investments as Agent | 190 | ✗ | **123** |
| Dealing in Investments as Principal | 129 | ✗ | not sampled |
| Providing Custody | 54 | ✗ | **18** |
| **Single Family Office** | 41 | ✅ (all withdrawn) | — |
| **Accepting Deposits** | 38 | ✅ | — |
| **Providing Fund Administration** | 33 | ✅ | — |
| Providing Trust Services | 20 | ✗ | not sampled |
| Managing a Profit Sharing Investment Account | 7 | ✗ | not sampled |

**Five services alone yield 613 distinct firms not in the CRM** — and that is with *Advising* capped
at 420 of its 810, and without *Arranging Deals* (817) or *Arranging Custody* (397) sampled at all.

Counts overlap heavily (one firm holds many permissions), so the sum is meaningless and only the
measured union counts. The union of those five is 613.

## ⚠ Not all of it is worth having, and the headline number flatters

**Representative offices (195 new) are the trap.** The names are spectacular — T. Rowe Price, Baring
Asset Management, Partners Group, Blackstone, Allfunds, Euroclear, Aviva Investors, Russell
Investments, MFS, Tata AM, Landesbank Baden-Württemberg. But **a representative office cannot conduct
financial business**: it is a marketing and liaison presence. The platform decision for Blackstone or
T. Rowe Price is made in New York or London, by people who already run enterprise systems, and a
DIFC rep office has no authority over it.

So these are *not* 195 leads. A minority are genuinely interesting — regional firms using a rep
office as their Gulf presence (The Family Office Co. BSC, Silk Invest, Elara Capital, Sun Global
Investments) — and the rest are brand names that would flatter a pipeline report and convert at
approximately zero. Taking them wholesale would repeat the *Agent PSP* mistake in better clothing.

**The broad advisory categories are the other trap.** *Advising on Financial Products* (810) and
*Arranging Deals in Investments* (817) include insurance advisers, credit advisers and corporate
finance boutiques alongside genuine wealth managers. High volume, low precision.

## What is actually worth taking

| Service | New | Segment | Why |
|---|---:|---|---|
| **Managing a Collective Investment Fund** | **100** | `fund_manager` | The real DIFC fund managers. A core segment, and a clear gap: we currently map *Providing Fund Administration* to `fund_manager`, which is **wrong** — a fund administrator is a service provider, not a manager. |
| **Dealing in Investments as Agent / Principal** | 123 + ? | `broker` | Adjacent, already a segment we hold. |
| **Providing Custody** | 18 | `custodian` | Adjacent, already a segment we hold. |
| **Providing Trust Services** | ? (20 total) | family-office adjacent | Small, but trust providers sit next to family offices. |
| Representative offices | 195 | — | **Candidates, not records.** Needs a human to separate the regional firms from the global brands. |
| Advising / Arranging | 273+ | — | **Candidates, not records.** Precision too low to create from. |

## A mis-mapping to fix while we are here

`SERVICES` maps `"Providing Fund Administration" → fund_manager`. Fund administration is
third-party operational servicing — NAV, registrar, reporting — not fund management. The correct
`fund_manager` service is *Managing a Collective Investment Fund*, which we do not query at all.
33 records may carry the wrong segment because of this.

## Recommendation

Extend the DFSA connector before building anything new. It is the highest-yield work available: a
source that is already live, already trusted, already tested, and already polite — we were simply
asking it four questions out of fifty.

Precision-first: create records for the four high-precision services (~240 firms), send
representative offices and the broad advisory categories to the **candidate queue** where a human
decides. That grows DIFC coverage by roughly 75% in records and puts another ~470 in review,
without lowering the bar for what a record means.
