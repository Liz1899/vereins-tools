import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
from pdf_tools.extract_images import extract_images_from_pdf

def main() -> None:
    parser = argparse.ArgumentParser(description="Extrahiere alle Bilder aus einer PDF-Datei.")
    parser.add_argument("pdf_path", help="Pfad zur PDF-Datei")
    parser.add_argument("-o", "--output", default="output", help="Basis-Ausgabeordner (Standard: output/)")
    parser.add_argument("-e", "--ext", help="Erzwinge Bildformat (z. B. jpg, png)", default=None)
    args = parser.parse_args()

    count = extract_images_from_pdf(args.pdf_path, args.output, args.ext)
    print(f"[✓] {count} Bilder extrahiert in: {Path(args.output) / Path(args.pdf_path).stem}")

if __name__ == "__main__":
    main()