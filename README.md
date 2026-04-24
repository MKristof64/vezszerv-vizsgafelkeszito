# VezSzerv vizsgafelkészítő

Ez a projekt egy statikus, böngészőből megnyitható magyar nyelvű tanulóapp a `VezSzerv Teljes KönyvA.pdf` anyaghoz. A kész app közvetlenül megnyitható helyben, és GitHubon is megosztható.

## Mi van a repóban?

- `index.html`: GitHub Pages-barát belépőoldal, ami az appra irányít.
- `output/vezszerv-tanuloapp.html`: a kész, megnyitható app.
- `output/topics.generated.json`: a generált, beágyazott témaköri adat forrása.
- `data/topic_blueprint.json`: a gondozott témaköri tartalom.
- `scripts/build_topic_data.py`: témaköri adatok előállítása.
- `scripts/build_html_app.py`: a standalone HTML app generátora.
- `scripts/build.ps1`: teljes build PowerShell wrapper.
- `scripts/extract-book-ocr.ps1`: helyi OCR export a könyvhöz.

## Helyi használat

Gyors build OCR smoke testtel:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -RunOcr -Pages "5,120,300"
```

Build OCR nélkül:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

Ezután megnyitható:

- `.\index.html`
- vagy `.\output\vezszerv-tanuloapp.html`

## GitHub megosztás

Ez a projekt úgy van előkészítve, hogy repo formában vagy GitHub Pages-szel is meg lehessen osztani.

Ajánlott lépések:

1. Hozz létre egy új GitHub repót, például `vezszerv-vizsgafelkeszito` néven.
2. Töltsd fel ezt a projektmappát.
3. Ha webes megosztást szeretnél, kapcsold be a GitHub Pages-t a repository gyökerére.
4. A megosztott belépési pont a gyökérben lévő `index.html`.

## A `Könyv` gomb viselkedése

- Helyi megnyitásnál a gomb a gépen lévő PDF-et nyitja meg.
- GitHubon a helyi `file:///` link nem működne, ezért a gomb ott nem lesz törött link.
- Ha a könyvhöz webes linket is szeretnél, két lehetőség van:

1. Adj meg egy külső URL-t build előtt:

```powershell
$env:VEZSZERV_BOOK_SHARE_URL = "https://pelda.hu/vezszerv-konyv.pdf"
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

2. Tegyél egy megosztható PDF-et a `book/` mappába, GitHub-kompatibilis méretben.

Megjegyzés:

- A jelenlegi helyi könyv túl nagy ahhoz, hogy simán GitHubra kerüljön.
- A GitHub normál feltöltési limitje 100 MB fájlonként, ezért a teljes helyi PDF-et nem érdemes közvetlenül a repóba tenni.

## Fontos

- A builder OCR nélkül is működik.
- A kész app futás közben nem igényel backendet.
- A hash-alapú témalinkek GitHubon is működnek.
