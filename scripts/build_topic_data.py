from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = Path(r"C:\Users\krist\OneDrive\Dokumentumok\vezsz")
DEFAULT_BOOK_SHARE_URL = "https://mersz.hu/kiadvany/147/"

TOPIC_STUDY_GUIDES = {
    "szervezet-vezetes-hatekonysag-eredmenyesseg": {
        "scenario": "egy franchise pékséghálózat vezetője két új üzlet megnyitását értékeli szűk költségkeret mellett",
        "sampleQuestion": "Mi a különbség a hatékonyság és az eredményesség között, és miért kell mindkettőt egyszerre vizsgálni?",
        "commonTrap": "A hallgató ugyanannak tekinti a hatékonyságot és az eredményességet, vagy csak az egyik oldalt magyarázza el.",
        "examFocus": [
            "definíció után azonnal tudj példát mondani szervezeti helyzetre",
            "különítsd el a cél elérését az erőforrás-felhasználástól",
            "mutasd meg, hogy vezetés nélkül a fogalmak nem kapcsolódnak döntéshez",
        ],
    },
    "menedzsment-vs-leadership-vezetesi-funkciok": {
        "scenario": "egy regionális kórházi igazgató egyszerre akar stabil működést és változást elérni",
        "sampleQuestion": "Miben más a menedzseri és a leaderi fókusz, és hogyan jelenik meg ez a négy vezetési funkcióban?",
        "commonTrap": "Csak személyiségtípusokként írja le a két fogalmat, és nem köti őket vezetői feladathoz.",
        "examFocus": [
            "ne csak felsorold a funkciókat, hanem kösd őket konkrét vezetői munkához",
            "értsd, hogy a menedzser és a leader nem egymást kizáró szerepek",
            "tudd elhelyezni a funkciókat a különböző hierarchiaszinteken",
        ],
    },
    "strategiai-premisszak-es-platform": {
        "scenario": "egy technológiai startup tulajdonosai új piacra lépést készítenek elő eltérő kockázati étvággyal",
        "sampleQuestion": "Mik a stratégiai premisszák, és miért fontos a domináns koalíció a stratégiaalkotás elején?",
        "commonTrap": "A premisszákat kész tényként kezeli, és nem hangsúlyozza, hogy ezek feltételezések.",
        "examFocus": [
            "mutasd be, hogy a stratégia mindig valamilyen előfeltevésre épül",
            "magyarázd el, miért kell szereplői egyetértés a végrehajtás előtt",
            "kösd a témát a későbbi célkijelöléshez és kontrollhoz",
        ],
    },
    "misszio-vizio-es-strategiai-celok": {
        "scenario": "egy hazai egészségügyi szolgáltató országos terjeszkedést tervez, de közben meg akarja őrizni küldetését",
        "sampleQuestion": "Hogyan különbözik egymástól a misszió, a vízió és a stratégiai cél, és milyen kapcsolatnak kell köztük lennie?",
        "commonTrap": "Összekeveri az identitást, a jövőképet és a mérhető célokat.",
        "examFocus": [
            "mindhárom fogalomhoz tudj rövid definíciót és különbséget mondani",
            "emeld ki a mérhetőséget és a határidőt a stratégiai céloknál",
            "mutasd meg, hogy a misszió nem ugyanaz, mint egy reklámszlogen",
        ],
    },
    "strategiak-szintjei": {
        "scenario": "egy élelmiszeripari vállalat egyszerre dönt portfólióról, piaci pozícióról és HR-fejlesztésről",
        "sampleQuestion": "Melyek a stratégia fő szintjei, és miben adnak más típusú választ a vállalat működésére?",
        "commonTrap": "Nem választja szét a vállalati, verseny- és funkcionális szintet.",
        "examFocus": [
            "tudd azonosítani, melyik döntés melyik stratégiai szinthez tartozik",
            "magyarázd el a vertikális összhang jelentőségét",
            "kapcsold a stratégiákat a végrehajtó tervekhez és a háttérfunkciókhoz",
        ],
    },
    "uzleti-terv-operativ-terv-es-tervezesi-logikak": {
        "scenario": "egy gyártóvállalatnak egyszerre kell hároméves beruházási tervet és éves értékesítési tervet készítenie",
        "sampleQuestion": "Miben más az üzleti terv és az operatív terv, és hogyan tér el a felülről lefelé, az alulról felfelé és az ellenáramú tervezés?",
        "commonTrap": "A hallgató csak időtáv szerint különbözteti meg a terveket, de nem beszél a felelősségekről és a tervezési logikákról.",
        "examFocus": [
            "tudd megmutatni a stratégia és a napi működés közötti hidat",
            "különítsd el a centralizált és decentralizált tervezés előnyeit",
            "emeld ki, hogy a terv számszerűsített és felelősökhöz kötött",
        ],
    },
    "kulso-kornyezet-es-iparagelemzes": {
        "scenario": "egy új elektromos rollermegosztó szolgáltatás belépne egy erősen szabályozott városi piacra",
        "sampleQuestion": "Miért stratégiai input a külső környezet- és iparágelemzés, és mire kell figyelni egy vezetőnek az elemzés során?",
        "commonTrap": "Általános trendlistát mond, de nem köti össze a környezetet a szervezeti mozgástérrel.",
        "examFocus": [
            "ne csak tényezőket sorolj, hanem mutasd meg a hatásukat a döntésekre",
            "kapcsold össze a környezetet a misszióval és a célokkal",
            "értsd, hogy ugyanaz a trend lehet veszély és lehetőség is",
        ],
    },
    "kontingenciaelmelet-es-szervezeti-illeszkedes": {
        "scenario": "egy gyorsan változó szoftvercég és egy stabil közszolgáltató eltérő szervezeti megoldásokat keres",
        "sampleQuestion": "Mit állít a kontingenciaelmélet, és hogyan jelenik meg benne az illeszkedés logikája?",
        "commonTrap": "Azt mondja, hogy van egy legjobb szervezeti forma minden helyzetre.",
        "examFocus": [
            "tedd világossá, hogy nincs univerzális recept",
            "mondd ki az illeszkedés fő elemeit: környezet, stratégia, struktúra, magatartás, teljesítmény",
            "példával igazold, hogy ugyanaz a megoldás más helyzetben rossz lehet",
        ],
    },
    "szervezetalakitast-befolyasolo-tenyezok": {
        "scenario": "egy családi vállalkozás országos hálózattá nő, miközben a régi emberekre és a régi rutinokra épít",
        "sampleQuestion": "Mely tényezők befolyásolják a szervezetalakítást, és miért nem lehet egyik napról a másikra teljesen új struktúrát bevezetni?",
        "commonTrap": "Csak a környezetről beszél, és kihagyja a belső adottságokat, a meglévő struktúrát és az emberi oldalt.",
        "examFocus": [
            "különítsd el a rövid távon és a középtávon változtatható tényezőket",
            "emeld ki a meglévő emberi erőforrás korlátait",
            "mutasd be a vezetés kettős feladatát: alkalmazkodás és feltételalakítás",
        ],
    },
    "egyszeru-es-funkcionalis-szervezet": {
        "scenario": "egy kis kézműves műhelyből közepes méretű gyártóvállalat lesz, és el kell dönteni, maradjon-e minden a tulajdonos kezében",
        "sampleQuestion": "Miben különbözik az egyszerű és a funkcionális szervezet, és milyen helyzetben melyik forma előnyös?",
        "commonTrap": "Csak a szervezeti ábrát írja le, de nem mond semmit a koordinációról és a méretfeltételekről.",
        "examFocus": [
            "hasonlítsd össze a centralizációt és a szakosodást",
            "tudd az előnyöket és a tipikus korlátokat is elmondani",
            "kapcsold a modellt a szervezet méretéhez és tevékenységéhez",
        ],
    },
    "divizionalis-szervezet": {
        "scenario": "egy országos kereskedelmi lánc termékcsoportonként külön vezetést alakít ki saját eredményfelelősséggel",
        "sampleQuestion": "Mikor indokolt a divizionális szervezet, és milyen előnyökkel illetve kockázatokkal jár?",
        "commonTrap": "Csak a decentralizációt emeli ki, de nem beszél az output-felelősségről és a párhuzamosságokról.",
        "examFocus": [
            "magyarázd el, hogyan jön létre az önálló egységfelelősség",
            "mutasd meg, miért kapcsolódik ehhez gyakran piaci kontroll",
            "ne felejtsd el a belső rivalizálás és többletköltség kockázatát",
        ],
    },
    "matrixszervezet": {
        "scenario": "egy nemzetközi tanácsadó cégnél a munkatárs egyszerre tartozik szakmai vezetőhöz és projekthez",
        "sampleQuestion": "Mi a mátrixszervezet lényege, és miért egyszerre előnyös és konfliktusveszélyes megoldás?",
        "commonTrap": "Csak annyit mond, hogy két főnök van, de nem mutatja meg, mire jó ez a modell.",
        "examFocus": [
            "hangsúlyozd a többdimenziós működés előnyét",
            "emeld ki a kettős függés koordinációs feszültségeit",
            "kösd a modellt összetett, gyorsan változó környezethez",
        ],
    },
    "munkamegosztas-koordinacio-formalizalas": {
        "scenario": "egy logisztikai központban nő a forgalom, ezért újra kell osztani a feladatokat és szabályozni kell az átadásokat",
        "sampleQuestion": "Mit jelent a munkamegosztás, a koordináció és a formalizálás, és hogyan hatnak együtt a szervezeti működésre?",
        "commonTrap": "Külön-külön definiálja a fogalmakat, de nem mutatja meg, hogyan függnek össze.",
        "examFocus": [
            "tudd összekapcsolni a feladatmegosztást a koordináció szükségességével",
            "emeld ki a formalizálás előnyét és túlzásának veszélyét",
            "magyarázd el, hogy a struktúra nem csak rajz, hanem működési logika",
        ],
    },
    "folyamatszervezes-alapjai": {
        "scenario": "egy egyetemi ügyfélszolgálatnál a hallgatói kérelmek túl lassan futnak végig a rendszeren",
        "sampleQuestion": "Miért más a folyamatszervezési szemlélet, mint a klasszikus struktúraszemlélet, és milyen célokat szolgál?",
        "commonTrap": "A szervezeti egységeket magyarázza, de nem a végigfutó tevékenységsort.",
        "examFocus": [
            "mutasd meg a minőség-költség-idő hármas célt",
            "emeld ki, hogy a folyamat átnyúlik a szervezeti határokon",
            "tudd összekötni a szemléletet vevői vagy ügyfélélménnyel",
        ],
    },
    "folyamatoptimalizalas-cpi": {
        "scenario": "egy biztosító javítani akarja a kárbejelentési folyamatot anélkül, hogy mindent a nulláról újratervezne",
        "sampleQuestion": "Miben áll a folyamatoptimalizálás logikája, és miben különbözik a radikális újratervezéstől?",
        "commonTrap": "Ugyanaznak tekinti a CPI-t és az újratervezést.",
        "examFocus": [
            "tudd hangsúlyozni a lépésenkénti fejlesztést",
            "kapcsold össze a folyamatelemzéssel és az optimalizálási célokkal",
            "mutasd meg, hogy a meglévő folyamat logikája megmarad",
        ],
    },
    "ujratervezes-es-radikalis-folyamatatalakitas": {
        "scenario": "egy hagyományos könyvelőiroda teljesen digitális működésre áll át, mert a régi folyamat már versenyképtelen",
        "sampleQuestion": "Mikor indokolt a radikális folyamat-újratervezés, és miben más a logikája, mint az optimalizálásé?",
        "commonTrap": "A hallgató csak annyit mond, hogy nagyobb változás, de nem mutatja meg a szemléletváltást.",
        "examFocus": [
            "mondd ki, hogy nem a régi folyamat javítása, hanem új logika építése a cél",
            "emeld ki a szervezeti ellenállás és a vezetői támogatás szerepét",
            "kapcsold a témát a működési jövőképhez és az implementációs kockázathoz",
        ],
    },
    "leader-vs-menedzser-kotter": {
        "scenario": "egy gyárigazgatónak egyszerre kell költségfegyelmet tartania és egy új szervezeti kultúrát elindítania",
        "sampleQuestion": "Hogyan különíti el Kotter a leader és a menedzser szerepét, és miért van szükség mindkettőre?",
        "commonTrap": "A hallgató értékítéletet mond, és nem mutatja meg a két szerep kiegészítő jellegét.",
        "examFocus": [
            "kösd a menedzsert a rendhez és a leadert a változáshoz",
            "mutasd meg, hogy ugyanaz a vezető is gyakorolhatja mindkét logikát",
            "kapcsold a témát szervezeti helyzethez, ne maradjon elvont",
        ],
    },
    "mintzberg-vezetoi-szerepei": {
        "scenario": "egy üzemvezető napja percek alatt vált tárgyalásból problémamegoldásba, majd erőforrás-elosztásba",
        "sampleQuestion": "Melyek Mintzberg fő vezetői szerepei, és mit árulnak el a vezetői munka természetéről?",
        "commonTrap": "Felsorolja a szerepeket, de nem magyarázza el, hogy a vezetői munka miért töredezett és kommunikációintenzív.",
        "examFocus": [
            "tudd a szerepeket a három nagy csoportba rendezni",
            "kapcsold a szerepeket konkrét napi vezetői helyzetekhez",
            "emeld ki, hogy a vezetői munka nem lineáris feladatlista",
        ],
    },
    "motivacio-alapfogalmai-es-szuksegletek": {
        "scenario": "egy call centerben a vezető azt látja, hogy ugyanaz a jutalom az egyik embert felhúzza, a másikat közömbösen hagyja",
        "sampleQuestion": "Mi a motiváció, és hogyan kapcsolódik az egyéni teljesítményhez a környezet és a képesség mellett?",
        "commonTrap": "A motivációt összekeveri a puszta ösztönzéssel vagy jutalmazással.",
        "examFocus": [
            "tudd a teljesítmény három tényezőjét együtt kezelni",
            "emeld ki a szükséglet mint belső feszültség szerepét",
            "kösd a témát a későbbi motivációs elméletekhez",
        ],
    },
    "maslow-szukseglethierarchia": {
        "scenario": "egy nagyvállalat új juttatási és fejlesztési csomagot tervez különböző munkatársi csoportoknak",
        "sampleQuestion": "Mi Maslow szükséglethierarchiájának logikája, és milyen korlátokkal kell kezelni a modellt?",
        "commonTrap": "Mechanikusan kezeli a sorrendet, és nem mondja ki, hogy a valóságban a szintek keveredhetnek.",
        "examFocus": [
            "tudd helyesen felsorolni az öt szintet",
            "magyarázd el, mire jó a modell vezetői szemmel",
            "ne felejtsd el a kritikát sem megemlíteni",
        ],
    },
    "alderfer-erg-elmelet": {
        "scenario": "egy tanácsadó cégnél a munkatárs egyszerre akar fizetésemelést, jobb csapatkapcsolatot és fejlődési lehetőséget",
        "sampleQuestion": "Miben tér el Alderfer ERG-modellje Maslow rendszerétől, és mit jelent a frusztráció-visszalépés elve?",
        "commonTrap": "Csak annyit mond, hogy három szint van, de nem magyarázza a rugalmasabb működést.",
        "examFocus": [
            "tudd a három kategóriát helyesen azonosítani",
            "emeld ki, hogy több szükséglet egyszerre is aktív lehet",
            "magyarázd el a visszalépés logikáját rövid példával",
        ],
    },
    "herzberg-kettenyezos-modell": {
        "scenario": "egy gyárban megemelik a béreket, mégis ugyanúgy alacsony marad a belső lelkesedés",
        "sampleQuestion": "Mi a különbség Herzberg higiéniás tényezői és motivátorai között, és milyen vezetői következménye van ennek?",
        "commonTrap": "A hallgató azt állítja, hogy a jó fizetés önmagában motivátor minden helyzetben.",
        "examFocus": [
            "különítsd el az elégedetlenség csökkentését a valódi motiválástól",
            "tudd példával megmutatni a motivátorok szerepét",
            "kösd a modellt munkakörtervezéshez és felhatalmazáshoz",
        ],
    },
    "mcgregor-x-es-y-emberkepe": {
        "scenario": "egy új részlegvezető szigorú ellenőrzéssel kezd, mert nem bízik a csapat önállóságában",
        "sampleQuestion": "Mit jelent McGregor X és Y emberképe, és hogyan hat a vezetői gyakorlatra?",
        "commonTrap": "Az X és Y emberképet a dolgozók személyiségének, nem pedig vezetői alapfeltevésnek kezeli.",
        "examFocus": [
            "mondd ki, hogy emberképről és nem objektív tényről van szó",
            "kapcsold a feltételezéseket irányítási stílushoz",
            "emeld ki az önbeteljesítő hatás lehetőségét",
        ],
    },
    "hunt-celstruktura-modell": {
        "scenario": "egy projektcsapatban az egyik tag stabilitást, a másik hatalmat, a harmadik önállóságot keres",
        "sampleQuestion": "Miért tekinti Hunt a motivációt dinamikus célstruktúrának, és mit jelent ez vezetői szempontból?",
        "commonTrap": "Újabb hierarchiának állítja be a modellt, pedig éppen a rugalmassága a lényege.",
        "examFocus": [
            "tudd a fő célterületeket megnevezni",
            "mutasd meg, hogy a célok egyszerre is jelen lehetnek",
            "kösd a modellt személyre szabott motiválási döntésekhez",
        ],
    },
    "lewin-vezetesi-stilusai": {
        "scenario": "egy üzletnyitási projektben a vezető autokratikus, demokratikus és megengedő működést is kipróbál a csapattal",
        "sampleQuestion": "Melyek Lewin vezetési stílusai, és hogyan hatnak a teljesítményre, a hangulatra és a kreativitásra?",
        "commonTrap": "Csak a teljesítményszázalékokat mondja, de nem magyarázza a csoportlégkör és a vezetőfüggés következményeit.",
        "examFocus": [
            "tudd mindhárom stílus fő jegyét megkülönböztetni",
            "emeld ki, hogy a rövid távú output nem minden",
            "kapcsold a stílusokat a csoport működési minőségéhez",
        ],
    },
    "hersey-blanchard-szituativ-leadership": {
        "scenario": "egy újonnan belépett munkatárs lelkes, de tapasztalatlan, míg egy másik tapasztalt, de motiválatlan",
        "sampleQuestion": "Hogyan működik a szituatív leadership, és mikor célszerű diktáló, eladó, résztvevő vagy delegáló stílust alkalmazni?",
        "commonTrap": "A stílusokat önmagukban magolja be, és nem köti őket a beosztott érettségéhez.",
        "examFocus": [
            "értsd az érettség két dimenzióját: képesség és hajlandóság",
            "tudd párosítani a helyzeteket a stílusokkal",
            "hangsúlyozd a vezetői rugalmasságot",
        ],
    },
    "kommunikacio-modellje-es-iranyai": {
        "scenario": "egy szolgáltató központban félreértett e-mail, elakadt visszajelzés és gyenge horizontális egyeztetés okoz hibákat",
        "sampleQuestion": "Hogyan épül fel a kommunikáció klasszikus modellje, és milyen irányokban áramlik a kommunikáció a szervezetben?",
        "commonTrap": "Csak a csatornákat sorolja, és nem beszél a zajról vagy a visszacsatolás szerepéről.",
        "examFocus": [
            "tudd végigmondani a kommunikációs folyamat elemeit",
            "különítsd el a lefelé, felfelé és horizontális irányt",
            "mutasd meg, hogy a kommunikáció minden vezetési funkció alapja",
        ],
    },
    "informalis-kommunikacio-es-szervezeti-kapcsolatok": {
        "scenario": "egy vállalatnál gyorsabban terjed a folyosói információ, mint a hivatalos vezetői tájékoztatás",
        "sampleQuestion": "Mi az informális kommunikáció szerepe a szervezetben, és hogyan viszonyul a formális kommunikációhoz?",
        "commonTrap": "Az informális kommunikációt puszta pletykának minősíti, és nem látja a pozitív információs szerepét.",
        "examFocus": [
            "magyarázd el, miért gyors és miért nehezen szabályozható",
            "mutasd meg, hogy a jó vezető információforrásként is használja",
            "kapcsold a témát bizalomhoz és szervezeti hangulathoz",
        ],
    },
    "csoportok-csapatok-es-szerepek": {
        "scenario": "egy projektcsapatban egyes tagok szerveznek, mások ötletelnek, megint mások a belső kohéziót tartják fenn",
        "sampleQuestion": "Mitől lesz valami csoport, milyen csoporttípusok léteznek, és miért fontosak a csoportszerepek?",
        "commonTrap": "A hallgató csak definíciót mond, de nem mutatja meg a szerepek és normák működését.",
        "examFocus": [
            "különítsd el a formális és az informális csoportokat",
            "mutasd meg a rendszeres interakció és a közös cél szerepét",
            "kapcsold a témát csapatműködéshez és vezetői feladatokhoz",
        ],
    },
    "kontroll-folyamat-tipusok-es-controlling": {
        "scenario": "egy többszintű vállalatnál a felső vezetés stratégiát ellenőriz, az üzletágak pénzügyi célokat követnek, a műszakvezető pedig napi feladatot mér",
        "sampleQuestion": "Mi a kontroll folyamata, melyek a kontrolltípusok és hogyan különül el egymástól a stratégiai, menedzsment- és feladatkontroll?",
        "commonTrap": "A hallgató csak az ellenőrzést hangsúlyozza, de nem mondja el a standardképzés és a beavatkozás szerepét.",
        "examFocus": [
            "tudd a kontrollfolyamat teljes lépéssorát",
            "különítsd el a piaci, bürokratikus és klánkontroll alkalmazási helyzetét",
            "magyarázd el, hogy a controlling információs eszközrendszer, nem önálló vezetési funkció",
        ],
    },
}

