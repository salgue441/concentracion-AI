import os
import piexif
import argparse
import csv
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from tqdm import tqdm


def get_image_files(base_path: Path) -> List[Path]:
    """
    Recursively search for image files in the given directory.

    Args:
        base_path: The directory to search in.

    Returns:
        A list of Path objects representing the image files found.
    """

    image_extensions = {".jpeg", ".jpg", ".png", ".gif", ".bmp"}

    return [f for f in base_path.rglob("*") if f.suffix.lower() in image_extensions]


def clean_column_name(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


def extract_metadata(image_path: Path) -> Dict[str, Any]:
    """
    Extract metadata from an image file.

    Args:
        image_path: The path to the image file.

    Returns:
        A dictionary containing the extracted metadata.
    """

    metadata = {
        "filename": image_path.name,
        "file_path": str(image_path),
        "file_size": image_path.stat().st_size,
        "last_modified": datetime.fromtimestamp(image_path.stat().st_mtime),
    }

    try:
        with Image.open(image_path) as img:
            metadata.update(
                {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "color_mode": img.mode,
                    "aspect_ratio": (
                        img.width / img.height if img.width and img.height else None
                    ),
                    "orientation": (
                        "landscape"
                        if img.width > img.height
                        else "portrait" if img.height > img.width else "square"
                    ),
                }
            )

            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    clean_tag = clean_column_name(tag)

                    if isinstance(value, (int, float, str)):
                        metadata[f"exif_{clean_tag}"] = value

            try:
                exif_dict = piexif.load(img.info["exif"])

                if "0th" in exif_dict and piexif.ImageIFD.Software in exif_dict["0th"]:
                    metadata["software"] = exif_dict["0th"][
                        piexif.ImageIFD.Software
                    ].decode("utf-8")

            except Exception:
                pass

    except Exception as e:
        print(f"Error processing {image_path}: {e}")

    return metadata


def save_to_csv(metadata_list: List[Dict[str, Any]], output_file: Path):
    """
    Save a list of metadata dictionaries to a CSV file.

    Args:
        metadata_list: A list of dictionaries containing metadata.
        output_file: The path to the output CSV file.
    """

    if not metadata_list:
        return

    fieldnames = set()
    for metadata in metadata_list:
        fieldnames.update(metadata.keys())

    with output_file.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for metadata in metadata_list:
            writer.writerow(metadata)


def main(base_path: str, output_file: str):
    base_dir = Path(base_path)

    if not base_dir:
        raise ValueError(f"Directory not found: {base_path}")

    image_files = get_image_files(base_dir)
    print(f"Found {len(image_files)} image files.")

    metadata_list = []
    for image_file in tqdm(image_files, desc="Processing images"):
        metadata = extract_metadata(image_file)
        metadata_list.append(metadata)

    output_path = Path(output_file)
    save_to_csv(metadata_list, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract metadata from image files.")

    parser.add_argument(
        "base_path",
        type=str,
        help="The directory to search for image files.",
    )

    parser.add_argument(
        "output_file",
        type=str,
        help="The path to the output CSV file.",
    )

    args = parser.parse_args()
    main(args.base_path, args.output_file)
