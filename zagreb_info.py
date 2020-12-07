import requests
from bs4 import BeautifulSoup
import csv
import json
import datetime
import os

#lista linkova kategorija
def listaLinkovaGlavnogIzbornika(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    kategorije = soup.find_all(class_='td-menu-item')
    for kategorija in kategorije:
        link = kategorija.find('a')['href']
        if ((link != "https://www.zagreb.info/category/aktualno/") and (link != "https://www.zagreb.info/category/sport/") and (link != "https://www.zagreb.info/category/ritam-grad/") and (link != "https://www.zagreb.info/category/ritam-grad/kultura/")
        and (link != "https://www.zagreb.info/impressum") and (link != "https://www.zagreb.info/uvjeti-koristenja") and (link != "https://www.zagreb.info/marketing")):
            listaLinkova.append(link)
    return listaLinkova

#lista linkova clanaka po kategoriji
def listaLinkovaKategorije(bazniUrlKategorije, strana):
    response = requests.get(bazniUrlKategorije + str(strana))
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('div', class_='td-ss-main-content')
    linkovi = [] 
    for block in main_content.findAll('div', class_='td-block-row'):
        for span in block.findAll( 'div', class_='td-block-span6'): 
            linkovi.append(span.find('a')['href'])
    return linkovi

#podaci unutar clanka
def informacijeOclanku(urlClanka):
    response = requests.get(urlClanka)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all(class_='td-ss-main-content')
    id_Cl, title, objavio, date, tekst, kategorija = "", "", "", "", "", ""

    for post in posts:
        id_Cl = idClanka(urlClanka)
        title = post.find(class_ = 'entry-title').get_text().replace('\n', '')
        date = post.find("time", class_ = "entry-date")
        if (post.find("strong")):
            objavio = post.find("strong").get_text()
        else:
            objavio =post.find('a').contents[0]
        tekst = post.find(class_ = 'td-post-content').get_text().replace("\n", "").replace('ShareFacebookTwitterEmailPrintKomentari', '')
        kategorija = kategorijaClanka(urlClanka)
    if (date != ""):
        date = date.get_text()
    return id_Cl, title, objavio, date, tekst, kategorija

#id clanka iz url-a
def idClanka(url):
    razdvojeno = url.split("/")
    razdvojeno = razdvojeno[::-1]
    return razdvojeno[1]

#kategorija iz url-a
def kategorijaClanka(url):
    razdvojeno = url.split("/")
    return razdvojeno[3]

#upis u txt
def upisLinkovaTxt(url, file):
    append_write = 'w'
    if os.path.exists(file):
        append_write = 'a'
    with open(file, append_write) as f:
        f.write("%s\n" % url)

#ispisuje informacije o clancima - test
def ispisSvihInfoSvihClanaka(url):
    for link in listaLinkovaGlavnogIzbornika(url):
        linkoviClanakaJedneKategorije = listaLinkovaKategorije(link+"page/", 1) 
        for l in linkoviClanakaJedneKategorije:
            id_Cl, title, objavio, date, tekst, kategorija = informacijeOclanku(l)
            print("ID: ", id_Cl)
            print ('Naslov: ', title)
            print ('Objavio: ', objavio)
            print ('Datum: ', date)
            print('Tekst: ', tekst)
            print('kategorija:', kategorija)
            print('Link: ', l)

#pretvorba datuma u int
def pretvorbaDatuma(datum):
    razdvojeno = datum.split(" ")
    dan = razdvojeno[0].replace('.', '')
    godina = razdvojeno[2].replace('.', '')
    mjesec = 0
    if "sije" in razdvojeno[1]:
        mjesec = 1
    if "velj" in razdvojeno[1]:
        mjesec = 2
    if "ožu" in razdvojeno[1]:
        mjesec = 3
    if "trav" in razdvojeno[1]:
        mjesec = 4
    if "svib" in razdvojeno[1]:
        mjesec = 5
    if "lip" in razdvojeno[1]:
        mjesec = 6
    if "srp" in razdvojeno[1]:
        mjesec = 7
    if "kol" in razdvojeno[1]:
        mjesec = 8
    if "ruj" in razdvojeno[1]:
        mjesec = 9
    if "lis" in razdvojeno[1]:
        mjesec = 10
    if "stu" in razdvojeno[1]:
        mjesec = 11
    if "pro" in razdvojeno[1]:
        mjesec = 12
    return int(dan), int(mjesec), int(godina)

#upis u csv file
def upisCsv(file, id_Cl, title, objavio, date, tekst, kategorija, l):
    redak = [id_Cl, title, objavio, date, tekst, kategorija, l]
    with open(file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(redak)
    csvfile.close() 

#priprema za upis u json file
def upisRedakJson(jsonRed, id_Cl, title, objavio, date, tekst, kategorija, l):
    redak = {"ID: " : id_Cl, "Naslov: " : title, "Autor: " : objavio, "Datum: " : date, "Tekst: " : tekst, "Kategorija: " : kategorija, "url: " : l}
    jsonRed.append(redak)

linkovi = [] 
listaLinkova = []
linkoviClanakaJedneKategorije = []

with open('ZagrebInfo.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = ["ID", "NASLOV", "AUTOR", "DATUM", "TEKST", "KATEGORIJA", "URL"])
    writer.writeheader()
csvfile.close()

jsonCijeli = []

for link in listaLinkovaGlavnogIzbornika('https://www.zagreb.info/'):
    strana = 1
    datumNijePostignut = True
    while datumNijePostignut:
        linkoviClanakaJedneKategorije = listaLinkovaKategorije(link+"page/", strana)
        for l in linkoviClanakaJedneKategorije:
            id_Cl, title, objavio, date, tekst, kategorija = informacijeOclanku(l)
            if (date == ""):
                continue
            dan, mjesec, godina = pretvorbaDatuma(date)
            datum_clanka = datetime.datetime(godina, mjesec, dan)
            datum_od = datetime.datetime(2020, 1, 1)
            datum_do = datetime.datetime(2020, 11, 30)
            if ((datum_clanka >= datum_od) and (datum_clanka <= datum_do)):
                print (datum_clanka, " ", l)
                upisLinkovaTxt(l, 'ZagrebInfo_linkovi.txt')
                upisCsv('ZagrebInfo.csv', id_Cl, title, objavio, date, tekst, kategorija, l)
                upisRedakJson(jsonCijeli, id_Cl, title, objavio, date, tekst, kategorija, l)
            if (datum_clanka < datum_od):
                datumNijePostignut = False
                break
        strana = strana + 1 

with open('ZagrebInfo.json', "w", encoding='utf-8') as jsonFile:
    json.dump(jsonCijeli, jsonFile, indent=4, ensure_ascii=False)