DEFAULT_EXAM_FOCUS = [
    "a fogalom definíciója mellett az összefüggést is tudd elmagyarázni",
    "kösd a választ vezetői vagy szervezeti példához",
    "figyelj arra, mivel szokták összekeverni a témát",
]

EXPLANATION_TEMPLATES = [
    "Vizsgán ezt a pontot nem elég felsorolni: azt kell megmutatnod, hogy {point}. A biztos válaszhoz mindig kapcsolj hozzá egy vezetői következményt is: {focus}.",
    "Ennél a kulcspontnál az összefüggés a fontos. A lényege, hogy {point}, és ebből a gyakorlatban valamilyen döntési vagy szervezési következmény adódik. Vizsgán erre szoktak ráfordulni: {focus}.",
    "Ezt a tételmondataid közé érdemes tenni, mert definícióból könnyen összehasonlító kérdés lesz. A helyes magyarázat kulcsa, hogy {point}, és ezt a témád fő logikájával együtt mondd el: {focus}.",
    "Ha ezt a pontot röviden kell kifejtened, akkor a magmondata az legyen, hogy {point}. Utána egy fél mondatban tedd hozzá, miért számít ez vizsgán: {focus}.",
]

EXAMPLE_TEMPLATES = [
    "Példa: {scenario}. Ilyenkor ez a szempont abban jelenik meg, hogy a vezető nem rutinból dönt, hanem abból indul ki, hogy {point}.",
    "Példa: {scenario}. Ha ezt a pontot figyelmen kívül hagyják, a működés elsőre rendezettnek tűnhet, de később koordinációs, teljesítmény- vagy motivációs zavar jelenik meg.",
    "Példa: {scenario}. A gyakorlatban ez ott látszik, hogy a vezető a döntéseit ehhez a logikához igazítja, különben a csapat vagy a szervezet rossz irányba indul.",
    "Példa: {scenario}. Vizsgahelyzetben is jó példa, ha megmutatod: ez a pont nem elméleti dísz, hanem konkrétan befolyásolja, hogyan terveznek, szerveznek vagy ellenőriznek.",
]

