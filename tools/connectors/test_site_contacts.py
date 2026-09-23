#!/usr/bin/env python
"""Tests for the website contact sweep. No network.

**What is actually at risk here.** This connector is the only one that writes a value we will later
*use to contact a real person*. A wrong count on a dashboard is embarrassing; a wrong email address
sends a message to a stranger, or bounces and burns the firm. So the tests are concentrated on the
extraction, where a wrong address would come from:

- debris in page source that looks like an address (`sentry.io`, `logo@2x.png`),
- a vendor's address mistaken for the firm's,
- a number that is not a phone number,
- and above all, that nothing is ever *constructed*.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import site_contacts as sc  # noqa: E402


# -- emails ------------------------------------------------------------------

def test_reads_an_address_printed_as_plain_text():
    """Plenty of firms print an address as text with no mailto link at all."""
    html = "<p>Pour nous joindre : contact@gestion-example.fr</p>"
    assert sc._clean_emails(html) == {"contact@gestion-example.fr"}


def test_reads_a_mailto_link():
    html = '<a href="mailto:Info@Firm.co.uk?subject=hi">write to us</a>'
    assert sc._clean_emails(html) == {"info@firm.co.uk"}


def test_drops_the_debris_that_looks_like_an_address():
    """Every one of these was observed in real page source, not invented for the test."""
    html = """
      <img src="logo@2x.png"><script>Sentry.init({dsn:'x@sentry.io'})</script>
      <span>noreply@firm.fr</span><span>someone@example.com</span>
      <span>a@b.wixpress.com</span><a href="mailto:real@firm.fr">us</a>
    """
    assert sc._clean_emails(html) == {"real@firm.fr"}


def test_script_and_style_contents_are_not_mined_for_text_addresses():
    html = "<style>.x{background:url(a@2x.png)}</style><script>var t='track@gstatic.com'</script>"
    assert sc._clean_emails(html) == set()


def test_nothing_is_constructed_from_a_domain():
    """The whole contract in one assertion: a page with no address yields no address.

    ⚠ If this ever fails, the connector has started guessing `info@<domain>` — stop and revert.
    """
    html = "<html><body><h1>Gestion Example</h1><p>Paris</p></body></html>"
    assert sc._clean_emails(html) == set()


# -- ranking -----------------------------------------------------------------

def test_role_address_is_preferred_over_a_persons():
    role, personal = sc._rank_emails(
        {"j.dupont@firm.fr", "contact@firm.fr"}, "firm.fr")
    assert role == ["contact@firm.fr"]
    assert personal == ["j.dupont@firm.fr"]


def test_an_address_on_the_firms_own_domain_outranks_an_agency_one():
    """A PR agency's address is a real route, but it is not the firm."""
    role, _ = sc._rank_emails({"contact@agency.com", "contact@firm.fr"}, "firm.fr")
    assert role[0] == "contact@firm.fr"


def test_a_subdomain_still_counts_as_the_firms_own():
    role, _ = sc._rank_emails({"contact@investors.firm.fr", "contact@other.com"}, "firm.fr")
    assert role[0] == "contact@investors.firm.fr"


# -- phones ------------------------------------------------------------------

def test_takes_only_international_format_numbers():
    """A bare local string is indistinguishable from a registration number or a price."""
    html = "<p>Tel +33 1 42 68 00 00 — SIREN 552 100 554 — 01 42 68 00 00</p>"
    assert sc._clean_phones(html) == {"+33142680000"}


def test_rejects_digit_strings_that_are_not_phone_numbers():
    html = "<p>+1234567 too short</p><p>+1234567890123456789 too long</p>"
    assert sc._clean_phones(html) == set()


# -- link following ----------------------------------------------------------

def test_follows_only_same_host_contact_pages():
    html = """
      <a href="/contact">Contact</a>
      <a href="/produits">Produits</a>
      <a href="https://linkedin.com/company/x/contact">LinkedIn</a>
      <a href="/notre-equipe">Notre équipe</a>
    """
    links = sc._links(html, "https://firm.fr/")
    assert links == ["https://firm.fr/contact", "https://firm.fr/notre-equipe"]


def test_recognises_a_contact_page_by_its_link_text_alone():
    """French sites routinely use an opaque path with a plain label."""
    links = sc._links('<a href="/p/17">Nous contacter</a>', "https://firm.fr/")
    assert links == ["https://firm.fr/p/17"]


def test_a_fragment_is_not_a_separate_page():
    html = '<a href="/contact#form">Contact</a><a href="/contact">Contact</a>'
    assert sc._links(html, "https://firm.fr/") == ["https://firm.fr/contact"]


# -- robots ------------------------------------------------------------------

