/**
 * Guards the bug that shipped: the emitter and this app disagreed about a shape, and nothing said
 * so until the site was opened in a browser.
 *
 * `site_data.py` writes `site/public/data/`, `schemas.ts` declares what that data must look like,
 * and the two are maintained by hand on opposite sides of a language boundary. When a run record
 * gained a source that had never been read successfully, its history carried `count: null` — which
 * is the honest value, but the schema demanded a number.
 *
 * The failure mode is what makes this worth a test:
 *  - `python tools/build_site.py --check` **passed**, because validation is dev-only at runtime;
 *  - `tsc` **passed**, because Python's output is not typechecked;
 *  - the site built, deployed and rendered "The data layer could not be loaded".
 *
 * So the contract is now checked against the real emitted files, with no browser involved. Anything
 * `site_data.py` writes that `schemas.ts` refuses fails here instead.
 */
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { validate } from "./schemas";

const DATA = join(import.meta.dirname, "..", "..", "public", "data");

function read(path: string): unknown {
  return JSON.parse(readFileSync(join(DATA, path), "utf-8"));
}

const TOP_LEVEL = [
  "index.json",
  "rfps.json",
  "runs.json",
  "events.json",
  "sources.json",
  "candidates.json",
  "coverage.json",
  "stats.json",
  "questions.json",
  "build.json",
];

describe("the emitted data matches the contract this app declares", () => {
  for (const file of TOP_LEVEL) {
    it(`${file} validates`, () => {
      expect(() => validate(file, read(file))).not.toThrow();
    });
  }

  it("every company record validates", () => {
    // Not a sample: one malformed record breaks that firm's page and nothing else, which is
    // precisely the kind of failure that goes unnoticed until someone opens it.
    const dir = join(DATA, "companies");
    const files = readdirSync(dir).filter((f) => f.endsWith(".json"));
    expect(files.length).toBeGreaterThan(0);
    for (const f of files) {
      expect(() => validate(`companies/${f}`, read(join("companies", f)))).not.toThrow();
    }
  });

  it("checks every file the emitter writes, so a new one cannot be added untested", () => {
    // Without this, adding `coverage.json` to the emitter and forgetting it here would leave it
    // unvalidated — and the test suite would still be green.
    const written = readdirSync(DATA).filter((f) => f.endsWith(".json"));
    expect([...written].sort()).toEqual([...TOP_LEVEL].sort());
  });
});