ADVANTAGE_TEMPLATES = [
    "Segíti az egyértelműbb vezetői döntést, mert láthatóvá teszi, hogy {point}.",
    "Javítja az összehangolást, mert a szereplők könnyebben értik, hogy {focus}.",
    "Erősíti a teljesítményt és a számonkérhetőséget, ha a gyakorlatban is abból indulnak ki, hogy {point}.",
    "Könnyebbé teszi az erőforrások elosztását és a prioritások kijelölését olyan helyzetben is, mint {scenario}.",
]

DISADVANTAGE_TEMPLATES = [
    "Túl merevvé válhat a működés, ha minden helyzetben leegyszerűsítve csak arra hivatkoznak, hogy {point}.",
    "Több egyeztetést és vezetői figyelmet igényel, különösen akkor, amikor {scenario}.",
    "Félreértésekhez vagy rossz döntéshez vezethet, ha a csapat nem érti pontosan, hogy {focus}.",
    "Vizsgán és gyakorlatban is hibás következtetéshez vezethet, ha {common_trap}.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Vizsgafelkészítő témaköri JSON építése a blueprintből, a jegyzetekből és opcionális OCR-kimenetből."
    )
    parser.add_argument(
        "--blueprint",
        type=Path,
        default=ROOT / "data" / "topic_blueprint.json",
        help="A kézzel gondozott témaköri blueprint JSON útvonala.",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="A kiegészítő tananyagokat tartalmazó mappa.",
    )
    parser.add_argument(
        "--ocr-path",
        type=Path,
        default=ROOT / "output" / "book-ocr.json",
        help="Opcionális OCR JSON. Ha nem létezik, a builder nélküle is lefut.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "topics.generated.json",
        help="A létrejövő, validált témaköri adatfájl.",
    )
    return parser.parse_args()


