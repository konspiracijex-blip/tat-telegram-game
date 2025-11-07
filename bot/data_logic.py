# Definisanje celog testa: Slike, odgovori i bodovi
# Koristi se format: {pitanje_broj: {odgovor_oznaka: bodovi}}

# NAPOMENA: Bodovi (1-4) su trenutno placeholderi i mogu se prilagoditi Vašem sistemu bodovanja!

SCORING_SCHEMA = {
    1: {'A': 4, 'B': 1, 'C': 3, 'D': 2},
    2: {'A': 1, 'B': 4, 'C': 2, 'D': 3},
    3: {'A': 3, 'B': 2, 'C': 4, 'D': 1},
    4: {'A': 2, 'B': 3, 'C': 1, 'D': 4},
    5: {'A': 4, 'B': 1, 'C': 3, 'D': 2},
    6: {'A': 1, 'B': 4, 'C': 2, 'D': 3},
    7: {'A': 3, 'B': 2, 'C': 4, 'D': 1},
    8: {'A': 2, 'B': 3, 'C': 1, 'D': 4},
    9: {'A': 4, 'B': 1, 'C': 3, 'D': 2},
    10: {'A': 1, 'B': 4, 'C': 2, 'D': 3},
}

MAX_SCORE = 4 * 10 # 40
MIN_SCORE = 1 * 10 # 10

# Tekstovi za pitanja koji se salju WebApp-u
# WebApp koristi ove podatke za prikaz
WEBAPP_QUESTIONS = [
    {'q': 1, 'slika': 'placeholder/slika_01.jpg', 'tekst': 'Šta vidite kada pogledate ovu staru kuću?', 'odgovori': {'A': 'Napušteno, ali puno uspomena.', 'B': 'Prazan, propadajući objekat.', 'C': 'Mesto koje čeka novu priču.', 'D': 'Samo prolaznost vremena.'}},
    {'q': 2, 'slika': 'placeholder/slika_02.jpg', 'tekst': 'Ova planina Vas podseća na:', 'odgovori': {'A': 'Prepreku koju treba zaobići.', 'B': 'Izazov koji treba savladati.', 'C': 'Miran, stabilan oslonac.', 'D': 'Simbol večnosti.'}},
    {'q': 3, 'slika': 'placeholder/slika_03.jpg', 'tekst': 'Ova scena u kafiću Vas čini:', 'odgovori': {'A': 'Radoznalim, želite da se pridružite.', 'B': 'Ravndušnim.', 'C': 'Nestrpljivim da odete.', 'D': 'Opuštenim i smirenim.'}},
    {'q': 4, 'slika': 'placeholder/slika_04.jpg', 'tekst': 'Kakvo osećanje dominira ovom apstraktnom slikom?', 'odgovori': {'A': 'Haos i anksioznost.', 'B': 'Energičnost i kretanje.', 'C': 'Tuga i melanholija.', 'D': 'Neizvesnost i tišina.'}},
    {'q': 5, 'slika': 'placeholder/slika_05.jpg', 'tekst': 'Ovaj lik iz daljine Vas navodi da mislite:', 'odgovori': {'A': 'Ima jasan cilj i ide ka njemu.', 'B': 'Izgubljen je i traži put.', 'C': 'Čeka nekoga ili nešto.', 'D': 'Uživa u samoći.'}},
    {'q': 6, 'slika': 'placeholder/slika_06.jpg', 'tekst': 'Boje na ovom zalasku sunca su:', 'odgovori': {'A': 'Previše dramatične.', 'B': 'Inspirativne i ispunjavajuće.', 'C': 'Uobičajene i svakodnevne.', 'D': 'Tople i umirujuće.'}},
    {'q': 7, 'slika': 'placeholder/slika_07.jpg', 'tekst': 'U ovom hodniku se osećate:', 'odgovori': {'A': 'Klaustrofobično i zarobljeno.', 'B': 'Zaštićeno i sigurno.', 'C': 'Radoznalo, šta je na kraju?', 'D': 'Pomalo izgubljeno.'}},
    {'q': 8, 'slika': 'placeholder/slika_08.jpg', 'tekst': 'Ovaj osmeh Vas navodi da mislite da je osoba:', 'odgovori': {'A': 'Srećna, bez sumnje.', 'B': 'Nešto krije.', 'C': 'Pokušava da Vas impresionira.', 'D': 'Zadovoljna sobom.'}},
    {'q': 9, 'slika': 'placeholder/slika_09.jpg', 'tekst': 'Kakav je Vaš prvi utisak o ovoj osobi?', 'odgovori': {'A': 'Ambiciozna i odlučna.', 'B': 'Blaga i nesigurna.', 'C': 'Sanjalica i emotivna.', 'D': 'Pragmatična i logična.'}},
    {'q': 10, 'slika': 'placeholder/slika_10.jpg', 'tekst': 'Ova šuma u magli izaziva osećaj:', 'odgovori': {'A': 'Misterije i avanture.', 'B': 'Opasnosti i pretnje.', 'C': 'Spokoja i usamljenosti.', 'D': 'Dosade i monotonije.'}},
]

