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
- Google Business Profile changes were subsequently explicitly approved: replace the four website links with their branch URLs and correct Tuesday closures. Do not change profile names, categories, phone numbers, reviews or other fields.

## Tasks

- [x] Add `tools/build_local_seo.py`: parse existing branch records, add homepage metadata and real branch links, generate `our-branches.html`, four `branches/*.html`, `robots.txt`, `sitemap.xml`. Include canonical URLs and matching Organization/LocalBusiness data, and reserve icon dimensions.
- [x] Replace the unused Temple PNG preload with the current hero WebP; add favicon and font preconnects. Keep existing hero image and layout.
- [x] Add explicit generated public files to local `.vercelignore`; keep all deny rules intact.
- [x] Check generated pages with JavaScript disabled, unique titles/canonicals, sitemap URLs, matching displayed and structured contact details, keyboard focus, mobile overflow and real navigation.
- [x] Serve on localhost with existing `serve.mjs`; use `screenshot.mjs` for at least two comparison rounds and inspect PNGs.
- [x] Request a fresh code review, fix material findings, publish against current production source and confirm live responses, links, verification files and deployment status.
- [x] Verify Search Console ownership for the explicitly approved account and submit `/sitemap.xml`. Google reports Success and six discovered pages.
- [x] Inspect the four existing verified Google Business Profiles. Save each matching branch website URL. Correct Kothapet and Warangal Tuesday closures; Somajiguda and Karimnagar already have correct hours.

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
- Owner approved the fuller managed Google addresses and PIN codes after comparing them with the original site. Updated source branch records, generated page copy, postal codes and homepage head-office address together. No coordinates, ratings or reviews were added to schema.
- Fresh review found no material regressions. A minor extra-blank-line issue was fixed; repeated generation is now byte-identical.
- Browser checker initially attempted the hidden desktop navigation at a mobile width and later clicked during the splash/menu animations. Corrected the checker to use the visible viewport and await the UI states; actual desktop, mobile and legacy contact navigation pass.
- Local and live browser checks: all six pages, JavaScript disabled, 375/768/1280 px, descriptions, titles, canonicals, matching visible/schema contact data, Tuesday closure and sitemap. Live navigation checks pass. Existing Vitest configuration contains no test files; browser checks provide the relevant integration verification.
- The approved owner account uses `google1a736d462f272294.html`; it was downloaded from Search Console and added alongside the original `googlee1584360cfe843d2.html`. Both are permanent and explicitly included in deployment rules.
- Google Business Profiles: all four were already verified; no new duplicate profiles created. Google descriptions already identify Reddy-community matchmaking and branch numbers. Existing primary and secondary phone numbers were retained.
- Existing homepage links `/support`, `/privacy-policy`, `/terms`, `/account-deletion` still return 404. Local drafts contain unfinished text; they were deliberately not published or rewritten as part of this approved search update. New branch pages link to working contact pages.
- Screenshots and Search Console/Business Profile proof are saved in `temporary screenshots/` locally. Search Console shows sitemap Success with six discovered pages; discovery is not a claim of indexing or ranking.