def normalize_text(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_search_text(text: str) -> str:
    stripped = "".join(
        ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch)
    )
    stripped = stripped.lower()
    stripped = re.sub(r"[^a-z0-9]+", " ", stripped)
    return re.sub(r"\s+", " ", stripped).strip()


def lower_first(text: str) -> str:
    if not text:
        return text
    return text[0].lower() + text[1:]


def trim_sentence(text: str) -> str:
    return normalize_text(text).rstrip(".")


def build_list_points(templates: list[str], *, point: str, focus: str, scenario: str, common_trap: str) -> list[str]:
    items: list[str] = []
    for template in templates:
        text = normalize_text(
            template.format(
                point=lower_first(trim_sentence(point)),
                focus=lower_first(trim_sentence(focus)),
                scenario=lower_first(trim_sentence(scenario)),
                common_trap=lower_first(trim_sentence(common_trap)),
            )
        )
        items.append(text)
        if len(items) == 3:
            break
    return items


def extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml").decode("utf-8", errors="ignore")
    text = re.sub(r"</w:p>", "\n", xml)
    text = re.sub(r"<[^>]+>", "", text)
    return normalize_text(text)


def extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    return normalize_text("\n\n".join(pages))


def collect_supporting_files(source_dir: Path) -> list[Path]:
    selected: list[Path] = []
    for path in sorted(source_dir.iterdir(), key=lambda item: item.name.lower()):
        if path.name.startswith("~$"):
            continue
        lower_name = path.name.lower()
        if path.suffix.lower() == ".docx" and path.name.startswith("1-4."):
            selected.append(path)
            continue
        if path.suffix.lower() != ".pdf":
            continue
        if (
            path.name.startswith("1-4.")
            or path.name.startswith("Előadás 1-3")
            or path.name.startswith("Első küldetés")
            or path.name.startswith("Második Küldetés")
            or path.name.startswith("VezSzerv_")
            or "teszt" in lower_name
        ):
            selected.append(path)
    return selected


