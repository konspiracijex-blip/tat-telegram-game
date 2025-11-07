import os
import json
import logging
from datetime import datetime
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# Importovanje lokalnih modula
# PAZNJA: Ovi fajlovi moraju postojati u bot/ direktorijumu
from gspread_setup import setup_gspread, create_player_row, update_player_response, get_player_data, delete_player_row, finalize_player_score
from data_logic import calculate_score, generate_profile, WEBAPP_QUESTIONS

# Ucitavanje okruzenjskih varijabli iz .env fajla (ako se pokrece lokalno)
# Na serveru (Render/Heroku), varijable se citaju direktno
load_dotenv()

# Postavljanje logovanja
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- INICIJALIZACIJA GLOBALNIH RESURSA ---

# Ucitavanje tokena iz okruzenjske varijable
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Ime Sheet-a
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "TAT_Igra_Baza")
# URL WebApp-a (morate ga postaviti u .env ili na serveru!)
WEB_APP_URL = os.getenv("WEB_APP_URL") 

# Globalna varijabla za Sheets
gspread_worksheet = None

# --- TELEGRAM HANDLERI (Funkcije za Bot) ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Obradjivanje /start komande, inicijalizuje igru i salje WebApp dugme."""
    global gspread_worksheet
    
    if gspread_worksheet is None:
        await update.message.reply_text("Greška: Bot se nije uspio povezati sa bazom podataka. Proverite JSON ključ.")
        return
    
    if WEB_APP_URL is None:
        await update.message.reply_text("Greška: WebApp URL nije konfigurisan. Ne mogu pokrenuti igru.")
        return

    player_id = update.effective_user.id
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Inicijalizacija reda u Sheets-u
    success = create_player_row(gspread_worksheet, player_id, current_time)
    
    if success:
        logger.info(f"Novi igrac {player_id} inicijalizovan u Sheets-u.")
        
        # 2. Slanje WebApp dugmeta
        webapp_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text="🚀 POKRENI TAT IGRA TEST", 
                # Koristimo WebAppInfo sa postavljenim URL-om
                web_app=WebAppInfo(url=WEB_APP_URL)
            )]
        ])
        
        await update.message.reply_text(
            f"Dobrodošli u TAT IGRA TEST! Molimo Vas da odgovorite na 10 pitanja u WebApp prozoru. \n\n"
            f"Vaši rezultati će biti odmah generisani i poslati ovde.",
            reply_markup=webapp_markup
        )
    else:
        await update.message.reply_text("Greška pri inicijalizaciji igre u bazi podataka. Pokušajte ponovo.")


async def webapp_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Obradjivanje podataka poslanih iz WebApp-a.
    Ovaj handler prima odgovore na pitanja.
    """
    global gspread_worksheet
    
    # Podaci dolaze u update.effective_message.web_app_data.data (JSON string)
    web_app_data = update.effective_message.web_app_data.data
    player_id = update.effective_user.id
    
    try:
        data = json.loads(web_app_data)
        question_num = data.get('pitanje')
        answer = data.get('odgovor')
        
        if not all([question_num, answer]):
            logger.warning(f"Neispravan WebApp data format: {data}")
            return
            
        # 1. Izracunavanje bodova
        points = calculate_score(question_num, answer)
        
        # 2. Azuriranje Sheets-a
        update_success = update_player_response(gspread_worksheet, player_id, question_num, answer, points)
        
        logger.info(f"Igrac {player_id} - Pitanje {question_num}: Odgovor {answer}, Bodovi {points}")

        # 3. Provera da li je poslednje pitanje (10.)
        if question_num == 10 and update_success:
            # Kraj igre! Generisanje profila.
            await generate_and_send_profile(player_id, update)
            
    except Exception as e:
        logger.error(f"GRESKA pri obradi WebApp podataka za ID {player_id}: {e}")

async def generate_and_send_profile(player_id, update: Update):
    """Generise profil, salje ga igracu i brise podatke."""
    
    # 1. Citanje svih podataka
    player_data = get_player_data(gspread_worksheet, player_id)
    
    if not player_data:
        await update.message.reply_text("Greška: Vaši rezultati nisu pronađeni. Proverite da li je baza podataka pravilno postavljena.")
        return

    # 2. Sabiranje bodova iz procitanog reda
    total_score = 0
    # Kolone bodova: B1 je na indeksu 2, B10 na indeksu 20 (u 0-indeksiranom nizu)
    for i in range(2, 21, 2):
        try:
            # Gspread vraca vrednosti kao stringove
            total_score += int(player_data[i] or 0) 
        except ValueError:
            continue

    # 3. Upisivanje ukupnog skora u Sheets (Opcionalno, radi pregleda)
    finalize_player_score(gspread_worksheet, player_id, total_score)

    # 4. Generisanje narativa
    profile_text = generate_profile(total_score)
    
    # 5. Slanje profila igracu
    # Koristimo parse_mode='MarkdownV2' i escape-ujemo specijalne karaktere ako je potrebno
    await update.message.reply_text(profile_text, parse_mode='MarkdownV2')
    
    # 6. BRISANJE PODATAKA (PRIVATNOST I CISTOCA BAZE)
    delete_success = delete_player_row(gspread_worksheet, player_id)
    
    if delete_success:
        logger.info(f"Podaci igraca {player_id} su uspesno obrisani.")
    else:
        logger.warning(f"GRESKA: Podaci igraca {player_id} NISU OBRISANI!")


def main() -> None:
    """Pokretanje bota."""
    global gspread_worksheet
    
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN nije pronadjen. Prekinuta inicijalizacija.")
        return

    # Inicijalizacija Sheets-a pre pokretanja Bota
    gspread_worksheet = setup_gspread(GOOGLE_SHEET_NAME)
    
    if gspread_worksheet is None:
        logger.error("Bot nije mogao da se poveže sa Google Sheets-om. Prekidam.")
        return

    # Kreiranje Application i definisanje Bota
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Dodavanje handler-a za komande
    application.add_handler(CommandHandler("start", start_command))

    # Handler za WebApp podatke
    # Koristimo filters.StatusUpdate.WEB_APP_DATA za hvatanje podataka poslanih iz WebApp-a
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data_handler))
    
    logger.info("Bot je uspešno povezan sa Sheets-om i spreman za rad (Polling Mode).")
    
    # Polling - Bot stalno proverava nove poruke (Idealno za lokalno testiranje)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
