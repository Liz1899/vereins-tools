from pathlib import Path
import fitz
from typing import Optional

def extract_images_from_pdf(
    pdf_path: str,
    output_base: str,
    force_extension: Optional[str] = None
) -> int:
    pdf_path_obj = Path(pdf_path)
    pdf_name = pdf_path_obj.stem
    output_folder = Path(output_base) / pdf_name
    output_folder.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    image_count = 0

    for page_number, page in enumerate(doc, start=1):
        for img_index, img in enumerate(page.get_images(full=True), start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            if force_extension:
                image_ext = force_extension.lstrip(".").lower()

            image_filename = f"{pdf_name}_{image_count + 1:03d}.{image_ext}"
            image_path = output_folder / image_filename

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            image_count += 1

    return image_count