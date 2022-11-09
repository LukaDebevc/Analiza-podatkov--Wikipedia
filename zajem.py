from bs4 import BeautifulSoup
import requests
import re
import json
import csv
import time
import random

class Stran:
    def __init__(self, povezava: str, jezik: str) -> None:
        self.povezava = povezava
        self.jezik = jezik
        self.ustreza = True # nekater strani ne bodo ustrezale in se jih bo izlocilo
        html_strani = self.requests_()
        # soup = BeautifulSoup(html_strani, 'html.parser')

        # self.naslov = self.naslov_(soup)
        self.besedilo = self.besedilo_(html_strani)
        # self.zunanje_povezave = len(soup.find_all)
        self.hiperpovezave = self.hiperpovezave_(html_strani)

        if self.ustreza: self.ocisti_besedilo()

    def requests_(self):
        try: return requests.get(self.povezava).text
        except: return ""
        
    def naslov_(self, soup):
        naslov = re.findall(r">([\w ]*) -", str(soup.title))
        if len(naslov) == 1: return naslov[0]
        else: self.ustreza = False

    # def besedilo_(self, soup, html_strani):
    #     li = jezikovni_slovar[self.jezik]["besede"]
    #     if li[0] == "": 
    #         soup = BeautifulSoup(re.findall(r"parser[\s\S]*?(<p>[\s\S]+)", html_strani)[0], 'html.parser')
    #         print(type(soup.text), soup.text)
    #     besedilo = re.findall(fr"{li[0]}([\s\S]*?)({'|'.join([i for i in li[1:]])})", str(soup.text))
    #     if len(besedilo) == 1: return besedilo[0][0]
    #     else: self.ustreza = False; print("besedilo ne ustreza", [print(nu,"\n",i, "\n") for nu, i in enumerate(besedilo)])
    
    def besedilo_(self, html_strani):
        if len(izlusceno_besedilo := re.findall(r"parser[\s\S]*?(<p>[\s\S]+<\/p>)", html_strani)) != 1: self.ustreza = False
        else: return str(BeautifulSoup(izlusceno_besedilo[0], 'html.parser').text)

    def hiperpovezave_(self, html_strani):
        koncnice = re.findall(r'<a.*"(/wiki/.*?)".*>', html_strani)
        osnova = re.findall(r'(.*?org)', self.povezava)[0]
        return [osnova + i for i in koncnice]
    
    def ocisti_besedilo(self):
        self.besedilo = re.sub(r"\[[\s\S]*?\]", "", self.besedilo)
        self.besedilo = re.sub(r" +", r" ", self.besedilo)
        self.besedilo = re.sub(r"\n+", r"\n", self.besedilo)

    def json(self):
        return [self.povezava, self.jezik, self.besedilo, self.hiperpovezave]
        # return [self.povezava, self.jezik, self.naslov, self.besedilo, self.hiperpovezave]


def dodaj_jezik(jezik:str, zacetna_povezava:str, kljucne_besede:list):
    if jezikovni_slovar.get(jezik, "se_ne_obstaja") == "se_ne_obstaja":
        jezikovni_slovar[jezik] = {
            "besede": kljucne_besede,   # oblika: ["zacetek", "konec_1", "konec_2", ...]
            "zbrani_clanki": [],        # oblika: {"hiperlink": stran.json()}
            "poznane_povezave":{zacetna_povezava: None}, # oblika: {povezava : None}  za O(1) access time
            "ne_prebrane_povezave" : [zacetna_povezava]  # oblika [povezava, povezava, ...]   
        }
    else: raise ValueError(f"jezik {jezik} je ze dodan. Poisci napako.")


def shrani_jezikovni_slovar():
    with open("jeziki.json", "w") as datoteka:
        json.dump(jezikovni_slovar, datoteka, indent = 4)


def generator_csv(slovar):
    for jezik_ in slovar:
        for (povezava, jezik, besedilo, hiperpovezave) in slovar[jezik_]["zbrani_clanki"]:
            yield [jezik, len(hiperpovezave), besedilo]


# jezikovni slovar slika jezik v ključne besede, ki so pomembne za ekstrakcijo podatkov
with open("jeziki.json", "r") as datoteka:
    jezikovni_slovar = json.load(datoteka)

