# Analiza podatkov

Analiziral bom članke [Wikipedije](https://www.wikipedia.org/) v različnih Evropskih jezikih.
___________
### V člankih bom zajel:
-	besedilo (dolžino člankov in drugo)
-	število povezav na druge članke v samem besedilu Wikipedije

_Pri besedilu bom pozoren tudi na razlike med jeziki, ki so porabljeni v članku glede na frekvenčna porazdelitev črk in besed ter dolžina stavkov in povedi._

_____________
### Delovne hipoteze:
-	Predvidevam, da bodo članki veliko daljši, meli več hiperpovezav v jezikih z večjim številom naravnih govorcev.
-   Predvidevam, da so krajše besede pogosteje uporabljene kot daljše.
-	Ali imajo članki v različnih jezikih različno frekvenčno porazdelitev besed in črk?
-	Ali lahko predvidimo jezik v katerem je bil članek napisan na podlagi zajetih podatkov?

_______________
### Podatki:
-   Podatki se nahajajo v **podatki.csv**,
-   ločeni so ločeni z **¤** in
-   so oblike **jezik**¤**povezave**¤**besedilo**.

*Pod povezave je mišljeno število hiperpovezav na druge članke v istem jeziku.*