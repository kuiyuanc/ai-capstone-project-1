import os
from argparse import ArgumentParser
from itertools import product

import pandas as pd
import requests
from tqdm import tqdm

BASE_URL = "https://pixabay.com/api/"


def fetch_image(url, filepath):
    """
    Fetches an image from the given URL and saves it to the specified file path.

    Args:
        url (str): URL of the image.
        filepath (str): Path to the file where the image should be saved.

    Returns:
        bool: True if the image was successfully downloaded and saved, False otherwise.
    """
    # Send a GET request to the URL with streaming enabled
    response = requests.get(url, stream=True)

    # Check if the request was successful (HTTP status code 200)
    successful = response.status_code == 200

    if successful:
        # Open the file in binary write mode
        with open(filepath, "wb") as file:
            # Write the image content in chunks to the file
            for chunk in response.iter_content(2**16):
                file.write(chunk)
    else:
        # Print a failure message if the request was not successful
        print(f"Fail:       {filepath}")

    return successful


def fetch_images(metadata: pd.DataFrame, save_dir):
    """
    Downloads images from URLs specified in the metadata DataFrame and saves them to the specified directory.

    Args:
        metadata (pd.DataFrame): DataFrame containing image metadata, including URLs and IDs.
        save_dir (str): Directory where images will be saved.

    Returns:
        None

    The function creates the directory if it doesn't exist, iterates through each row of the metadata,
    constructs the file path using the image ID, and downloads the image if it hasn't been previously downloaded.
    """
    # Ensure the save directory exists
    os.makedirs(save_dir, exist_ok=True)

    # Iterate through each row in the metadata DataFrame
    for _, row in tqdm(tuple(metadata.iterrows()), desc="Fetch images"):
        # Extract the URL and ID for each image
        url = row["URL"]
        filename = f"{row['ID']}.jpg"

        # Construct the file path
        filepath = os.path.join(save_dir, filename)

        # Download the image only if it doesn't already exist
        if not os.path.exists(filepath):
            # Fetch and save the image
            fetch_image(url, filepath)


def make_query(params):
    """
    Makes a query to the Pixabay API with the given parameters and returns the received metadata.

    Args:
        params (dict): Dictionary of query parameters.

    Returns:
        list: List of metadata dictionaries.
    """
    # Make a request to the Pixabay API
    if params["content_type"] == "authentic":
        # For authentic content, make a regular request
        response = requests.get(BASE_URL, params=params)
    else:
        # For AI-generated content, make a request with the 'q' parameter
        # (query) set to 'ai_generated'
        response = requests.get(f"{BASE_URL}?q=ai_generated", params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response as JSON
        data = response.json()

        # Get the list of hits from the response
        metadata = data.get("hits", list())
    else:
        # If the request was not successful, print the response text
        print()
        print(response.text)

        # Set the metadata to an empty list
        metadata = []

    return metadata


def fetch_metadata(args):
    """
    Fetches metadata from the Pixabay API according to the given parameters and returns them as a pandas DataFrame.

    Args:
        args (Namespace): Parsed command line arguments.

    Returns:
        pd.DataFrame: DataFrame containing the metadata.
    """
    # Define the iterested values for content types, image types, orders
    CONTENT_TYPES = ("authentic", "ai")
    IMAGE_TYPES = ("photo", "illustration")
    ORDERS = ("popular",)

    # Unused parameters: categories, colors, editor choices
    CATEGORIES = ("Unknown",)
    COLORS = ("Unknown",)
    EDITOR_CHOICES = ("Unknown",)

    # Define the column names for the metadata DataFrame
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

    metadata = []  # List to store metadata entries
    params = {"key": args.api_key, "per_page": args.per_page}  # Base parameters for API query

    # Generate all possible combinations of the parameters
    param_combs = tuple(product(CONTENT_TYPES, IMAGE_TYPES, CATEGORIES, COLORS, EDITOR_CHOICES, ORDERS))

    # Iterate over each combination of parameters
    for content_type, image_type, category, colors, editors_choice, order in tqdm(param_combs, desc="Fetch metadata"):
        # Set the specific parameters for this combination
        params["content_type"] = content_type
        params["image_type"] = image_type

        # Calculate the number of pages to request based on the number of images and images per page
        for page in range(1, args.num_images // args.per_page + 1):
            params["page"] = page  # Set the current page number

            # Make a query to the Pixabay API with the current parameters
            response = make_query(params)

            # Append each image's metadata to the list
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

    # Return the metadata as a pandas DataFrame
    return pd.DataFrame(metadata, columns=COLUMNS)


def build_dataset(args):
    """
    Builds the dataset by reading the metadata from the given CSV file, and fetching the images using the URLs in the metadata.

    Args:
        args (ArgumentParser): Object containing the following attributes:
            csv_file (str): Path to the CSV file containing the metadata.
            save_dir (str): Directory where the images should be saved.

    Returns:
        None
    """
    metadata = fetch_metadata(args)
    metadata.to_csv(args.csv_file, index=False)
    fetch_images(metadata, args.save_dir)


def parse_args():
    """
    Parses command line arguments and returns an ArgumentParser object containing the parsed arguments.

    Args:
        None

    Returns:
        ArgumentParser: Object containing the parsed arguments.
    """
    # API Key for Pixabay API
    API_KEY = "49378178-ce6d36965efbe00b94869088b"

    # Output directory for the images
    SAVE_DIR = "pixabay"

    # CSV file for storing the metadata
    CSV_FILE = "metadata.csv"

    # Number of images to fetch per page
    PER_PAGE = 200

    # Number of queries to make per category
    NUM_IMAGES = 600

    parser = ArgumentParser()

    # Set the default API key
    parser.add_argument("--api_key", default=API_KEY, type=str, help="Pixabay API Key")

    # Set the default output directory
    parser.add_argument("--save_dir", default=SAVE_DIR, type=str, help="Output directory")

    # Set the default CSV file for metadata
    parser.add_argument("--csv_file", default=CSV_FILE, type=str, help="CSV file for metadata")

    # Set the default number of images to fetch per page
    parser.add_argument("--per_page", default=PER_PAGE, type=int, help="Number of images per page")

    # Set the default number of queries to make per category
    parser.add_argument("--num_images", default=NUM_IMAGES, type=int, help="Number of queries per category")

    return parser.parse_args()


def main():
    """
    Main entry point for the script. Parses command line arguments and builds the dataset.

    Args:
        None

    Returns:
        None
    """
    args = parse_args()
    build_dataset(args)


if __name__ == "__main__":
    main()