#jezikovni_slovar = {}
## oblika [(jezik, zacetna_povezava, kljucne_besede), ...]
#dodaj_te_jezike = [("sl", "https://sl.wikipedia.org/wiki/Wikipedija", ["Iz Wikipedije, proste enciklopedije", "Sklici", "Zunanje povezave", "Glej tudi", "Viri", "Literatura", "Opombe in sklici"]),
#                   ("en", "https://en.wikipedia.org/wiki/Wikipedia", ["From Wikipedia, the free encyclopedia", "See also", "References", "External links", "Further reading", "Footnotes"]),
#                   ("de", "https://de.wikipedia.org/wiki/Wikipedia", ["", "Siehe auch", "Weblinks", "Einzelnachweise", "Literatur"]),
#                   ("es", "https://es.wikipedia.org/wiki/Wikipedia", ["", "Véase también", "Referencias", "Enlaces externos", "Bibliografía", "Libros"]),
#                   ("hr", "https://hr.wikipedia.org/wiki/Wikipedija", ["", "Vidi još", "Izvori", "Vanjske poveznice"]),
#                   ("it", "https://it.wikipedia.org/wiki/Wikipedia", ["Da Wikipedia, l'enciclopedia libera.", "Bibliografia", "Voci correlate", "Altri progetti", "Collegamenti esterni", "Note"]),
#                   ("fr", "https://fr.wikipedia.org/wiki/Wikip%C3%A9dia", ["", "Notes et références", "Voir aussi", "Liens externes", "Articles connexes", "Bibliographie", "Références", "Annexes"]),
#                   ("pt", "https://pt.wikipedia.org/wiki/Wikip%C3%A9dia", ["Origem: Wikipédia, a enciclopédia livre.", "Ver também", "Referências", "Ligações externas", "Notas"]),
#                   ("hu", "https://hu.wikipedia.org/wiki/Wikip%C3%A9dia", ["A Wikipédiából, a szabad enciklopédiából", "Jegyzetek", "Források", "Kapcsolódó szócikkek", "További információk", "További irodalom"]),
#                   ("sk", "https://sk.wikipedia.org/wiki/Wikip%C3%A9dia", ["", "Iné projekty", "Externé odkazy", "Zdroj", "Literatúra", "Referencie", "Pozri aj"]),
#                   ("nl", "https://nl.wikipedia.org/wiki/Wikipedia", ["", "Zie ook", "Externe link", "Noten en referenties", "Bronnen", "Literatuur"]),
#                   ("la", "https://la.wikipedia.org/wiki/Vicipaedia", ["", "Notae", "Bibliographia", "Nexus interni", "Nexus externi", "Notae"]),
#                   ("sv", "https://sv.wikipedia.org/wiki/Wikipedia", ["", "Bokkällor", "Externa länkar", "Noter", "Se även, Referenser"]),
#                   ("no", "https://no.wikipedia.org/wiki/Wikipedia", ["Fra Wikipedia, den frie encyklopedi", "Referanser", "Fotnoter", "Se også", "Eksterne lenker"]),
#                   ("fi", "https://fi.wikipedia.org/wiki/Wikipedia", ["", "Sisarhankkeet", "Lähteet", "Aiheesta muualla", "Muuta", "Kirjallisuutta", "Dokumenttielokuvia", "Katso myös"]),
#                   ("pl", "https://pl.wikipedia.org/wiki/Wikipedia", ["", "Uwagi", "Przypisy", "Bibliografia", "Linki zewnętrzne", "Zobacz też", "Przypisy"]),
#                   ("ru", "https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F", ["Материал из Википедии — свободной энциклопедии", "Ссылки", "Литература", "Источники", "Публикации", "См. также", "Примечания", "Комментарии"]),
#                   ("uk", "https://uk.wikipedia.org/wiki/%D0%92%D1%96%D0%BA%D1%96%D0%BF%D0%B5%D0%B4%D1%96%D1%8F", []),
#                   ("ro", "https://ro.wikipedia.org/wiki/Wikipedia", []),
#                   ("tr", "https://tr.wikipedia.org/wiki/Vikipedi", []),
#                   ("el", "https://el.wikipedia.org/wiki/%CE%92%CE%B9%CE%BA%CE%B9%CF%80%CE%B1%CE%AF%CE%B4%CE%B5%CE%B9%CE%B1", []),
#                   ("cs", "https://cs.wikipedia.org/wiki/Wikipedie", []),
#                   ("sr", "https://sr.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%98%D0%B0", []),
#                   ("bg", "https://bg.wikipedia.org/wiki/%D0%A3%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F", []),
#                   ("da", "https://da.wikipedia.org/wiki/Wikipedia", []),
#                   ("bar", "https://bar.wikipedia.org/wiki/Wikipedia", []),
#                   ("sq", "https://sq.wikipedia.org/wiki/Wikipedia", []),
#                   ("ca", "https://ca.wikipedia.org/wiki/Viquip%C3%A8dia", []),
#                   ("scn", "https://scn.wikipedia.org/wiki/Wikipedia", []),
#                   ("lmo", "https://lmo.wikipedia.org/wiki/Wikipedia", []),
#                   ("be", "https://be.wikipedia.org/wiki/%D0%92%D1%96%D0%BA%D1%96%D0%BF%D0%B5%D0%B4%D1%8B%D1%8F", []),
#                   ("lt", "https://lt.wikipedia.org/wiki/Vikipedija", []),
#                   ("bs", "https://bs.wikipedia.org/wiki/Wikipedia", []),
#                   ("lv", "https://lv.wikipedia.org/wiki/Vikip%C4%93dija", []),
#                   ("et", "https://et.wikipedia.org/wiki/Vikipeedia", []),
#                   ("is", "https://is.wikipedia.org/wiki/Wikipedia", []),
#                   ("ga", "https://ga.wikipedia.org/wiki/Vicip%C3%A9id", []),
#                   ("lb", "https://lb.wikipedia.org/wiki/Wikipedia", []),
#                   ("mk", "https://mk.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%98%D0%B0", []),
#                   ("mt", "https://mt.wikipedia.org/wiki/Wikipedija", [])]