def resolve_book_pdf(source_dir: Path) -> Path | None:
    candidates = [
        path
        for path in source_dir.iterdir()
        if path.suffix.lower() == ".pdf"
        and not path.name.startswith("~$")
        and path.name.startswith("VezSzerv Teljes")
    ]
    if not candidates:
        return None

    candidates.sort(
        key=lambda path: (
            0 if path.name.endswith("A.pdf") else 1,
            path.name.lower(),
        )
    )
    return candidates[0]


def resolve_shareable_book_url(book_path: Path | None) -> str | None:
    env_url = normalize_text(os.environ.get("VEZSZERV_BOOK_SHARE_URL", ""))
    if env_url.startswith("http://") or env_url.startswith("https://"):
        return env_url

    if book_path and book_path.name.startswith("VezSzerv Teljes"):
        return DEFAULT_BOOK_SHARE_URL

    if not book_path:
        return None

    repo_book = ROOT / "book" / book_path.name
    if repo_book.exists():
        return f"./book/{quote(book_path.name)}"

    return None


def load_supporting_corpus(source_dir: Path) -> tuple[list[dict], str]:
    sources: list[dict] = []
    combined_texts: list[str] = []

    for source_path in collect_supporting_files(source_dir):
        if source_path.suffix.lower() == ".docx":
            text = extract_docx_text(source_path)
        else:
            text = extract_pdf_text(source_path)
        sources.append(
            {
                "name": source_path.name,
                "path": str(source_path),
                "charCount": len(text),
            }
        )
        combined_texts.append(text)

    return sources, normalize_text("\n\n".join(combined_texts))