def test_a_disallowing_site_is_declined_and_never_fetched(monkeypatch):
    """A refusal is a decision we honour, not a failure to report."""
    monkeypatch.setattr(sc, "_robots_allows", lambda base: (False, "robots.txt disallows"))

    def explode(url):  # pragma: no cover - the point is that it is never called
        raise AssertionError("fetched a site that refused us in robots.txt")

    monkeypatch.setattr(sc, "_get", explode)
    out = sc.read_site("https://firm.fr")
    assert out["declined"] is True
    assert out["ok"] is False
    assert out["emails"] == {}


# -- writing to the CRM ------------------------------------------------------

def test_an_unreachable_site_is_reported_by_name_not_counted_as_no_website(monkeypatch):
    """"We could not read it" and "it publishes nothing" are different facts."""
    monkeypatch.setattr(sc, "_robots_allows", lambda base: (True, "no robots.txt"))

    def boom(url):
        raise sc.SiteError("HTTP 403")

    monkeypatch.setattr(sc, "_get", boom)
    out = sc.read_site("https://firm.fr")
    assert out["ok"] is False and out["declined"] is False
    assert out["reason"] == "HTTP 403"


def test_every_address_carries_the_url_it_was_read_from(monkeypatch):
    monkeypatch.setattr(sc, "_robots_allows", lambda base: (True, "no robots.txt"))
    monkeypatch.setattr(sc, "_get",
                        lambda url: (url, '<a href="mailto:contact@firm.fr">x</a>'))
    monkeypatch.setattr(sc.time, "sleep", lambda *_: None)
    out = sc.read_site("https://firm.fr")
    assert out["emails"]["contact@firm.fr"] == "https://firm.fr"


# -- the wrong door ----------------------------------------------------------

def test_a_data_protection_officer_is_never_a_contact_route():
    """`dpo@` and `rgpd@` are real, published, and exactly the wrong people to sell to.

    Observed on real French asset-manager sites. Emailing a privacy officer to pitch software is a
    reliable way to generate a complaint instead of a meeting.
    """
    role, personal = sc._rank_emails(
        {"dpo@firm.fr", "rgpd@firm.fr", "contact@firm.fr"}, "firm.fr")
    assert role == ["contact@firm.fr"]
    assert personal == []


def test_recruitment_and_press_inboxes_are_never_a_contact_route():
    role, personal = sc._rank_emails(
        {"careers@firm.fr", "jobs@firm.fr", "press@firm.fr", "infos@firm.fr"}, "firm.fr")
    assert role == ["infos@firm.fr"]
    assert personal == []


def test_a_firm_that_publishes_only_wrong_doors_yields_no_route():
    """Better to hold nothing than to hold an address that should not be written to."""
    assert sc._rank_emails({"dpo@firm.fr", "careers@firm.fr"}, "firm.fr") == ([], [])


def test_plural_and_french_role_forms_are_recognised():
    """`infos@` was being filed as a person's address for want of one letter."""
    for local in ("infos", "contacts", "serviceclients", "accueil"):
        role, _ = sc._rank_emails({f"{local}@firm.fr"}, "firm.fr")
        assert role == [f"{local}@firm.fr"], local


# -- phone country codes -----------------------------------------------------

def test_a_phone_from_the_wrong_country_is_discarded():
    """Measured: a French asset manager's page yielded a Seattle number (+1 206).

    Almost certainly a vendor widget in the markup. A wrong phone number is worse than none.
    """
    html = "<p>+1 206 266 1000</p><p>+33 1 44 55 02 10</p>"
    assert sc._clean_phones(html, "France") == {"+33144550210"}


def test_overseas_french_numbers_still_count_as_France():
    assert sc._clean_phones("<p>+262 262 90 00 00</p>", "France") == {"+262262900000"}


def test_gulf_market_codes():
    assert sc._clean_phones("<p>+971 4 362 1000</p>", "UAE") == {"+97143621000"}
    assert sc._clean_phones("<p>+966 11 279 1111</p>", "Saudi Arabia") == {"+966112791111"}


def test_an_unknown_market_keeps_the_number_rather_than_inventing_a_rule():
    assert sc._clean_phones("<p>+41 22 707 0000</p>", None) == {"+41227070000"}


def test_the_national_trunk_prefix_is_stripped():
    """"+33 (0)1 56 88 33 00" must not become "+330156883300" — one digit too many, and undiallable.

    Every French site in the first live batch printed the number this way, so this was not an edge
    case: it was the common case.
    """
    assert sc._clean_phones("<p>+33 (0)1 56 88 33 00</p>", "France") == {"+33156883300"}
    assert sc._clean_phones("<p>+971 (0)4 362 1000</p>", "UAE") == {"+97143621000"}


def test_a_number_without_a_trunk_prefix_is_left_alone():
    assert sc._clean_phones("<p>+33 1 44 55 02 10</p>", "France") == {"+33144550210"}
