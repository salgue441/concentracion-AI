import argparse
from pathlib import Path
from typing import Dict, List
from PIL import Image, ImageStat
import csv
from tqdm import tqdm


def calculate_image_metrics(image_path: Path) -> Dict[str, float]:
    """
    Calculate brightness and contrast for an image.

    Args:
        image_path: Path to the image file

    Returns:
        Dictionary containing brightness and contrast values
    """
    try:
        with Image.open(image_path) as img:
            if img.mode != "L":
                img = img.convert("L")

            stat = ImageStat.Stat(img)

            return {
                "filename": image_path.name,
                "brightness": round(stat.mean[0], 2),
                "contrast": round(stat.stddev[0], 2),
            }
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return {"filename": image_path.name, "brightness": None, "contrast": None}


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

    with output_file.open("w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=["filename", "brightness", "contrast"]
        )
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze image brightness and contrast."
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

    if results:
        avg_brightness = sum(
            r["brightness"] for r in results if r["brightness"] is not None
        ) / len(results)

        avg_contrast = sum(
            r["contrast"] for r in results if r["contrast"] is not None
        ) / len(results)

        print(f"\nProcessed {len(results)} images")
        print(f"Average brightness: {round(avg_brightness, 2)}")
        print(f"Average contrast: {round(avg_contrast, 2)}")
        print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
