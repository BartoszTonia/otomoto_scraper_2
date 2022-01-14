## ..:: Otomoto scraper ::..


### Features
Create tables with data scraped from Otomoto search page. 

As default it scrape all electric cars with mileage over 1000 km. This can be edited within the code in `main.py` at `line #11` 

```
11    search_page = "https://www.otomoto.pl/osobowe?search%5Bfilter_enum_fuel_type%5D=electric&search%5Bfilter_float_mileage%3Afrom%5D=1000"
```


Table contains following columns:
- price
- model
- mileage
- year

and more options if they only were assigned in original offer like:
- <b> range for electric cars </b>
- leasing prices
- horsepower
- transmission type
- and more...

```
"Index(['Unnamed: 0', 'url', 'price', 'Oferta', 'Kategoria', 'Marka', 'Model',
       'Wersja', 'Rok', 'Przebieg', 'Rodzaj', 'Moc', 'Skrzynia', 'Napęd',
       'Typ', 'Liczba', 'Kolor', 'Możliwość', 'Leasing', 'Zarejestrowany',
       'Pierwszy', 'Bezwypadkowy', 'Serwisowany', 'Stan', 'VAT', 'Kraj',
       'Faktura', 'Pierwsza', 'distance', 'Okres', 'lub', 'Numer', 'Gwarancja',
       'Generacja', 'Tuning', 'Opłata', 'Miesięczna', 'Wartość', 'Kierownica',
       'Homologacja', 'Spalanie', 'Emisja', 'Uszkodzony', 'Filtr'],
      dtype='object')"

```


### Prerequisites :coffee:

You will need the following things properly installed on your machine.

* python3
* pip3
```
apt-get install python3-pip
```

### Installation :books:
1. Install all dependencies using 
```
 pip3 install -r requirements.txt 
```


### Run
Try according to line below
```
python3 main.py
```