def calculate_score(question_num, answer):
    """Vraca bodove za dati odgovor iz SCORING_SCHEMA."""
    # Vraca 0 ako pitanje ili odgovor nisu pronadjeni
    return SCORING_SCHEMA.get(question_num, {}).get(answer, 0)

def generate_profile(total_score):
    """
    Generise tekstualni profil na osnovu ukupnog broja bodova (10 - 40).
    (Može se koristiti MarkdownV2 za formatiranje u Telegramu)
    """
    
    # Prilagođeno za MarkdownV2: Koristimo * za bold, \n\n za nove paragrafe
    
    if total_score >= 35:
        title = "👑 Vizionar i Strateški Optimista"
        narrative = (
            "Vaš profil ukazuje na izuzetnu sposobnost da interpretirate složene scene sa fokusom na potencijal i budućnost\\. "
            "Ne vidite probleme, već prilike\\. Imate snažnu unutrašnju motivaciju i sklonost ka akciji\\. "
            "Možda previše naginjete idealizaciji, ali Vas to čini neodoljivim vođom\\."
        )
    elif total_score >= 25:
        title = "🧭 Balansirani Istraživač i Posmatrač"
        narrative = (
            "Postigli ste izbalansiran skor, što ukazuje na Vašu sposobnost da situaciju sagledate iz više uglova\\. "
            "Emocionalna inteligencija Vam omogućava da razumete nijanse, dok pragmatičnost osigurava da ostanete čvrsto na zemlji\\. "
            "Uglavnom Vas odlikuje mirna snaga i sposobnost da budete dobar oslonac\\."
        )
    elif total_score >= 15:
        title = "🧐 Oprezni Analitičar i Realista"
        narrative = (
            "Vaša tumačenja su usmerena na realnost i detalje, ponekad na štetu šire slike\\. "
            "Imate tendenciju da stvari vidite onakvima kakve jesu, sa dozom skepticizma\\. "
            "Iako ste pouzdani i temeljni, ponekad Vam nedostaje spontanosti u donošenju odluka\\."
        )
    else:
        title = "💡 Introvertni Posmatrač i Kontemplativac"
        narrative = (
            "Niski skorovi često ukazuju na osobu koja je duboko promišljena, ali koja više vremena provodi u posmatranju nego u interakciji\\. "
            "Možda Vas opterećuju detalji, a emotivna stanja su Vam intenzivna\\. "
            "Potrebno Vam je više vremena da se otvorite, ali kada to učinite, Vaš unutrašnji svet je izuzetno bogat\\."
        )
        
    # Koristimo escape karaktere (\.) jer Telegram MarkdownV2 zahteva escapeovanje tačaka i drugih specijalnih karaktera
    # NAPOMENA: Potrebno je da Bot bude pokrenut sa parse_mode='MarkdownV2'
    return f"✨ *{title}* ✨\n\n{narrative}\n\n_Ukupan skor: {total_score} od {MAX_SCORE} moćnih bodova\\._"

# Funkcija koja se koristi u WebApp index.html (iako je WebApp kodiran statički u ovom MVP-u)
def get_webapp_question_data(question_num):
    """Vraca podatke za jedno pitanje za WebApp (za kasniju dinamicku implementaciju)."""
    for q in WEBAPP_QUESTIONS:
        if q['q'] == question_num:
            return q
    return None
