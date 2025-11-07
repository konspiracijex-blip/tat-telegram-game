import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import logging

logger = logging.getLogger(__name__)

# 1. FUNKCIJA ZA POVEZIVANJE
def setup_gspread(sheet_name):
    """
    Inicijalizuje vezu sa Google Sheets-om koristeći Service Account Credentials.
    Izmenjeno: Čita creds direktno iz google_creds.json fajla (za PythonAnywhere)
    """
    try:
        # PRIVREMENO: Citanje iz lokalnog fajla na PythonAnywhere
        try:
            with open("google_creds.json", "r") as f:
                creds_dict = json.load(f)
        except FileNotFoundError:
            logger.error("GRESKA: google_creds.json nije pronadjen. Proverite da li fajl postoji u bot/ folderu.")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"GRESKA: JSON format credentials-a u google_creds.json je neispravan. Detalji: {e}")
            return None
            
        # Obim (Scope) dozvola koje su Botu potrebne
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Autentifikacija
        creds = ServiceAccountCredentials.from_json(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Otvaranje tabele po imenu
        sheet = client.open(sheet_name)
        
        # Otvaranje taba "Igraci" 
        worksheet = sheet.worksheet("Igraci")
        
        logger.info(f"Uspesno povezano sa Google Sheet: {sheet_name}/Igraci")
        return worksheet
        
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error(f"GRESKA: Google Sheet '{sheet_name}' nije pronadjen. Proverite ime i dozvole (Deljenje).")
        return None
    except gspread.exceptions.WorksheetNotFound:
        logger.error(f"GRESKA: Tab 'Igraci' nije pronadjen unutar Sheets-a. Proverite da li je ime taba tacno.")
        return None
    except Exception as e:
        logger.error(f"GRESKA pri povezivanju sa Google Sheets: {e}")
        return None

# 2. FUNKCIJE ZA CRUD OPERACIJE

def create_player_row(worksheet, player_id, timestamp):
    """Kreira novi red za igraca."""
    # Definisemo prazan red sa inicijalnim podacima: ID i Vreme.
    # Ukupno 23 kolone: ID, P1, B1, P2, B2, ..., P10, B10, Ukupno, Datum/vreme
    
    # Inicijalizacija 20 praznih kolona za Pitanja/Bodove
    empty_data = [''] * 20 
    
    # Redosled kolona: [ID, P1, B1, ..., P10, B10, Ukupno, Datum/vreme]
    row_data = [str(player_id)] + empty_data + [''] + [timestamp]
    
    try:
        worksheet.append_row(row_data)
        return True
    except Exception as e:
        logger.error(f"GRESKA pri kreiranju reda {player_id}: {e}")
        return False

def update_player_response(worksheet, player_id, question_num, answer, points):
    """Azurira odgovor i bodove za odredjeno pitanje."""
    try:
        # 1. Pronalazimo red (Trazenje po prvoj koloni - ID igraca)
        cell = worksheet.find(str(player_id), in_column=1)
        row_index = cell.row

        # 2. Racunanje indeksa kolone
        # Pitanje N: Ans. Col 1 + (N*2 - 1), Bod Col 1 + (N*2)
        ans_col = 1 + (question_num * 2) - 1 
        bod_col = 1 + (question_num * 2)     
        
        # 3. Azuriranje celija 
        worksheet.update_cell(row_index, ans_col, answer)
        worksheet.update_cell(row_index, bod_col, str(points))
        
        return True
    except gspread.exceptions.CellNotFound:
        logger.warning(f"Igrac sa ID {player_id} nije pronadjen za azuriranje.")
        return False
    except Exception as e:
        logger.error(f"GRESKA pri azuriranju odgovora za {player_id}: {e}")
        return False

def get_player_data(worksheet, player_id):
    """Vraca sve podatke za igraca (za bodovanje)."""
    try:
        cell = worksheet.find(str(player_id), in_column=1)
        row_data = worksheet.row_values(cell.row) 
        return row_data
    except gspread.exceptions.CellNotFound:
        return None
    
def delete_player_row(worksheet, player_id):
    """Brise red igraca nakon generisanja profila."""
    try:
        cell = worksheet.find(str(player_id), in_column=1)
        worksheet.delete_rows(cell.row)
        return True
    except gspread.exceptions.CellNotFound:
        logger.warning(f"Igrac sa ID {player_id} nije pronadjen za brisanje (vec obrisan?).")
        return False
    except Exception as e:
        logger.error(f"GRESKA pri brisanju reda za {player_id}: {e}")
        return False

def finalize_player_score(worksheet, player_id, total_score):
    """Upisuje ukupan skor u kolonu 'Ukupno' (22. kolona)."""
    try:
        cell = worksheet.find(str(player_id), in_column=1)
        row_index = cell.row
        
        TOTAL_SCORE_COL = 22
        
        worksheet.update_cell(row_index, TOTAL_SCORE_COL, str(total_score))
        return True
    except gspread.exceptions.CellNotFound:
        return False
