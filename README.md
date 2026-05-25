# Magnifica Humanitas EPUB

Clean EPUB version of Pope Leo XIV's *Magnifica Humanitas*, generated from the Holy See's HTML source.

Source: https://www.vatican.va/content/leo-xiv/en/encyclicals/documents/20260515-magnifica-humanitas.html

The EPUB includes:

- cover image
- metadata
- table of contents
- footnotes

It validates with `epubcheck` 5.3.0 with no errors or warnings.

## Build

```sh
python3 -m pip install -r requirements.txt
python3 build_magnifica_humanitas_epub.py
epubcheck "Magnifica Humanitas - Pope Leo XIV.epub"
```

