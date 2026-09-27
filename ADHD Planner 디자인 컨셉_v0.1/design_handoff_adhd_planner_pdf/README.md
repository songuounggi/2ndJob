# Handoff: ADHD Planner, digital PDF for Etsy (GoodNotes / Notability)

## Overview
This is a set of undated digital planner PDFs sold on Etsy and used in note-taking apps (GoodNotes, Notability) on iPad. The look is called **"Lifted Paper"**. Each page shows a warm-white sheet lying on a light grey desk, with one or two corners lifted slightly as if by a breeze. The ink follows the Broadsheet style: editorial serif type, hairline rules and very sparing spot color.

**Your job:** produce print-ready PDFs from the HTML design reference. Keep them as small as possible, with working internal links.

**Hard constraints**
- **File size:** Etsy caps each file at **20 MB**, and a listing can have up to 5 files. Target **≤ 5 MB per PDF**, and ideally 2 to 4 MB.
- **Links:** the right-edge index tabs must be **clickable internal links** in the PDF, because GoodNotes follows them.
- **Vector content:** text, rules, boxes and tables must stay **vector**. Only the sheet background may be a raster image.

## About the design files
`design/Admin Tables v17.dc.html` is a **design reference built in HTML**. It's one big canvas showing every page side by side, with explanations and option labels. **Don't print this canvas as-is.** Recreate each page as its own fixed-size page (see *Recommended pipeline*) and copy layouts, sizes and copy from the reference.

To view the reference, open it in Chromium from inside `design/` (it loads `support.js` and `_ds/.../styles.css` relatively). Every page is a `768 × 1024` box. Its ink content is inline-styled HTML inside `position:absolute; inset:38px`. The captions under each page ("Sheet A · Daily", "7b", etc.) are annotations only and must **not** go into the PDF.

The file contains **two canvases**:
1. **Top section, tables 7a to 7f:** alternative designs for the Admin Edition "Bills & due dates" page, plus a generic blank table (7f).
2. **Bottom section, editions 6a to 6d:** the full page sets for four editions, plus Digital directions.

**Some of this is options, not final pages.** The owner will pick. Unless told otherwise:
- **Bills page:** use **7b** in the Admin Edition PDF, and add **7f** as a generic "Table" page. 7a, 7c, 7d and 7e are alternatives, so build them only if asked.
- **Digital directions (3a/3b/3c):** these are three *style directions* for the Focus Edition, each a cover plus a daily page. Build them as a **separate "Directions sampler" PDF**, not inside the Focus Edition. The owner will decide what to keep.

## Fidelity
**High fidelity.** Colors, type sizes, spacing, rules and copy are final. Match the reference pixel for pixel at 768 × 1024.

## Page geometry (every page)
| | Value |
|---|---|
| PDF page | 768 × 1024 CSS px, which is 576 × 768 pt (8 × 10.667 in, iPad portrait 3:4) |
| Desk margin | 38 px on all four sides (5%). Part of the page, colored `#eae7e7` |
| Sheet (paper) | 692 × 948 px at x=38, y=38, color `#f8f4f4` |
| Content padding inside sheet | 40 top, 44 right, 30 bottom, 44 left (so the content box is 604 × 878) |
| Index tabs | stick out of the sheet's right edge into the desk margin (see *Tabs*) |

### Sheet types (the lifted-paper background)
There are only two backgrounds. They're pre-rendered in `backgrounds/`:

| Type | Lifted corners | Used for | File |
|---|---|---|---|
| **Sheet A** | bottom-right (100%) + top-left (60%) | every working page | `backgrounds/sheet-a-2x.jpg` (PNG master alongside) |
| **Sheet B** | bottom-right (100%) + bottom-left (60%) | **covers and section dividers only** (used rarely, on purpose) | `backgrounds/sheet-b-2x.jpg` |

The images are 1536 × 2048 (2×) and full-bleed. They include the desk, the four-edge float shadow, the corner desk shadows and the corner highlights. Place one image per page at `0,0,768,1024`, then lay the ink on top.
> **This is the key size optimisation.** In the HTML reference these effects are live CSS (`box-shadow`, `filter: blur(24px)`, radial gradients). Chromium would rasterize them *separately on every page*, which is what makes files huge. Never recreate those effects in the PDF build. Use the two images. Each is about 40 KB as JPEG q90.

