# Local search implementation plan

**Goal:** Make the confirmed four branches easier to discover in website search and connect each page to its existing Maps listing.

**Architecture:** Preserve the static HTML site and its existing design. Generate ordinary HTML branch pages using the public business details already in `index.html`; no runtime dependencies or build step on Vercel.

**Spec:** The user approved the existing name, four branches, current design, descriptions, sitemap, business data, linked branch pages and permanent verification file in chat on 2026-10-20.

## Constraints

- Public name: Naveen Reddy Marriage Bureau.
- Branches: Somajiguda, Kothapet, Warangal, Karimnagar.
- Use existing addresses, phone numbers, Maps links and hours; omit unknown PIN codes rather than guessing.
- Preserve local uncommitted design changes; publish SEO changes against the current production source only.
- Keep `googlee1584360cfe843d2.html` permanently.
- Do not change Google Business Profiles or claim their ownership/verification status.

## Tasks

- [ ] Add `tools/build_local_seo.py`: parse existing branch records, add homepage metadata and real branch links, generate `our-branches.html`, four `branches/*.html`, `robots.txt`, `sitemap.xml`. Include canonical URLs and matching Organization/LocalBusiness data, and reserve icon dimensions.
- [ ] Replace the unused Temple PNG preload with the current hero WebP; add favicon and font preconnects. Keep existing hero image and layout.
- [ ] Add explicit generated public files to local `.vercelignore`; keep all deny rules intact.
- [ ] Check generated pages with JavaScript disabled, unique titles/canonicals, sitemap URLs, matching displayed and structured contact details, keyboard focus, mobile overflow and real navigation.
- [ ] Serve on localhost with existing `serve.mjs`; use `screenshot.mjs` for at least two comparison rounds and inspect PNGs.
- [ ] Request a fresh code review, fix material findings, publish a single commit against current production source and confirm live responses, links, verification file and deployment status.

## Review focus

- Branch details remain readable without JavaScript.
- Nested pages use absolute asset paths and link correctly on Vercel clean URLs.
- Tuesday is consistently closed in visible content and structured data.
- Unknown postcodes, coordinates, reviews and ratings are never invented.
- Existing hash links and local uncommitted styling are preserved.

## Execution record

- Audit: homepage missing description/canonical/structured data; sitemap and robots return 404; main navigation uses buttons and hashes; favicon returns 404; redundant PNG preload downloads 659 KB.
- Existing mobile homepage: no horizontal overflow, no page script errors and no broken images at 390 px.
- Ruling: implement directly within the approved scope and use a fresh reviewer at the end; do not repeat approval requests for the already approved description.
- Ruling: prepare production files separately from the dirty local checkout so unrelated pending edits are not published.
- Environment: `python` is absent from PATH; use the bundled Python executable supplied by workspace dependencies.
