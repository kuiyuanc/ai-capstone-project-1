import os
from argparse import ArgumentParser
from itertools import product

import pandas as pd
import requests
from tqdm import tqdm

BASE_URL = "https://pixabay.com/api/"


def fetch_image(url, filepath):
    response = requests.get(url, stream=True)
    successful = response.status_code == 200

    if successful:
        with open(filepath, "wb") as file:
            for chunk in response.iter_content(2**16):
                file.write(chunk)
    else:
        print(f"Fail:       {filepath}")

    return successful


def fetch_images(metadata: pd.DataFrame, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    for _, row in tqdm(tuple(metadata.iterrows()), desc="Fetch images"):
        url = row["URL"]
        filename = f"{row['ID']}.jpg"
        filepath = os.path.join(save_dir, filename)
        if not os.path.exists(filepath):
            fetch_image(url, filepath)


def make_query(params):
    if params["content_type"] == "authentic":
        response = requests.get(BASE_URL, params=params)
    else:
        response = requests.get(f"{BASE_URL}?q=ai_generated", params=params)

    if response.status_code == 200:
        data = response.json()
        metadata = data.get("hits", list())
    else:
        print()
        print(response.text)
        metadata = []

    return metadata


def fetch_metadata(args):
    CONTENT_TYPES = ("authentic", "ai")
    IMAGE_TYPES = ("photo", "illustration")
    # CATEGORIES = ("fashion", "nature", "backgrounds", "science", "education", "people", "feelings", "religion", "health", "places", "animals", "industry", "food", "computer", "sports", "transportation", "travel", "buildings", "business", "music")
    CATEGORIES = ("Unknown",)
    # COLORS = ("grayscale", "transparent", "red", "orange", "yellow", "green", "turquoise", "blue", "lilac", "pink", "white", "gray", "black", "brown")
    COLORS = ("Unknown",)
    # EDITOR_CHOICES = ("true", "false")
    EDITOR_CHOICES = ("Unknown",)
    # ORDERS = ("popular", "latest")
    ORDERS = ("popular",)
    COLUMNS = (
        "ID",
        "Content_Type",
        "Image_Type",
        "Category",
        "Colors",
        "Editor_Choice",
        "Order",
        "Tags",
        "Views",
        "Downloads",
        "Likes",
        "Comments",
        "URL",
    )

    metadata = []
    params = {"key": args.api_key, "per_page": args.per_page}
    param_combs = tuple(product(CONTENT_TYPES, IMAGE_TYPES, CATEGORIES, COLORS, EDITOR_CHOICES, ORDERS))
    for content_type, image_type, category, colors, editors_choice, order in tqdm(param_combs, desc="Fetch metadata"):
        params["content_type"] = content_type
        params["image_type"] = image_type
        # params["category"] = category
        # params["colors"] = colors
        # params["editors_choice"] = editors_choice
        # params["order"] = order
        for page in range(1, args.num_images // args.per_page + 1):
            params["page"] = page

            response = make_query(params)
            for image in response:
                metadata.append(
                    (
                        image["id"],
                        content_type,
                        image["type"],
                        category,
                        colors,
                        editors_choice,
                        order,
                        image["tags"],
                        image["views"],
                        image["downloads"],
                        image["likes"],
                        image["comments"],
                        image["largeImageURL"],
                    )
                )

    return pd.DataFrame(metadata, columns=COLUMNS)


def build_dataset(args):
    # metadata = fetch_metadata(args)
    # metadata.to_csv(args.csv_file, index=False)
    metadata = pd.read_csv(args.csv_file)
    fetch_images(metadata, args.save_dir)


def parse_args():
    API_KEY = "49378178-ce6d36965efbe00b94869088b"
    SAVE_DIR = "pixabay"
    CSV_FILE = "metadata.csv"
    PER_PAGE = 200
    NUM_IMAGES = 600

    parser = ArgumentParser()
    parser.add_argument("--api_key", default=API_KEY, type=str, help="Pixabay API Key")
    parser.add_argument("--save_dir", default=SAVE_DIR, type=str, help="Output directory")
    parser.add_argument("--csv_file", default=CSV_FILE, type=str, help="CSV file for metadata")
    parser.add_argument("--per_page", default=PER_PAGE, type=int, help="Number of images per page")
    parser.add_argument("--num_images", default=NUM_IMAGES, type=int, help="Number of queries per category")

    return parser.parse_args()


def main():
    args = parse_args()
    build_dataset(args)


if __name__ == "__main__":
    main()
