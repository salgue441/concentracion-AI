import os
import piexif
import argparse
import csv
import hashlib
import math
import imghdr
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


def calculate_aspect_ratio(width: int, height: int) -> float:
    return width / height if width and height else None


def calculate_orientation(width: int, height: int) -> str:
    if width > height:
        return "landscape"
    elif height > width:
        return "portrait"
    else:
        return "square"


def calculate_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(chunk_size), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def get_image_quality_score(img: Image) -> float:
    resolution_score = min(100, (img.width * img.height) / 1000000)
    aspect_ratio = calculate_aspect_ratio(img.width, img.height)

    if aspect_ratio > 3 or aspect_ratio < 0.33:
        resolution_score *= 0.7

    return round(resolution_score, 2)


def extract_metadata(image_path: Path) -> Dict[str, Any]:
    """
    Extract enhanced metadata from an image file.

    Args:
        image_path: The path to the image file.

    Returns:
        A dictionary containing the extracted metadata.
    """
    metadata = {
        "filename": image_path.name,
        "file_path": str(image_path),
        "file_size_bytes": image_path.stat().st_size,
        "file_size_mb": round(image_path.stat().st_size / (1024 * 1024), 2),
        "last_modified": datetime.fromtimestamp(image_path.stat().st_mtime),
        "creation_time": datetime.fromtimestamp(image_path.stat().st_ctime),
        "file_hash": calculate_file_hash(image_path),
        "actual_format": imghdr.what(image_path),
        "extension": image_path.suffix.lower(),
    }

    try:
        with Image.open(image_path) as img:
            metadata.update(
                {
                    "width": img.width,
                    "height": img.height,
                    "resolution": f"{img.width}x{img.height}",
                    "megapixels": round(img.width * img.height / 1000000, 2),
                    "format": img.format,
                    "color_mode": img.mode,
                    "color_depth": img.bits if hasattr(img, "bits") else None,
                    "aspect_ratio": (
                        round(img.width / img.height, 3)
                        if img.width and img.height
                        else None
                    ),
                    "orientation": (
                        "landscape"
                        if img.width > img.height
                        else "portrait" if img.height > img.width else "square"
                    ),
                    "quality_score": get_image_quality_score(img),
                    "is_animated": getattr(img, "is_animated", False),
                    "n_frames": (
                        getattr(img, "n_frames", 1)
                        if getattr(img, "is_animated", False)
                        else 1
                    ),
                }
            )

            exif_data = img._getexif() if hasattr(img, "_getexif") else None
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    clean_tag = tag.lower().replace(" ", "_").replace("-", "_")

                    if isinstance(value, (int, float, str)):
                        metadata[f"exif_{clean_tag}"] = value

                    if tag == "GPSInfo":
                        try:
                            metadata["gps_latitude"] = value[2]
                            metadata["gps_longitude"] = value[4]
                        except:
                            pass

            try:
                exif_dict = piexif.load(img.info["exif"])

                if "0th" in exif_dict:
                    metadata.update(
                        {
                            "camera_make": exif_dict["0th"]
                            .get(piexif.ImageIFD.Make, b"")
                            .decode("utf-8", errors="ignore"),
                            "camera_model": exif_dict["0th"]
                            .get(piexif.ImageIFD.Model, b"")
                            .decode("utf-8", errors="ignore"),
                            "software": exif_dict["0th"]
                            .get(piexif.ImageIFD.Software, b"")
                            .decode("utf-8", errors="ignore"),
                        }
                    )

                # Exposure information
                if "Exif" in exif_dict:
                    metadata.update(
                        {
                            "iso": exif_dict["Exif"].get(
                                piexif.ExifIFD.ISOSpeedRatings
                            ),
                            "exposure_time": str(
                                exif_dict["Exif"].get(piexif.ExifIFD.ExposureTime, "")
                            ),
                            "f_number": str(
                                exif_dict["Exif"].get(piexif.ExifIFD.FNumber, "")
                            ),
                            "focal_length": str(
                                exif_dict["Exif"].get(piexif.ExifIFD.FocalLength, "")
                            ),
                        }
                    )

            except Exception:
                print(f"Error reading EXIF data from {image_path}")

    except Exception as e:
        print(f"Error processing {image_path}: {e}")

    return metadata


def save_to_csv(metadata_list: List[Dict[str, Any]], output_file: Path):
    """
    Save metadata to CSV with improved formatting and error handling.
    """
    if not metadata_list:
        print("No metadata to save!")
        return

    fieldnames = sorted(set().union(*(d.keys() for d in metadata_list)))

    with output_file.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for metadata in metadata_list:
            cleaned_metadata = {
                k: ("" if v is None else v) for k, v in metadata.items()
            }
            writer.writerow(cleaned_metadata)


def generate_summary(metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    summary = {
        "total_images": len(metadata_list),
        "total_size_mb": round(
            sum(m["file_size_bytes"] for m in metadata_list) / (1024 * 1024), 2
        ),
        "formats": {},
        "orientations": {},
        "color_modes": {},
        "avg_quality_score": 0,
        "duplicate_hashes": set(),
    }

    file_hashes = {}
    quality_scores = []

    for metadata in metadata_list:
        summary["formats"][metadata["format"]] = (
            summary["formats"].get(metadata["format"], 0) + 1
        )

        summary["orientations"][metadata["orientation"]] = (
            summary["orientations"].get(metadata["orientation"], 0) + 1
        )

        summary["color_modes"][metadata["color_mode"]] = (
            summary["color_modes"].get(metadata["color_mode"], 0) + 1
        )

        if "quality_score" in metadata:
            quality_scores.append(metadata["quality_score"])

        if metadata["file_hash"] in file_hashes:
            summary["duplicate_hashes"].add(metadata["file_hash"])
        else:
            file_hashes[metadata["file_hash"]] = metadata["file_path"]

    summary["avg_quality_score"] = (
        round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else 0
    )
    summary["duplicate_count"] = len(summary["duplicate_hashes"])

    return summary


def main(base_path: str, output_file: str):
    base_dir = Path(base_path)
    if not base_dir.exists():
        raise ValueError(f"Directory not found: {base_path}")

    image_files = get_image_files(base_dir)
    print(f"Found {len(image_files)} image files.")

    metadata_list = []
    for image_file in tqdm(image_files, desc="Processing images"):
        metadata = extract_metadata(image_file)
        metadata_list.append(metadata)

    summary = generate_summary(metadata_list)
    print("\nSummary:")
    print(f"Total images: {summary['total_images']}")
    print(f"Total size: {summary['total_size_mb']} MB")
    print(f"Average quality score: {summary['avg_quality_score']}")
    print(f"Duplicate images found: {summary['duplicate_count']}")
    print("\nFormat distribution:")
    for fmt, count in summary["formats"].items():
        print(f"  {fmt}: {count}")

    output_path = Path(output_file)
    save_to_csv(metadata_list, output_path)
    print(f"\nMetadata saved to {output_path}")


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
