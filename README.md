## ..:: Otomoto scraper ::..

<a href="https://nbviewer.jupyter.org/github/BartoszTonia/otomoto_scraper_2/blob/master/electric_secondary_market.ipynb"> Demo file overview </a>

### Co zostało odświeżone
- scraper działa teraz na **Playwright** (bez Selenium),
- domyślnie uruchamia się **Chromium headless** z pełnym viewportem desktop,
- selektory pod szczegóły oferty zostały zmapowane pod aktualny layout (`data-testid`),
- parser wspiera dodatkowo `application/ld+json` (cena/marka/model), co zwiększa odporność na zmiany layoutu.

### Features
Create tables with data scraped from Otomoto search page.

As default it scrape all electric cars with mileage over 1000 km. This can be edited within the code in `main.py`.

Table contains following columns:
- price
- model
- mileage
- year

and more options if they only were assigned in original offer like:
- range for electric cars
- leasing prices
- horsepower
- transmission type
- and more...

### Prerequisites :coffee:

You will need the following things properly installed on your machine.

- python3
- pip3

### Installation :books:
1. Install python dependencies:
```bash
pip3 install -r requirements.txt
```
2. Install Playwright browser binaries:
```bash
python3 -m playwright install chromium
```

### Run
```bash
python3 main.py
```
