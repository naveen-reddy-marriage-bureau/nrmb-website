"""Generate public branch pages from the existing site's branch records.

Run manually after editing public branch details; Vercel serves the resulting
HTML directly. No credentials, network calls, or runtime build step are needed.
"""

import argparse
import html
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape as xml_escape

ORIGIN = "https://www.reddyelitematrimony.com"
NAME = "Naveen Reddy Marriage Bureau"
ORG_ID = ORIGIN + "/#organization"
KEYS = {"hyd": "somajiguda", "ktp": "kothapet", "wgl": "warangal", "krm": "karimnagar"}
LOCALITIES = {
    "hyd": ("Somajiguda, Hyderabad", "Hyderabad"),
    "ktp": ("Kothapet, Hyderabad", "Hyderabad"),
    "wgl": ("Warangal / Hanamkonda", "Hanamkonda"),
    "krm": ("Karimnagar", "Karimnagar"),
}
DETAILS = {
    "hyd": "Visit our corporate head office in Somajiguda, opposite Yashoda Hospital. Speak with the bureau team about Reddy matchmaking and the membership options available to your family.",
    "ktp": "Our Kothapet branch serves Reddy families in Hyderabad. Find us at Flat No. 501 on the fifth floor in Kothapet and call the branch before arranging your visit.",
    "wgl": "Meet our team in Phase 1, Teachers Colony, Hanamkonda for Reddy matrimony services in the Warangal area. Use our linked Google Maps listing and the location code XGRP+HVR for directions.",
    "krm": "Visit our Karimnagar office in Gajarla Complex, opposite Bank of India at Kaman Chowrasta. Contact the branch team to discuss assisted matchmaking for your family and arrange a convenient visit.",
}
DAYS = ["Monday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DESCRIPTION = "Reddy matrimony and personal matchmaking since 2000. Visit Naveen Reddy Marriage Bureau in Somajiguda, Kothapet, Warangal or Karimnagar."


def e(value):
    return html.escape(str(value), quote=True)


def phone(value):
    return "+" + re.sub(r"\D", "", value)


def load_branches(source):
    match = re.search(r"const BRANCHES\s*=\s*\{(.*?)\n\};", source, re.S)
    if not match:
        raise ValueError("Expected public BRANCHES records are missing")
    records = {}
    for key, slug in KEYS.items():
        record = re.search(r"\b" + key + r":\s*\{(.*?)\n\s*\}", match[1], re.S)
        if not record:
            raise ValueError(f"Branch {key} missing")
        fields = dict(re.findall(r"(\w+):'([^']*)'", record[1]))
        for field in ["city", "address", "phone", "mobile", "email", "maps", "hours", "landmark", "type"]:
            if not fields.get(field):
                raise ValueError(f"Branch {key}: required field {field} missing")
        # Fail rather than silently publishing stale structured opening times.
        if fields["hours"] != "Mon–Sun: 10:00 AM – 6:30 PM (Tuesday: Weekly Off)":
            raise ValueError("Opening hours changed; update visible hours and schema together")
        fields.update(key=key, slug=slug, path=f"/branches/{slug}")
        records[key] = fields
    return records


def organization(branches):
    head = branches["hyd"]
    return {
        "@type": "Organization", "@id": ORG_ID, "name": NAME,
        "url": ORIGIN + "/", "logo": ORIGIN + "/Assets/Logo-transparent.webp",
        "foundingDate": "2000", "telephone": phone(head["phone"]),
        "email": head["email"],
        "sameAs": ["https://www.instagram.com/naveenreddymarriagebureau/"],
        "location": [{"@id": ORIGIN + b["path"] + "#business"} for b in branches.values()],
    }


def business(b):
    area, locality = LOCALITIES[b["key"]]
    postcode = re.search(r"\b(\d{3})\s?(\d{3})\b", b["address"])
    address = {
        "@type": "PostalAddress", "streetAddress": b["address"],
        "addressLocality": locality, "addressRegion": "Telangana", "addressCountry": "IN",
    }
    if postcode:
        address["postalCode"] = postcode[1] + postcode[2]
    return {
        "@type": "LocalBusiness", "@id": ORIGIN + b["path"] + "#business",
        "name": NAME, "url": ORIGIN + b["path"],
        "description": f"Reddy matrimony and assisted matchmaking in {area}.",
        "image": ORIGIN + "/Assets/Logo-transparent.webp", "address": address,
        "telephone": phone(b["phone"]), "email": b["email"], "hasMap": b["maps"],
        "parentOrganization": {"@id": ORG_ID},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": DAYS, "opens": "10:00", "closes": "18:30"}],
    }


def metadata(title, description, path, graph):
    url = ORIGIN + path
    return f'''<!-- LOCAL SEO:BEGIN -->
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_IN">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{ORIGIN}/Assets/Logo-transparent.webp">
<meta property="og:image:alt" content="{NAME} logo">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/webp" href="/Assets/Logo-transparent.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<script type="application/ld+json">{json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>
<!-- LOCAL SEO:END -->'''


STYLE = """
:root{--primary:#7B1F2E;--hover:#9B2F40;--gold:#B8892A;--bg:#FFFBF5;--text:#3D1C0E;--muted:#7A4030;--border:#E8C98A}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:'EB Garamond',Georgia,serif;font-size:19px;line-height:1.7}
a{color:var(--primary);text-underline-offset:4px;transition:transform 180ms cubic-bezier(.22,1,.36,1),opacity 180ms}a:hover{color:var(--hover)}a:active{opacity:.75}a:focus-visible{outline:3px solid var(--primary);outline-offset:5px;border-radius:3px}
.skip{position:absolute;left:1rem;top:-5rem;background:#fff;padding:.6rem;z-index:10}.skip:focus{top:1rem}
.site-header{background:#fff;border-bottom:1px solid #F5E4CC;padding:1rem max(1.25rem,calc((100vw - 1120px)/2));display:flex;align-items:center;justify-content:space-between;gap:1.2rem;flex-wrap:wrap;box-shadow:0 2px 16px rgba(123,31,46,.04)}
.brand{display:flex;align-items:center;gap:.75rem;text-decoration:none;color:var(--primary);font-family:'Cormorant Garamond',Georgia,serif;font-weight:600;font-size:1.4rem;line-height:1.2}.brand img{width:48px;height:48px;object-fit:contain;flex-shrink:0}.brand small{display:block;font-family:'Josefin Sans',Arial,sans-serif;font-size:.7rem;font-weight:400;letter-spacing:.04em;margin-top:.4rem}
nav{display:flex;gap:1.25rem;flex-wrap:wrap}nav a{min-height:44px;display:inline-flex;align-items:center;font-size:1rem}
main{max-width:1120px;margin:auto;padding:1.5rem 1.25rem 4rem}.breadcrumb{font-size:1rem;color:var(--muted);margin-bottom:2rem;display:flex;align-items:center;gap:.5rem;flex-wrap:wrap}
.intro{max-width:790px;margin:0 0 2.25rem}h1,h2,h3{font-family:'Cormorant Garamond',Georgia,serif;font-weight:600;color:var(--primary);line-height:1.15}h1{font-size:clamp(2.35rem,5vw,3.6rem);letter-spacing:-.03em;margin:0 0 1rem}h2{font-size:2rem;margin:0 0 1rem}h3{font-size:1.75rem;margin:0 0 .5rem}p{margin:.5rem 0 1rem}
.eyebrow{font-family:'Josefin Sans',Arial,sans-serif;font-size:.82rem;color:var(--muted);margin:0 0 1rem}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1.4rem}.card,.panel{background:#fff;border:1px solid #F0DFC1;border-radius:20px;padding:1.8rem;box-shadow:0 4px 24px rgba(123,31,46,.045),0 1px 3px rgba(184,137,42,.08)}
.card address,.panel address{font-style:normal}.detail-layout{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(0,1fr);gap:1.5rem;align-items:start}.aside{background:#FDF3E0;border-color:var(--border)}.label{display:block;font-family:'Josefin Sans',Arial,sans-serif;font-size:.82rem;color:var(--muted);margin-top:1rem}.actions{display:flex;flex-wrap:wrap;gap:.7rem;margin-top:1.3rem}.button{display:inline-flex;justify-content:center;align-items:center;min-height:46px;padding:.65rem 1.2rem;border-radius:30px;background:var(--primary);border:1px solid var(--primary);color:#fff;text-decoration:none;font-family:'Josefin Sans',Arial,sans-serif;font-size:.85rem;box-shadow:0 3px 12px rgba(123,31,46,.12)}.button:hover{background:var(--hover);color:#fff;transform:translateY(-1px)}.button:active{transform:translateY(1px)}.button.secondary{background:transparent;color:var(--primary);box-shadow:none}.button.secondary:hover{background:#FFF0F2}
.network{margin-top:2rem;border-top:1px solid var(--border);padding-top:2rem;max-width:790px}.branch-links{display:flex;flex-wrap:wrap;gap:.4rem 1.3rem}.branch-links a{min-height:44px;display:inline-flex;align-items:center}.site-footer{background:#fff;border-top:1px solid #F5E4CC;padding:2rem max(1.25rem,calc((100vw - 1120px)/2));font-size:1rem}.site-footer p{max-width:750px}.footer-links{display:flex;gap:1.25rem;flex-wrap:wrap}.footer-links a{min-height:44px;display:inline-flex;align-items:center}.panel a:not(.button),.site-footer p a{display:inline-block;min-height:44px;padding:.3rem 0}address,p,a{overflow-wrap:anywhere}
@media(max-width:740px){.grid,.detail-layout{grid-template-columns:1fr}.site-header{gap:.7rem}.brand{font-size:1.2rem}.brand small{font-size:.65rem}nav{gap:1.2rem}.card,.panel{padding:1.4rem}.breadcrumb{margin-bottom:1.5rem}main{padding-top:1.1rem}.intro{margin-bottom:1.7rem}}
@media(prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
"""


def branch_links(branches, current=None):
    return '<div class="branch-links">' + "".join(
        f'<a href="{b["path"]}"' + (' aria-current="page"' if current == b["key"] else '') + f'>{e(b["city"])}</a>'
        for b in branches.values()
    ) + '</div>'


def shell(title, description, path, content, graph, branches):
    return f'''<!DOCTYPE html>
<html lang="en-IN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
{metadata(title, description, path, graph)}
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&amp;family=EB+Garamond:wght@400;500;600&amp;family=Josefin+Sans:wght@400;500;600&amp;display=swap" rel="stylesheet">
<style>{STYLE}</style></head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><a class="brand" href="/"><img src="/Assets/Logo-transparent.webp" width="48" height="48" alt=""><span>{NAME}<small>Reddy community matchmaking since 2000</small></span></a><nav aria-label="Main navigation"><a href="/">Home</a><a href="/our-branches">Our branches</a><a href="/#pgContact">Contact</a></nav></header>
<main id="main">{content}</main>
<footer class="site-footer"><p><strong>{NAME}</strong><br>Personal matchmaking for the Reddy community since 2000.</p>{branch_links(branches)}<p>For general enquiries: <a href="tel:+919848221166">+91 98482 21166</a> · <a href="mailto:naveenreddy0033@yahoo.com">naveenreddy0033@yahoo.com</a></p><div class="footer-links"><a href="/#pgContact">Contact the bureau</a><a href="/our-branches">All branch offices</a></div></footer>
</body></html>
'''


def hours():
    return "10:00 AM – 6:30 PM, Monday and Wednesday–Sunday. Closed on Tuesdays."


def branch_page(b, branches):
    area = LOCALITIES[b["key"]][0]
    title = f"Reddy Matrimony in {area} | Naveen Reddy"
    description = f"Visit {NAME} in {area} for Reddy matchmaking. Find our address, branch phone, opening hours and Google Maps directions."
    content = f'''<nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/our-branches">Our branches</a><span aria-hidden="true">/</span><span aria-current="page">{e(b['city'])}</span></nav>
<section class="intro"><p class="eyebrow">{e(b['type'])} · {NAME}</p><h1>Reddy matrimony in {e(area)}</h1><p>{e(DETAILS[b['key']])}</p></section>
<div class="detail-layout"><section class="panel" aria-labelledby="visit"><h2 id="visit">Visit our {e(b['city'])} office</h2><span class="label">Address</span><address>{e(b['address'])}</address><span class="label">Landmark</span><p>{e(b['landmark'])}</p><span class="label">Branch phone</span><a href="tel:{phone(b['phone'])}">{e(b['phone'])}</a><span class="label">Bureau mobile</span><a href="tel:{phone(b['mobile'])}">{e(b['mobile'])}</a><span class="label">Email</span><a href="mailto:{e(b['email'])}">{e(b['email'])}</a><div class="actions"><a class="button" href="tel:{phone(b['phone'])}">Call the {e(b['city'])} branch</a><a class="button secondary" href="{e(b['maps'])}" target="_blank" rel="noopener noreferrer">Get directions<span class="sr-only" style="position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)"> (opens in a new tab)</span></a></div></section>
<aside class="panel aside" aria-labelledby="hours"><h2 id="hours">Plan your visit</h2><p>{hours()}</p><p>Please call before visiting to confirm availability and discuss your requirements.</p><p>All membership tiers and the shared branch network are available through our bureau team.</p><a href="/#pgMembership">Explore membership options</a></aside></div>
<section class="network"><h2>Personal matchmaking for Reddy families</h2><p>Our bureau assists Reddy families with personal matchmaking. Contact the {e(b['city'])} team to discuss registration, membership and your family's preferences.</p><p>Profiles registered at any of our four branches are accessible through every branch. You can visit the office closest to you, regardless of where you registered.</p><h3>Our branch network</h3>{branch_links(branches, b['key'])}</section>'''
    breadcrumbs = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": ORIGIN + "/"},
        {"@type": "ListItem", "position": 2, "name": "Our branches", "item": ORIGIN + "/our-branches"},
        {"@type": "ListItem", "position": 3, "name": b["city"], "item": ORIGIN + b["path"]},
    ]}
    return shell(title, description, b["path"], content, [organization(branches), business(b), breadcrumbs], branches)