def load_ocr_corpus(ocr_path: Path) -> tuple[int, str]:
    if not ocr_path.exists():
        return 0, ""

    payload = json.loads(ocr_path.read_text(encoding="utf-8"))
    pages = payload.get("pages", []) if isinstance(payload, dict) else []
    texts = [normalize_text(page.get("text", "")) for page in pages]
    return len(pages), normalize_text("\n\n".join(texts))


def keyword_match_count(keyword: str, corpus: str) -> int:
    if not corpus:
        return 0
    term = normalize_search_text(keyword)
    haystack = normalize_search_text(corpus)
    if not term:
        return 0
    return haystack.count(term)


def build_topic_diagnostics(topic: dict, support_corpus: str, ocr_corpus: str) -> dict:
    support_hits = {
        keyword: keyword_match_count(keyword, support_corpus)
        for keyword in topic["keywords"]
    }
    ocr_hits = {
        keyword: keyword_match_count(keyword, ocr_corpus)
        for keyword in topic["keywords"]
    }
    return {
        "supportingHits": support_hits,
        "ocrHits": ocr_hits,
        "supportingTotal": sum(support_hits.values()),
        "ocrTotal": sum(ocr_hits.values()),
    }


def build_study_cards(topic: dict, guide: dict) -> list[dict]:
    focus_items = guide.get("examFocus") or DEFAULT_EXAM_FOCUS
    scenario = guide["scenario"]
    sample_question = guide["sampleQuestion"]
    common_trap = guide["commonTrap"]

    cards: list[dict] = []
    for index, point in enumerate(topic["keyPoints"], start=1):
        point_core = trim_sentence(point)
        focus = focus_items[(index - 1) % len(focus_items)]
        explanation_template = EXPLANATION_TEMPLATES[(index - 1) % len(EXPLANATION_TEMPLATES)]
        example_template = EXAMPLE_TEMPLATES[(index - 1) % len(EXAMPLE_TEMPLATES)]
        explanation = explanation_template.format(
            point=lower_first(point_core),
            focus=lower_first(trim_sentence(focus)),
        )
        example = example_template.format(
            scenario=scenario,
            point=lower_first(point_core),
        )
        advantages = build_list_points(
            ADVANTAGE_TEMPLATES,
            point=point_core,
            focus=focus,
            scenario=scenario,
            common_trap=common_trap,
        )
        disadvantages = build_list_points(
            DISADVANTAGE_TEMPLATES,
            point=point_core,
            focus=focus,
            scenario=scenario,
            common_trap=common_trap,
        )
        cards.append(
            {
                "id": index,
                "title": normalize_text(point),
                "explanation": normalize_text(explanation),
                "example": normalize_text(example),
                "advantages": advantages,
                "disadvantages": disadvantages,
                "examTip": normalize_text(
                    f"Vizsgatipp: gondold végig ezt a kérdést is: {sample_question}"
                ),
                "commonTrap": normalize_text(
                    f"Gyakori hiba: {common_trap}"
                ),
            }
        )
    return cards


