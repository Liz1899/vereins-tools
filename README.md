# Verbands-Toolset

Dies ist ein wachsendes Open-Source-Toolset zur digitalen Unterstützung von Verbänden, Vereinen und gemeinnützigen Organisationen.

Aktuell enthält es:
- 📄 PDF-Tools zur Bildextraktion
- 🎯 Event Manager: Turnier-/Eventdaten hochladen und verwalten

## PDF-Tools – Bildextraktion

Das Modul extrahiert alle eingebetteten Bilder aus einer PDF-Datei und speichert sie in einem Zielordner.

### Features
- Automatische Erkennung und Extraktion aller Bilder
- Ausgabe in Original- oder Wunschformat (z. B. JPG, PNG)
- Strukturierte Ablage im Ausgabeverzeichnis

### Nutzung

```bash
python scripts/run_pdf_image_extractor.py <Pfad_zur_PDF> [-o Zielordner] [-e Bildformat]`
```

Beispiel:
```bash
python scripts/run_pdf_image_extractor.py input.pdf -o extracted_images -e jpg
```

## Event Manager – Score Uploader

Das Modul `upload_scores` ermöglicht das automatische Einlesen von Spielerdaten aus CSV-Dateien oder Google Sheets und deren Übertragung in eine MongoDB-Datenbank.

### Features
- Import von Spielerdaten (Name, ID, Scores) aus CSV oder Google Sheets
- Validierung der Eingabedaten
- (`--dry-run`) zur Überprüfung der Daten ohne Datenbankänderung

### Getting Started

1. Repository klonen und in das Projektverzeichnis wechseln:

```bash
   git clone https://github.com/Liz1899/verein-tools.git
   cd verein-tools
```

2. Abhängigkeiten installieren:
   
```bash
   pip install -r requirements.txt
```

3. Konfiguration anlegen (über `.env`, siehe `.env.example`) und Script starten:

   - Dry run:
     ```bash
     python scripts/run_score_uploader.py --dry-run
     ```
   - Datenbank-Upload:
     ```bash
     python scripts/run_score_uploader.py
     ```

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green?logo=mongodb)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-API-34A853?logo=googlesheets)

---