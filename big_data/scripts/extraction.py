import argparse
from pathlib import Path
from typing import Dict, List
from PIL import Image, ImageStat
import csv
from tqdm import tqdm
from datetime import datetime


def calculate_image_metrics(image_path: Path) -> Dict[str, float]:
    """
    Calculate brightness and contrast for an image with additional metadata for visualization.
    """
    try:
        with Image.open(image_path) as img:
            if img.mode != "L":
                img = img.convert("L")

            stat = ImageStat.Stat(img)
            file_stats = image_path.stat()

            return {
                "filename": image_path.name,
                "brightness": round(stat.mean[0], 2),
                "contrast": round(stat.stddev[0], 2),
                "width": img.width,
                "height": img.height,
                "megapixels": round(img.width * img.height / 1000000, 2),
                "file_size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                "date_modified": datetime.fromtimestamp(file_stats.st_mtime).strftime(
                    "%Y-%m-%d"
                ),
                "file_type": image_path.suffix.lower().replace(".", ""),
                "aspect_ratio": (
                    round(img.width / img.height, 2)
                    if img.width and img.height
                    else None
                ),
            }
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None


def process_directory(directory: Path) -> List[Dict[str, float]]:
    """
    Process all images in a directory.
    """
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
    image_files = [
        f for f in directory.rglob("*") if f.suffix.lower() in image_extensions
    ]

    results = []
    for image_file in tqdm(image_files, desc="Processing images"):
        metrics = calculate_image_metrics(image_file)
        if metrics:
            results.append(metrics)

    return results


def save_to_csv(results: List[Dict[str, float]], output_file: Path):
    """
    Save results to a CSV file.
    """
    if not results:
        print("No results to save!")
        return

    fieldnames = [
        "filename",
        "brightness",
        "contrast",
        "width",
        "height",
        "megapixels",
        "file_size_mb",
        "date_modified",
        "file_type",
        "aspect_ratio",
    ]

    with output_file.open("w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze image brightness and contrast for Tableau visualization."
    )
    parser.add_argument("input_dir", type=str, help="Input directory containing images")
    parser.add_argument("output_file", type=str, help="Output CSV file path")
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    output_path = Path(args.output_file)

    if not input_path.exists():
        print(f"Error: Directory '{input_path}' does not exist!")
        return

    results = process_directory(input_path)
    save_to_csv(results, output_path)

    print(f"\nProcessed {len(results)} images")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