def validate_topics(topics: list[dict]) -> None:
    if len(topics) < 30:
        raise ValueError(
            f"Legalább 30 témára számítottam, de csak {len(topics)} van a blueprintben."
        )

    ids = [topic["id"] for topic in topics]
    if ids != list(range(1, len(topics) + 1)):
        raise ValueError("A témák azonosítóinak 1-től induló, folyamatos sorozatot kell alkotniuk.")

    slugs = [topic["slug"] for topic in topics]
    if len(slugs) != len(set(slugs)):
        raise ValueError("Minden slugnak egyedinek kell lennie.")

    valid_ids = set(ids)
    for topic in topics:
        if topic["slug"] not in TOPIC_STUDY_GUIDES:
            raise ValueError(f"Hiányzik study guide a következő témához: {topic['slug']}")
        if not topic["overview"].strip():
            raise ValueError(f"Üres overview mező: #{topic['id']} {topic['title']}")
        if not (5 <= len(topic["keyPoints"]) <= 8):
            raise ValueError(
                f"A keyPoints elemszámának 5 és 8 között kell lennie: #{topic['id']}"
            )
        if not (4 <= len(topic["keywords"]) <= 8):
            raise ValueError(
                f"A keywords elemszámának 4 és 8 között kell lennie: #{topic['id']}"
            )
        if not (2 <= len(topic["relatedTopicIds"]) <= 4):
            raise ValueError(
                f"A relatedTopicIds elemszámának 2 és 4 között kell lennie: #{topic['id']}"
            )
        for related_id in topic["relatedTopicIds"]:
            if related_id not in valid_ids:
                raise ValueError(
                    f"Érvénytelen relatedTopicId {related_id} a következő témánál: #{topic['id']}"
                )
            if related_id == topic["id"]:
                raise ValueError(f"Egy téma nem hivatkozhat önmagára: #{topic['id']}")


