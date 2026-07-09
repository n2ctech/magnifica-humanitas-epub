# Magnifica Humanitas EPUB

Clean EPUB versions of Pope Leo XIV's *Magnifica Humanitas*, generated from the Holy See's HTML source.

Sources:

- English: https://www.vatican.va/content/leo-xiv/en/encyclicals/documents/20260515-magnifica-humanitas.html
- French: https://www.vatican.va/content/leo-xiv/fr/encyclicals/documents/20260515-magnifica-humanitas.html
- Italian: https://www.vatican.va/content/leo-xiv/it/encyclicals/documents/20260515-magnifica-humanitas.html
- Portuguese: https://www.vatican.va/content/leo-xiv/pt/encyclicals/documents/20260515-magnifica-humanitas.html

The EPUBs include:

- cover image
- metadata
- table of contents
- footnotes

It validates with `epubcheck` 5.3.0 with no errors or warnings.

## Build

```sh
python3 -m pip install -r requirements.txt
python3 build_magnifica_humanitas_epub.py --lang en
python3 build_magnifica_humanitas_epub.py --lang fr
python3 build_magnifica_humanitas_epub.py --lang it
python3 build_magnifica_humanitas_epub.py --lang pt
epubcheck "Magnifica Humanitas - Pope Leo XIV.epub"
epubcheck "Magnifica Humanitas - Pape Leon XIV (fr).epub"
epubcheck "Magnifica Humanitas - Papa Leone XIV (it).epub"
epubcheck "Magnifica Humanitas - Papa Leao XIV (pt).epub"
```

The converter is not bound to English text. It is currently configured for the English, French, Italian, and Portuguese Vatican pages; adding another language is mostly a matter of adding the Vatican URL and localized metadata.