dodaj_te_jezike = []
STEVILO_CLANKOV = 200
k = 0

if __name__ == "__main__":
    for jezik in dodaj_te_jezike:
        dodaj_jezik(jezik[0], jezik[1], jezik[2])
    
    i = 0 # steje kdaj smo nazadnje preventivno shranili slovar
    for jezik in jezikovni_slovar:
        print(jezik)
        zbrani_clanki = jezikovni_slovar[jezik]["zbrani_clanki"]
        nadaljne_povezave = jezikovni_slovar[jezik]["ne_prebrane_povezave"]
        poznane_povezave = jezikovni_slovar[jezik]["poznane_povezave"]

        while len(zbrani_clanki) < STEVILO_CLANKOV: 
            print(i)
            nakljucno_stevilo = random.randrange(len(nadaljne_povezave))
            izbrana_povezava = nadaljne_povezave[nakljucno_stevilo]
            if nakljucno_stevilo < len(zbrani_clanki) - 1:
                nadaljne_povezave[nakljucno_stevilo] = nadaljne_povezave.pop()
            else: nadaljne_povezave.pop()
            
            stran = Stran(izbrana_povezava, jezik)
            if stran.ustreza: 
                zbrani_clanki.append(stran.json())
            for hiperpovezava in stran.hiperpovezave:
                if poznane_povezave.get(hiperpovezava, "ne_poznamo") == "ne_poznamo":
                    poznane_povezave[hiperpovezava] = None
                    nadaljne_povezave.append(hiperpovezava)
            
            i += 1; time.sleep(0) # ni potrebno, koda je pocasna
            if i % 2 ** k == 0: shrani_jezikovni_slovar(); k += 1

        if (n := i) != i: shrani_jezikovni_slovar(); n = i

    with open("podatki.csv", "w", encoding="utf-8", newline="") as datoteka:
        csv.writer(datoteka, delimiter="¤").writerow(["jezik", "povezave", "besedilo"])

    with open("podatki.csv", "a", encoding="utf-8", newline='') as datoteka:
        writer = csv.writer(datoteka, delimiter="¤")
        for vrstica in generator_csv(jezikovni_slovar): writer.writerow(vrstica)

    
