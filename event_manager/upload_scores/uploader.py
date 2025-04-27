import os
import pymongo
import logging
import sys
from pymongo import errors
from tqdm import tqdm
import time

from event_manager.upload_scores.models import PlayerEntry
from event_manager.upload_scores.utils import load_csv, load_google_sheet
from event_manager.upload_scores.exceptions import DatabaseConnectionError, InvalidInputError
from event_manager.upload_scores.config import load_config, check_env_vars

try:
    from colorama import Fore, Style, init as colorama_init

    colorama_init(autoreset=True)
except ImportError:
    Fore = Style = type('ColorStub', (),
                        {'RESET_ALL': '', 'YELLOW': '', 'CYAN': '', 'GREEN': '', 'MAGENTA': '', 'BLUE': '',
                         'WHITE': ''})()
    colorama_init = lambda *args, **kwargs: None

from logging.handlers import TimedRotatingFileHandler

file_handler = TimedRotatingFileHandler("logs/event_upload.log", when="midnight", backupCount=7, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), file_handler]
)


def validate_entry(entry):
    player_name = entry.get('playerName')
    player_id = entry.get('playerId')
    total_entries = entry.get('totalEntries')

    if not isinstance(player_name, str) or not player_name.strip():
        raise InvalidInputError(f"Invalid playerName: {player_name}")
    if not isinstance(player_id, (str, int)):
        raise InvalidInputError(f"Invalid playerId: {player_id}")
    if not isinstance(total_entries, int) or total_entries < 0:
        raise InvalidInputError(f"Invalid totalEntries: {total_entries}")


def display_preview(processed_data):
    logging.info("[DRY-RUN] Preview of first entries:")
    for player in processed_data[:3]:
        example_groups = ", ".join(entry['groupName'] for entry in player['entries'][:3])
        preview_line = (
            f"- {Fore.LIGHTBLUE_EX}{player['playerName']}{Style.RESET_ALL} "
            f"(ID: {Fore.LIGHTBLACK_EX}{player['playerId']}{Style.RESET_ALL}), "
            f"Total Entries: {player['totalEntries']}, "
            f"Example Groups: {example_groups}"
        )
        logging.info(preview_line)


def main(dry_run=False):
    load_config()
    check_env_vars()
    start_time = time.time()

    try:
        client = pymongo.MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)
        client.server_info()
    except pymongo.errors.ServerSelectionTimeoutError:
        logging.error("Database connection failed.")
        raise DatabaseConnectionError("Could not connect to MongoDB.") from None

    db = client.get_default_database()
    tournament_collection = db["tournament"]

    if os.getenv("USE_GOOGLE_SHEETS", "false").lower() == "true":
        records = load_google_sheet(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"), os.getenv("SPREADSHEET_ID"))
    else:
        records = load_csv(os.getenv("CSV_PATH"))

    processed_data = []
    validation_errors = []

    records_iter = tqdm(records, desc="Processing players", unit="player") if len(records) >= 250 else records
    for row in records_iter:
        if not row.get('playerId') and not row.get('playerName'):
            continue

        raw_player_id = row.get('playerId')

        if raw_player_id is None or str(raw_player_id).strip() == '':
            validation_errors.append("Validation error: playerId is missing or empty.")
            continue

        try:
            player_id_int = int(raw_player_id)
        except ValueError:
            validation_errors.append(f"Validation error: playerId '{raw_player_id}' is not a valid integer.")
            continue

        if len(str(player_id_int)) < 10:
            logging.warning(
                f"Validation warning: playerId '{player_id_int}' looks suspiciously short, but will be imported.")

        try:
            validated_entry = PlayerEntry(
                playerName=row.get('playerName'),
                playerId=player_id_int,
                totalEntries=int(row.get('totalEntries', 0) or 0)
            )
        except ValueError as e:
            validation_errors.append(f"Validation error for playerId {player_id_int}: {str(e)}")
            continue

        player_name = validated_entry.playerName
        player_id = validated_entry.playerId
        total_entries = validated_entry.totalEntries

        entries = []
        for i in range(1, 41):
            group_name = row.get(f'Entry {i}')
            score = int(row.get(f'Points {i}', 0) or 0)
            if group_name:
                entries.append({
                    'groupName': group_name,
                    'score': score,
                    'sub': group_name.startswith('Sub')
                })

        processed_data.append({
            'playerName': player_name,
            'playerId': player_id,
            'entries': entries,
            'totalEntries': total_entries
        })

    if validation_errors:
        logging.warning(Fore.RED + f"❌ Validation completed with {len(validation_errors)} error(s).")
        for error_msg in validation_errors:
            logging.warning(Fore.YELLOW + error_msg)
    else:
        logging.info(Fore.GREEN + "✅ Validation completed without any errors.")

    logging.info(Fore.GREEN + f"✅ Successfully processed {len(processed_data)} valid player(s).")
    if validation_errors:
        logging.info(Fore.YELLOW + f"⚠️ Skipped {len(validation_errors)} invalid player(s) due to validation errors.")
    elapsed_time = time.time() - start_time
    logging.info(Fore.CYAN + f"🏁 Done in {elapsed_time:.2f} seconds.")
    if dry_run:
        display_preview(processed_data)
    else:
        try:
            tournament_collection.delete_many({})
            if processed_data:
                tournament_collection.bulk_write([
                    pymongo.UpdateOne(
                        {'playerId': player['playerId']},
                        {'$set': player},
                        upsert=True
                    )
                    for player in processed_data
                ])
            logging.info(f"Updated {len(processed_data)} entries successfully.")

        except pymongo.errors.PyMongoError as e:
            logging.critical(f"❌ Database operation failed: {e}")
            raise DatabaseConnectionError("Bulk write to MongoDB failed.") from e