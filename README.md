# Magnifica Humanitas EPUB

Clean EPUB versions of Pope Leo XIV's *Magnifica Humanitas*, generated from the Holy See's HTML source.

The EPUBs include:

- cover image
- metadata
- table of contents
- footnotes

It validates with `epubcheck` 5.3.0 with no errors or warnings.

## Download

| Language | Source | Result |
| --- | --- | --- |
| English | [HTML](https://www.vatican.va/content/leo-xiv/en/encyclicals/documents/20260515-magnifica-humanitas.html) | [EPUB](../../releases/download/latest/Magnifica.Humanitas.-.Pope.Leo.XIV.epub) |
| French | [HTML](https://www.vatican.va/content/leo-xiv/fr/encyclicals/documents/20260515-magnifica-humanitas.html) | [EPUB](../../releases/download/latest/Magnifica.Humanitas.-.Pape.Leon.XIV.fr.epub) |
| German | [HTML](https://www.vatican.va/content/leo-xiv/de/encyclicals/documents/20260515-magnifica-humanitas.html) | [EPUB](../../releases/download/latest/Magnifica.Humanitas.-.Papst.Leo.XIV.de.epub) |
| Spanish | [HTML](https://www.vatican.va/content/leo-xiv/es/encyclicals/documents/20260515-magnifica-humanitas.html) | [EPUB](../../releases/download/latest/Magnifica.Humanitas.-.Papa.Leon.XIV.es.epub) |
| Italian | [HTML](https://www.vatican.va/content/leo-xiv/it/encyclicals/documents/20260515-magnifica-humanitas.html) | [EPUB](../../releases/download/latest/Magnifica.Humanitas.-.Papa.Leone.XIV.it.epub) |
| Portuguese | [HTML](https://www.vatican.va/content/leo-xiv/pt/encyclicals/documents/20260515-magnifica-humanitas.html) | [EPUB](../../releases/download/latest/Magnifica.Humanitas.-.Papa.Leao.XIV.pt.epub) |
| Polish | [HTML](https://www.vatican.va/content/leo-xiv/pl/encyclicals/documents/20260515-magnifica-humanitas.html) | [EPUB](../../releases/download/latest/Magnifica.Humanitas.-.Papiez.Leon.XIV.pl.epub) |

## Build

```sh
python3 -m pip install -r requirements.txt
for lang in en fr de es it pt pl; do
  python3 build_magnifica_humanitas_epub.py --lang "$lang"
done
epubcheck "Magnifica Humanitas - Pope Leo XIV.epub"
epubcheck "Magnifica Humanitas - Pape Leon XIV (fr).epub"
epubcheck "Magnifica Humanitas - Papst Leo XIV (de).epub"
epubcheck "Magnifica Humanitas - Papa León XIV (es).epub"
epubcheck "Magnifica Humanitas - Papa Leone XIV (it).epub"
epubcheck "Magnifica Humanitas - Papa Leao XIV (pt).epub"
epubcheck "Magnifica Humanitas - Papiez Leon XIV (pl).epub"
```

The converter is not bound to English text. It is currently configured for the English, French, German, Spanish, Italian, Portuguese, and Polish Vatican pages; adding another language is mostly a matter of adding the Vatican URL and localized metadata.
