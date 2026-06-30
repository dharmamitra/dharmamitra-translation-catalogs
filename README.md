# Dharmamitra Translation Catalogs

Catalogs of **Japanese** and **English** translations of classical Indian Buddhist works
(originals in Sanskrit / Pāli / Prakrit, including works surviving only in Tibetan or
Chinese), mined with Gemini from two large scholarship corpora, plus an interactive
category-stratified visualization for each.

## Contents

```
catalogs/
  japanese.tsv / .json   619 works  (332 with a full translation, 271 partial-only)
  english.tsv  / .json   280 works  (205 with a full translation,  74 partial-only)
viz/
  japanese.html          one interactive plot of ALL Japanese translations
  english.html           one interactive plot of ALL English translations
```

Open the `viz/*.html` files in a browser (Plotly is loaded from CDN).

## Catalog columns

| column | meaning |
|---|---|
| `work` | canonical romanized Sanskrit/Pāli title of the original |
| `category` | doctrinal/genre class: Madhyamaka, Yogācāra, Abhidharma, Prajñāpāramitā, Pramāṇa, Tathāgatagarbha, Mahāyāna-sūtra, Āgama-Nikāya, Vinaya, Tantra, Avadāna-Jātaka, Stotra-Kāvya, Other |
| `full` | count of **full**-text translations |
| `partial` | count of **partial** (chapter/section/installment) translations |
| `sanskrit_in_repo` | whether the Sanskrit original is present in `dharmanexus-sanskrit` |
| `files_on_drive` | number of translation files located on disk |
| `paths` | their file paths (`[full]`/`[partial]`-tagged) |

For **Japanese**, `full`/`partial` are derived from citation frequency across the
scholarship (a measure of translation activity); `paths` are the matched files in the
dharmanexus modern-Japanese corpus. For **English**, the counts are file-based (the
cleaned English corpus consists largely of the translations/editions themselves).

## Visualization

Each dot is a work, placed in its category column and jittered within it
(a "doctrinal stratification", analogous to the temporal stratification in
`sanskrit-dating`). Dot **size** ∝ number of translations; **green** = a full
translation exists, **grey** = partial only; **✦ / ringed** = Sanskrit original
available in `dharmanexus-sanskrit`. Hover for details, search to highlight, click a
legend category to toggle it.

## Sources & method

- Japanese: bibliographies and article titles of ~7,500 files in
  `dharmanexus-modern-japanese` (citation harvest → Gemini normalization to canonical
  works → file location).
- English: ~8,200 files in `pretraining-2026/en/buddhist-english-cleaned` (per-file
  Gemini classification of work + full/partial scope).
- Works normalized and categorized by `gemini-3-flash-preview`; Sanskrit availability
  cross-referenced against `dharmanexus-sanskrit`.

**Caveats:** Gemini-derived, so expect occasional mis-normalized spelling variants
(e.g. ṃ vs ṅ) and a few scope mislabels; "full" counts can be slightly optimistic.
Treat as a high-recall survey, not an authoritative bibliography.