## Ink rules (apply to every page)
- **One family:** Source Serif 4. Use 600 for headings and numerals, 400 for body, and 400 italic for helper copy. Don't use any sans serif.
- **Small-caps labels:** 10 to 11 px, `letter-spacing: .1em`, uppercase, neutral-700.
- **Writing lines:** 1 px, neutral-400 (neutral-300 when faint). Row pitch is usually 34 px, or 44 px for the lead item.
- **Tick boxes and circles:** transparent fill with a 1 px neutral-600 outline (reference uses `box-shadow: inset 0 0 0 1px`; a 1 px border is fine and safer for vectors). Radius is 1 px for boxes.
- **Cyan (`#0088b0`) marks only the lead item on a page.** That means item "1", the lead block's label, its writing lines (cyan at 40%) and "due this week" rows (cyan 6% tint). Everything else stays neutral.
- **The magenta off-register plate** is `text-shadow: 2.5px 2px 0 rgba(214,0,108,.45)`. Use it **at most once or twice per page**, on the page's hero word or numeral. Keep it as vector text: a text-shadow with no blur prints as a second copy of the text.
- **`.cmyk-num`** (Focus Edition cover "3", Press Proof numerals): the numeral printed as paper, cyan, magenta and yellow plate copies with small offsets. The CSS is in `design/_ds/.../styles.css` (`.cmyk-num`, `.plate-c/-m/-y`). Recreate it with 3 or 4 stacked text copies, offset as in that CSS, with `mix-blend-mode: multiply`. Don't rasterize it.
- **Tables:** the reference shows a full table system: a thick-thin top rule, a 1 px ink rule under the header, hairline rows and a double rule above totals. It uses no vertical rules except in 7d, 7e and 7f.
- **Footer on each working page:** 10 px small caps, neutral-700, edition name on the left and page name plus number on the right, pinned to the bottom of the content box.