def hub_page(branches):
    cards = []
    for b in branches.values():
        cards.append(f'''<article class="card"><p class="eyebrow">{e(b['type'])}</p><h2><a href="{b['path']}">{e(LOCALITIES[b['key']][0])}</a></h2><address>{e(b['address'])}</address><p>{hours()}</p><div class="actions"><a class="button" href="{b['path']}">View branch details</a><a class="button secondary" href="tel:{phone(b['phone'])}">Call {e(b['phone'])}</a></div></article>''')
    content = '''<nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span aria-current="page">Our branches</span></nav><section class="intro"><p class="eyebrow">Four offices, one connected bureau</p><h1>Reddy matrimony branches in Telangana</h1><p>Meet the Naveen Reddy Marriage Bureau team in Somajiguda, Kothapet, Warangal or Karimnagar. Choose the office closest to your family for personal Reddy matchmaking assistance.</p><p>Profiles registered at any branch are accessible through every branch. Please call before visiting.</p></section>'''
    content += '<div class="grid">' + ''.join(cards) + '</div>'
    graph = [organization(branches)] + [business(b) for b in branches.values()]
    return shell("Our Branches | " + NAME, DESCRIPTION, "/our-branches", content, graph, branches)


def update_home(source, branches):
    source = re.sub(r'<!-- LOCAL SEO:BEGIN -->.*?<!-- LOCAL SEO:END -->\s*', '', source, flags=re.S)
    title = "Reddy Matrimony in Telangana | " + NAME
    block = metadata(title, DESCRIPTION, "/", [organization(branches), {
        "@type": "WebSite", "@id": ORIGIN + "/#website", "url": ORIGIN + "/", "name": NAME,
        "publisher": {"@id": ORG_ID}, "inLanguage": "en-IN",
    }])
    source, count = re.subn(r'<title>.*?</title>', '<title>' + title + '</title>\n' + block, source, count=1, flags=re.S)
    if count != 1:
        raise ValueError("Homepage title missing")
    source = source.replace('href="Assets/Temple.png" as="image" fetchpriority="high"', 'href="Assets/Temple-hero.webp" as="image" fetchpriority="high"')
    source = source.replace('Where Sacred Traditions Meet Timeless Love', 'Reddy Matrimony, Rooted in Tradition')
    source = source.replace('alt="NRMB Logo"', 'alt="Naveen Reddy Marriage Bureau logo"')
    source = source.replace('alt="NRMB"', 'alt="Naveen Reddy Marriage Bureau"')
    # Only branch navigation changes. Legacy hash links remain supported.
    source = re.sub(r'<button\b([^>]*?)onclick="showPage\(\'pgBranches\'\)[^"]*"([^>]*)>(Our Branches|Our Branch Offices)</button>', r'<a\1href="/our-branches"\2>\3</a>', source)
    source = re.sub(r'<!-- BRANCH LINKS:BEGIN -->.*?<!-- BRANCH LINKS:END -->', '', source, flags=re.S)
    marker = '<!-- BRANCH LINKS:BEGIN --><div style="margin-top:1rem">' + branch_links(branches) + '</div><!-- BRANCH LINKS:END -->'
    source, count = re.subn(r'(<div class="fg-brand">.*?</p>)', r'\1' + marker, source, count=1, flags=re.S)
    if count != 1:
        raise ValueError("Expected homepage footer missing")
    source = re.sub(r'<!-- SEO LINKS STYLE:BEGIN -->.*?<!-- SEO LINKS STYLE:END -->\s*', '', source, flags=re.S)
    link_style = '''<!-- SEO LINKS STYLE:BEGIN --><style>
.nav-link,.mob-nav-link{text-decoration:none;display:inline-flex;align-items:center;justify-content:center}
.nav-link:focus-visible,.mob-nav-link:focus-visible,.branch-links a:focus-visible{outline:3px solid #7B1F2E;outline-offset:4px}
.nav-link:active,.mob-nav-link:active,.branch-links a:active{opacity:.75}
.feat-outer{opacity:1;transform:none}
.branch-links{display:flex;flex-wrap:wrap;gap:.4rem 1.3rem;margin-bottom:1.5rem}
.branch-links a{display:inline-flex;align-items:center;min-height:44px;font-size:1rem;color:#7B1F2E;text-underline-offset:4px}
.branch-links a:hover{color:#9B2F40}
</style><noscript><style>#splashScreen{display:none!important}</style></noscript><!-- SEO LINKS STYLE:END -->'''
    source = re.sub(r'<div class="sec-title">(.*?)</div>', r'<h2 class="sec-title">\1</h2>', source)
    source = re.sub(r'<div class="feat-title">(.*?)</div>', r'<h3 class="feat-title">\1</h3>', source)
    source = source.replace('</head>', link_style + '\n</head>', 1)
    return source


def generate(source_path, output):
    source = source_path.read_text(encoding="utf-8")
    branches = load_branches(source)
    output.mkdir(parents=True, exist_ok=True)
    files = {"index.html": update_home(source, branches), "our-branches.html": hub_page(branches)}
    for b in branches.values():
        files[f'branches/{b["slug"]}.html'] = branch_page(b, branches)
    paths = ["/", "/our-branches"] + [b["path"] for b in branches.values()]
    files["sitemap.xml"] = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{xml_escape(ORIGIN + path)}</loc></url>\n' for path in paths) + '</urlset>\n'
    files["robots.txt"] = "User-agent: *\nAllow: /\nDisallow: /Admin/\nDisallow: /next-app/\nDisallow: /scripts/\nDisallow: /tools/\nDisallow: /docs/\nDisallow: /Config/\nDisallow: /.tmp/\n\nSitemap: " + ORIGIN + "/sitemap.xml\n"
    for name, content in files.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
    print(f"Generated {len(files)} public files in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("index.html"))
    parser.add_argument("--output", type=Path, default=Path("."))
    args = parser.parse_args()
    generate(args.source, args.output)