def load_blueprint(path: Path) -> list[dict]:
    topics = json.loads(path.read_text(encoding="utf-8"))
    for topic in topics:
        topic["module"] = normalize_text(topic["module"])
        topic["title"] = normalize_text(topic["title"])
        topic["overview"] = normalize_text(topic["overview"])
        topic["keyPoints"] = [normalize_text(point) for point in topic["keyPoints"]]
        topic["keywords"] = [normalize_text(keyword) for keyword in topic["keywords"]]
    return topics


def enrich_topics(topics: list[dict]) -> list[dict]:
    enriched: list[dict] = []
    for topic in topics:
        guide = TOPIC_STUDY_GUIDES[topic["slug"]]
        topic_copy = dict(topic)
        topic_copy["examFocus"] = [normalize_text(item) for item in guide["examFocus"]]
        topic_copy["sampleQuestion"] = normalize_text(guide["sampleQuestion"])
        topic_copy["commonTrap"] = normalize_text(guide["commonTrap"])
        topic_copy["scenario"] = normalize_text(guide["scenario"])
        topic_copy["studyCards"] = build_study_cards(topic_copy, guide)
        topic_copy["studyCardCount"] = len(topic_copy["studyCards"])
        enriched.append(topic_copy)
    return enriched


def validate_enriched_topics(topics: list[dict]) -> None:
    for topic in topics:
        for card in topic.get("studyCards", []):
            advantages = card.get("advantages") or []
            disadvantages = card.get("disadvantages") or []
            if not (3 <= len(advantages) <= 7):
                raise ValueError(
                    f"A studyCard advantages elemszámának 3 és 7 között kell lennie: #{topic['id']} / {card['id']}"
                )
            if not (3 <= len(disadvantages) <= 7):
                raise ValueError(
                    f"A studyCard disadvantages elemszámának 3 és 7 között kell lennie: #{topic['id']} / {card['id']}"
                )


def build_payload(
    topics: list[dict],
    source_dir: Path,
    support_sources: list[dict],
    support_corpus: str,
    ocr_page_count: int,
    ocr_corpus: str,
    ocr_path: Path,
    book_path: Path | None,
    book_share_url: str | None,
) -> dict:
    diagnostics = {
        str(topic["id"]): build_topic_diagnostics(topic, support_corpus, ocr_corpus)
        for topic in topics
    }
    low_coverage = [
        {"id": topic["id"], "title": topic["title"]}
        for topic in topics
        if diagnostics[str(topic["id"])]["supportingTotal"] == 0
        and diagnostics[str(topic["id"])]["ocrTotal"] == 0
    ]

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceFolder": str(source_dir),
        "ocrPath": str(ocr_path) if ocr_path.exists() else None,
        "bookPath": str(book_path) if book_path else None,
        "bookUrl": book_path.as_uri() if book_path else None,
        "bookShareUrl": book_share_url,
        "supportingSources": support_sources,
        "ocrPageCount": ocr_page_count,
        "diagnostics": {
            "topicCount": len(topics),
            "lowCoverageTopics": low_coverage,
        },
        "topics": topics,
    }


def main() -> None:
    args = parse_args()
    topics = load_blueprint(args.blueprint)
    validate_topics(topics)
    topics = enrich_topics(topics)
    validate_enriched_topics(topics)

    support_sources, support_corpus = load_supporting_corpus(args.source_dir)
    ocr_page_count, ocr_corpus = load_ocr_corpus(args.ocr_path)
    book_path = resolve_book_pdf(args.source_dir)
    book_share_url = resolve_shareable_book_url(book_path)

    payload = build_payload(
        topics=topics,
        source_dir=args.source_dir,
        support_sources=support_sources,
        support_corpus=support_corpus,
        ocr_page_count=ocr_page_count,
        ocr_corpus=ocr_corpus,
        ocr_path=args.ocr_path,
        book_path=book_path,
        book_share_url=book_share_url,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Vizsgafelkészítő témaköri JSON elkészült: {args.output}")
    print(f"Betöltött kiegészítő források: {len(support_sources)}")
    print(f"Betöltött OCR-oldalak: {ocr_page_count}")
    if book_path:
        print(f"Könyv PDF: {book_path}")
    if book_share_url:
        print(f"Megosztható könyv URL: {book_share_url}")
    if payload["diagnostics"]["lowCoverageTopics"]:
        missing = ", ".join(
            f"#{item['id']}" for item in payload["diagnostics"]["lowCoverageTopics"]
        )
        print(f"Figyelem: alacsony forrásfedettségű témák: {missing}")


if __name__ == "__main__":
    main()