## Tabs (PDF internal links)
Every page has a vertical tab rail attached to the sheet's right edge. Each tab is `<a href="#page-id">`.
- **Geometry:** the rail starts at y = 38 + 64 px, and tabs are 6 px apart. Each tab is 26 px wide (30 px when active), 70 px tall (84 px if the label is longer than 6 characters), and overlaps the sheet by 4 px. Corners are rounded 0 2 2 0 px, with a shadow of `0 1px 2px rgba(45,43,43,.08), 0 3px 8px rgba(45,43,43,.07)`. The shadow is small and may rasterize, which is acceptable.
- **Label:** vertical text (`writing-mode: vertical-rl`), 10 px, uppercase, `letter-spacing .12em`.
- **Colors:** the active tab is cyan with `#f3f2f2` text. Inactive tabs are paper-colored with neutral-800 text.
- **Tab sets (the destination is that edition's page with the matching key):**
  - **Focus:** Home, Guide, Dump, Day, Week, Month, Track, Habits, Menu
  - **Evening:** Home, Shutdown, Sleep, Wind-down, Notes
  - **Admin:** Home, Bills, Subs, Projects (+ Tables if 7f is included)
  - **Directions sampler:** Home, Dump, Day, Week, Month, Habits, Meds, Menu
- If a tab has no page yet (Evening "Wind-down" and "Notes", and most Directions tabs), link it to the edition's Home page. Also list it in your summary.
- In the reference, each page wrapper has an `id="pg-<edition>-<key>"`. Reuse those ids as the link targets.

## Page inventory
Every entry is **ID · page · sheet type**. Copy and layout come straight from the reference.

### The Focus Edition (canvas section `#fe`), 9 pages
1. `pg-fe-home` · **Cover** · **B**: the title "The / Focus / Edition" at 88 px, with the plate on "Focus". The big `.cmyk-num` **"3"** (200 px) sits beside the italic line "Three things are plenty…". Below is the "In this edition" index and a "Belongs to" line.
2. `pg-fe-guide` · How to use · A: five numbered rules, with rule 1 in cyan and carrying the plate.
3. `pg-fe-dump` · Brain dump · A: two ruled columns and the T/W/S/X sort key (T in cyan).
4. `pg-fe-day` · Daily · A: title Today, week circles, date, energy dots. Lead "1" (72 px, cyan + plate) with two 44 px lines and "Tiniest first step". Then items 2 and 3, Hours (7am–8pm) next to Don't forget and Stray thoughts (dot grid), and the meds/water/one-good-thing row.
5. `pg-fe-week` · Weekly · A: the intention line (cyan), 7 days plus "Next week, maybe", 4 lines each.
6. `pg-fe-month` · Monthly · A: a 7 × 6 hairline calendar, plus "This month's focus" (cyan) and "Dates to remember".
7. `pg-fe-track` · Section divider "Trackers" · **B**: "Trackers" at 128 px with the plate.
8. `pg-fe-habits` · Habit tracker · A: a 31-day grid with **filled cells** (neutral-200 on weekdays, neutral-300 on weekends). Row 1 is tinted cyan.
9. `pg-fe-menu` · Dopamine menu · A: four blocks (Starters, Mains, Sides, Desserts), with the plate on "menu".

### The Admin Edition (section `#ae` + tables 7a–7f)
1. `pg-ae-home` · Cover · **B** (plate on "Admin").
2. `pg-ae-bills` · Bills & due dates · A: **use layout 7b** (chunked by week) from the top canvas, with the Bills tab active.
3. `pg-ae-subs` · Subscriptions & appointments · A: two tables.
4. `pg-ae-projects` · Projects in motion · A.
5. `pg-ae-tables` · Table · A: **use 7f**, a plain 5-column, 16-row grid with a write-in header.

### The Evening Edition (section `#ee`), 3 pages
1. Cover · **B** (plate on "Evening"). 2. The shutdown · A. 3. Sleep & mood · A.

### Directions sampler (section `#dd`), 6 pages, separate PDF
- 3a The Daily Focus (newspaper): Cover **B** + Front page **A**.
- 3b Press Proof (registration marks, halftone circles, color wedge): Cover **B** + Daily **A**. The halftone circles on the 3b cover are CSS radial-gradient patterns. Render them as a small raster with multiply blend, or as an SVG dot pattern. Keep that cost under 300 KB.
- 3c Big Type: Cover **B** + Daily **A**.

## Recommended pipeline
1. **One HTML file per edition.** Each page is a `<section class="page">` sized exactly `768px × 1024px`, with `break-after: page`, `position: relative` and `overflow: hidden`, containing:
   - `<img src="backgrounds/sheet-a-2x.jpg">` (or `-b`) at `inset:0; width:768px; height:1024px`. **Use the same file path on every page** so the image is embedded once.
   - the tab rail (`<nav>` with `<a href="#…">`)
   - the ink content box at `left:38px; top:38px; width:692px; height:948px; padding:40px 44px 30px`
2. **Print with Playwright/Chromium:** `page.pdf({ width: '768px', height: '1024px', printBackground: true, preferCSSPageSize: false, margin: 0 })`, with `@page { size: 768px 1024px; margin: 0 }`. Chromium keeps `href="#id"` anchors as internal PDF links and subsets the fonts automatically.
3. **Replace effects that would rasterize:**
   - Change `box-shadow: inset 0 0 0 1px` outlines to `border` or `outline`.
   - Change repeating/radial-gradient **dot grids and ruled lines** to SVG `<pattern>`s or real 1 px elements. Chromium can rasterize CSS gradients, which inflates size.
   - Don't use `filter`, `backdrop-filter` or blurred shadows anywhere in the ink layer.
4. **Post-process (optional):** `qpdf --object-streams=generate --recompress-flate in.pdf out.pdf`.
5. **Fonts:** load Source Serif 4 (400, 600, 400 italic) locally, from Google Fonts or a bundled copy, so the PDF never falls back to a system font. Wait for `document.fonts.ready` before printing.

## Checklist before shipping each PDF
- [ ] The file is ≤ 5 MB. `pdfimages -list` shows **exactly 2 unique background images** (or fewer), not one per page.
- [ ] `pdffonts` shows only Source Serif 4 subsets, and no fallback fonts.
- [ ] Every tab link jumps to the right page in Preview, Acrobat and GoodNotes.
- [ ] Sheet B appears only on covers and section dividers.
- [ ] Cyan appears only on each page's lead item, and the magenta plate appears at most twice per page.
- [ ] No captions, option badges ("7b", "Sheet A") or dashed "PDF edge" guides were printed.
- [ ] Text stays selectable/searchable, which proves it's vector.
- [ ] A spot check at 400% zoom shows crisp lines and type.

## Design tokens
See `tokens.css`. The key values:
- **Desk and paper:** desk `#eae7e7`, paper `#f8f4f4`.
- **Ink:** ink `#201e1d`, neutrals 300–900 `#d7d3d3 #bab6b6 #9b9797 #7d7979 #605d5d #444141 #2d2b2b`.
- **Spot colors:** cyan `#0088b0` (700 `#006786`, 800 `#004961`), magenta `#d6006c`, yellow `#edbb00`.
- **Radius:** 1 px and 2 px.

## Assets
- `backgrounds/sheet-a-2x.jpg`, `sheet-b-2x.jpg` (plus PNG masters): the lifted-paper backgrounds, generated from the same parameters as the HTML reference.
- There are no photos or icons. All ornament is type, rules and plates.
- Font: Source Serif 4 (OFL), from Google Fonts.

## Reference screenshots
`screenshots/` holds a 768 × 1024 PNG of every page (the captions are excluded). Use them to compare your PDF output against the design.
- Files are named `<edition>-<nn>-<page>.png`, `directions-<3a|3b|3c>-<cover|daily>.png` and `table-7a…7f-*.png`.
- `admin-02-bills-v16-original.png` is the **older** Bills layout. The Admin Edition should use `table-7b-chunked-by-week.png` instead.
- These were captured with a DOM-to-image renderer, so a few effects look rougher than in a real browser. **The cmyk-num “3” on the Focus cover and the Press Proof halftones in particular.** When a screenshot and the HTML/CSS disagree, follow the HTML/CSS.

## Files
- `screenshots/`: per-page reference images (see above).
- `design/Admin Tables v17.dc.html`: the full design reference (tables 7a–7f on top, all editions below).
- `design/support.js`, `design/_ds/broadsheet-…/styles.css`, `_ds_bundle.js`: the runtime and styles the reference needs in order to render.
- `tokens.css`: the tokens above.
- `backgrounds/`: Sheet A and Sheet B.
