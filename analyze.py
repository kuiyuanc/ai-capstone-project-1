import os
from argparse import ArgumentParser

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import StandardScaler

CATEGORICAL_COLS = ("Content_Type", "Image_Type", "Category", "Colors", "Editor_Choice", "Order")
RAW_NUMERICAL_COLS = ["Views", "Likes", "Downloads", "Comments"]
DERIVED_NUMERICAL_COLS = [f"{col}_Per_View" for col in RAW_NUMERICAL_COLS[1:]]
NUMERICAL_COLS = RAW_NUMERICAL_COLS + DERIVED_NUMERICAL_COLS


def preprocess(metadata) -> pd.DataFrame:
    """
    Preprocess the metadata DataFrame by engineering features and encoding categorical variables.

    This function does the following:
    1. Creates derived features: engagement ratios (Views-to-Likes, Views-to-Downloads, Views-to-Comments)
    2. One-Hot encodes the categorical feature `Image_Type`
    3. Normalizes the numerical features using StandardScaler

    Args:
        metadata (pd.DataFrame): DataFrame containing the metadata, with columns to be preprocessed

    Returns:
        pd.DataFrame: The preprocessed DataFrame
    """
    # Feature Engineering: Create Engagement Ratios (Views-to-Likes, Views-to-Downloads, Views-to-Comments)
    for derived, raw in zip(DERIVED_NUMERICAL_COLS, RAW_NUMERICAL_COLS[1:]):
        metadata[derived] = metadata[raw] / metadata["Views"]
    metadata.fillna(0, inplace=True)  # Replace NaN from division by zero

    # One-Hot Encode Categorical Features Image_Type
    metadata = pd.get_dummies(metadata, columns=["Image_Type"])

    # Normalizing Numerical Features
    metadata[NUMERICAL_COLS] = StandardScaler().fit_transform(metadata[NUMERICAL_COLS])

    return metadata


def clean(metadata, log):
    """
    Cleans the metadata DataFrame by handling missing IDs, duplicates, mis-marked content types,
    and filling missing values.

    Args:
        metadata (pd.DataFrame): DataFrame containing the metadata to be cleaned.
        log: Logging object to record cleaning statistics.

    Returns:
        pd.DataFrame: The cleaned metadata DataFrame.
    """
    total = len(metadata)

    # Drop rows missing ID
    metadata.dropna(subset=["ID"], inplace=True)
    log.write("============================================================\n")
    log.write(f"Missing ID: {total - len(metadata)}\n")
    total = len(metadata)

    # Handle duplication by dropping duplicate IDs
    metadata.drop_duplicates(subset=["ID"], inplace=True)
    log.write(f"Duplication: {total - len(metadata)}\n")
    total = len(metadata)

    # Correct mis-marked content types: some AI-generated images are marked as authentic
    ai_tags_pattern = "ai generated|ai-generated|ai_generated|aigenerated"
    mask = (metadata["Content_Type"] == "authentic") & (metadata["Tags"].str.contains(ai_tags_pattern, na=False))
    mis_marked = metadata[mask].index
    metadata.loc[mis_marked, "Content_Type"] = "ai"
    log.write(f"Mis-marked Authentic Images: {len(mis_marked)}\n")
    log.write("============================================================\n")
    log.write("\n")

    # Fill missing values for categorical columns with 'Unknown'
    for col in CATEGORICAL_COLS:
        metadata.fillna({col: "Unknown"}, inplace=True)

    # Replace missing values in Tags with an empty string
    metadata.fillna({"Tags": ""}, inplace=True)

    # Fill missing numerical values with the median to handle outliers
    for col in RAW_NUMERICAL_COLS:
        metadata.fillna({col: metadata[col].median()}, inplace=True)

    return metadata


def summary(metadata, log, save_dir, suffix=""):
    """
    Generate summary statistics and plots for the metadata DataFrame.

    Args:
        metadata (pd.DataFrame): DataFrame containing the metadata.
        log: Logging object to record statistics.
        suffix (str): Suffix to append to the figure file names.

    Returns:
        None
    """
    log.write(f"Statistics - {suffix}\n")
    log.write("============================================================\n")

    # Check data types and missing values
    metadata.info(buf=log)
    log.write("\n")

    # Summary statistics
    log.write(f"{metadata.describe().to_string()}\n")
    log.write("============================================================\n")
    log.write("\n")

    # Correlation between Views, Downloads, Likes, and Comments
    sns.pairplot(metadata[RAW_NUMERICAL_COLS])
    plt.savefig(os.path.join(save_dir, f"pairplot_{suffix}.png"))
    plt.clf()

    # Do AI-generated images get more or fewer views/downloads/likes/comments compared to human images?
    sns.boxplot(
        x="Content_Type",
        y="value",
        hue="variable",
        data=pd.melt(metadata, id_vars=["Content_Type"], value_vars=RAW_NUMERICAL_COLS),
    )
    plt.title("Average Engagement: AI vs. Human")
    plt.savefig(os.path.join(save_dir, f"engagement_{suffix}.png"))
    plt.clf()


def parse_args():
    """
    Parse command line arguments for the script.

    Returns:
        ArgumentParser: Object containing the parsed arguments.
    """
    # Output directory for the statistics
    SAVE_DIR = "data/"

    # CSV file for raw metadata
    RAW = "metadata.csv"

    # CSV file for pre-processed metadata
    PRE_PROCESSED = "dataset.csv"

    # Text file for statistics
    STATISTICS = "statistics.txt"

    parser = ArgumentParser()

    # Set the default output directory
    parser.add_argument("--save_dir", default=SAVE_DIR, type=str, help="Output directory for the statistics.")

    # Set the default CSV file for metadata
    parser.add_argument("--raw", default=RAW, type=str, help="CSV file for raw metadata.")

    # Set the default CSV file for metadata
    parser.add_argument("--pre-processed", default=PRE_PROCESSED, type=str, help="CSV file for pre-processed metadata.")

    # Set the default CSV file for metadata
    parser.add_argument("--statistics", default=STATISTICS, type=str, help="Text file for statistics.")

    return parser.parse_args()


def main():
    """
    Main function to run the script.

    1. Parses command line arguments.
    2. Creates the output directory if it doesn't exist.
    3. Reads the raw metadata from the CSV file.
    4. Opens a log file in write mode.
    5. Calculates and logs the summary statistics for the raw metadata.
    6. Cleans the metadata by handling missing IDs, duplicates, mis-marked content types, and filling missing values.
    7. Preprocesses the metadata by engineering features and encoding categorical variables.
    8. Saves the pre-processed metadata to a new CSV file.
    9. Calculates and logs the summary statistics for the pre-processed metadata.
    10. Closes the log file.
    """
    args = parse_args()
    os.makedirs(args.save_dir, exist_ok=True)
    metadata = pd.read_csv(args.raw)
    log = open(os.path.join(args.save_dir, args.statistics), "w")

    summary(metadata, log, args.save_dir, suffix="raw")
    metadata = clean(metadata, log)
    metadata = preprocess(metadata)
    metadata.to_csv(args.pre_processed, index=False)
    summary(metadata, log, args.save_dir, suffix="pre-processed")
    log.close()


if __name__ == "__main__":
    main()
