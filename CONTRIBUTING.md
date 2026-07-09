# Contributing

Thank you for helping make *Magnifica Humanitas* readable on more devices and in more languages. New language editions, converter fixes, and careful proofreading against the Vatican source are all welcome.

## Before you start

Check the open pull requests and issues first so we don't duplicate each other's work. If an issue for your language already exists, leave a comment to claim it; if someone has an open PR for it, please contribute your findings there instead of opening a parallel one.

## Adding a language

1. **Find the Vatican source page.** The URL pattern is
   `https://www.vatican.va/content/leo-xiv/<lang>/encyclicals/documents/20260515-magnifica-humanitas.html`.
   The language switcher on the English page lists every published version (nine as of July 2026; Chinese and Latin have not been published by the Vatican).
2. **Add an entry to `LANGUAGE_CONFIGS`** in `build_magnifica_humanitas_epub.py`, following the existing entries: `source_url`, `source_html`, `build_dir`, `output_epub`, localized metadata (`title`, `subtitle`, `author`, `publisher`, cover and page labels), plus `start_anchors` and `top_level_pattern`.
3. **Verify everything against the actual page, not a translation you'd expect.** The subtitle must be exactly as printed. Watch for page quirks: the first body anchor often differs from English (`INTRODUCTION_` has a trailing underscore, most other languages don't), anchor names may contain HTML entities or non-ASCII characters, and `top_level_pattern` must match the TOC link texts at the top of the page (it is applied case-insensitively).
4. **Build and validate:**
   ```sh
   python3 -m pip install -r requirements.txt
   python3 build_magnifica_humanitas_epub.py --lang <lang>
   epubcheck <output>.epub
   ```
   epubcheck must report zero errors and zero warnings.
5. **Open the EPUB in an actual reader** and spot-check the table of contents, a few footnote round-trips, and the cover.

## Converter changes

If you touch shared code, please rebuild and validate all configured languages before submitting, since a change that fixes one Vatican page can silently break another.

## Copyright ground rules

The encyclical text is Copyright © Dicastery for Communication – Libreria Editrice Vaticana (see `NOTICE`). We reproduce it **unmodified**: no typo fixes, no reflowing, no editorial touches, even when tempting. If you spot an error in the source page, mention it in your PR description instead of fixing the text. Everything here is non-commercial and fully attributed.
