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


def preprocess(metadata):
    """
    Preprocess the metadata DataFrame by engineering features and encoding categorical variables.

    Args:
        metadata (pd.DataFrame): DataFrame containing the metadata, with columns to be preprocessed

    Returns:
        pd.DataFrame: The preprocessed DataFrame
    """
    # Avoid affecting file paths
    mask = metadata["Image_Type"].str.contains("/")
    metadata.loc[mask, "Image_Type"] = metadata["Image_Type"].str.replace("/", "_")

    # Feature engineering: create engagement ratios (Views-to-Likes, Views-to-Downloads, Views-to-Comments)
    for derived, raw in zip(DERIVED_NUMERICAL_COLS, RAW_NUMERICAL_COLS[1:]):
        metadata[derived] = metadata[raw] / metadata["Views"]
    metadata.fillna(0, inplace=True)  # Replace NaN from division by zero

    # Encode Content_Type
    metadata["Boolean_Content_Type"] = metadata["Content_Type"].map({"authentic": 0, "ai": 1})

    # One-hot encode Image_Type
    one_hot = pd.get_dummies(metadata["Image_Type"], prefix="Image_Type")
    metadata = pd.concat([metadata, one_hot], axis=1)

    # Normalize numerical features
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
    mask = (metadata["Content_Type"] == "authentic") & (
        metadata["Tags"].str.contains(ai_tags_pattern, na=False)
        | metadata["Image_Type"].str.contains("vector/ai", na=False)
    )
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


def summary(metadata, log, plot_dir, sub_dir=""):
    """
    Generates a summary of metadata, logs statistics, and creates various plots.

    Args:
        metadata (pd.DataFrame): DataFrame containing the metadata to be summarized.
        log (logging.Logger): Logger to record the summary statistics.
        plot_dir (str): Path to the directory where plots will be saved.
        sub_dir (str, optional): Optional subdirectory to save plots. Defaults to "".

    Returns:
        None
    """
    log.write(f"Statistics - {sub_dir}\n")
    log.write("============================================================\n")

    # Log metadata info
    metadata.info(buf=log)
    log.write("\n")

    # Log descriptive statistics
    log.write(f"{metadata.describe().to_string()}\n")
    log.write("============================================================\n")
    log.write("\n")

    # Save plots to subdirectory
    plot_path = os.path.join(plot_dir, sub_dir)
    os.makedirs(plot_path, exist_ok=True)

    # Plot content type distribution
    plot_path_content_type_distribution = os.path.join(plot_path, "content_type_distribution.png")
    plt.figure(figsize=(10, 6))  # Set the figure size to make the plot wider
    metadata["Content_Type"].value_counts().plot(kind="barh")
    plt.title("Content Type Distribution")
    plt.savefig(plot_path_content_type_distribution)
    plt.clf()

    # Plot image type distribution
    plot_path_image_type_distribution = os.path.join(plot_path, "image_type_distribution.png")
    plt.figure(figsize=(10, 6))  # Set the figure size to make the plot wider
    metadata["Image_Type"].value_counts().plot(kind="barh")
    plt.title("Image Type Distribution")
    plt.savefig(plot_path_image_type_distribution)
    plt.clf()

    # Plot content type distribution conditioned on image type
    plot_path_content_condition_image = os.path.join(plot_path, "content_type_distribution_condition_on_image_type.png")
    _, axes = plt.subplots(2, 2, figsize=(12, 12))
    image_types = metadata["Image_Type"].unique()
    axes = axes.flatten()
    for ax, image_type in zip(axes, image_types):
        subset = metadata[metadata["Image_Type"] == image_type]
        subset["Content_Type"].value_counts().plot(
            kind="pie", autopct="%1.1f%%", ax=ax, labels=subset["Content_Type"].unique()
        )
        ax.set_ylabel("")  # Remove y-axis label for better appearance
        ax.text(0.5, -0.05, f"Content Type Distribution for {image_type}", ha="center", transform=ax.transAxes)
    plt.tight_layout()
    plt.suptitle("Content Type Distribution Condition on Image Type")
    plt.savefig(plot_path_content_condition_image)
    plt.clf()

    # Plot image type distribution conditioned on content type
    plot_path_image_condition_content = os.path.join(plot_path, "image_type_distribution_condition_on_content_type.png")
    _, axes = plt.subplots(1, 2, figsize=(12, 8))
    content_types = metadata["Content_Type"].unique()
    axes = axes.flatten()
    for ax, content_type in zip(axes, content_types):
        subset = metadata[metadata["Content_Type"] == content_type]
        subset["Image_Type"].value_counts().plot(
            kind="pie", autopct="%1.1f%%", ax=ax, labels=subset["Image_Type"].unique()
        )
        ax.set_title(f"Image Type Distribution for {content_type}")
        ax.set_ylabel("")  # Remove y-axis label for better appearance
    plt.tight_layout()
    plt.suptitle("Image Type Distribution Condition on Content Type")
    plt.savefig(plot_path_image_condition_content)
    plt.clf()

    # Plot pairplot of engagement metrics
    plot_path_correlation = os.path.join(plot_path, "correlation.png")
    sns.pairplot(metadata[RAW_NUMERICAL_COLS])
    plt.suptitle("Correlation between Engagement Metrics")
    plt.savefig(plot_path_correlation)
    plt.clf()

    # Plot boxplot of average engagement by content type
    plot_path_boxplot_content_type = os.path.join(plot_path, "boxplot_content_type.png")
    plt.figure(figsize=(8, 8))
    sns.boxplot(
        x="Content_Type",
        y="value",
        hue="variable",
        data=pd.melt(metadata, id_vars=["Content_Type"], value_vars=RAW_NUMERICAL_COLS),
    )
    plt.title("Average Engagement of Content Type")
    plt.savefig(plot_path_boxplot_content_type)
    plt.clf()

    # Plot boxplot of average engagement by image type
    plot_path_boxplot_image_type = os.path.join(plot_path, "boxplot_image_type.png")
    plt.figure(figsize=(8, 8))
    sns.boxplot(
        x="Image_Type",
        y="value",
        hue="variable",
        data=pd.melt(metadata, id_vars=["Image_Type"], value_vars=RAW_NUMERICAL_COLS),
    )
    plt.title("Average Engagement of Image Type")
    plt.savefig(plot_path_boxplot_image_type)
    plt.clf()

    # Plot boxplot of average engagement by content type without extreme outliers
    plot_path_boxplot_content_type_no_outliers = os.path.join(plot_path, "boxplot_content_type_no_outliers.png")
    plt.figure(figsize=(8, 8))
    sns.boxplot(
        x="Content_Type",
        y="value",
        hue="variable",
        data=pd.melt(metadata, id_vars=["Content_Type"], value_vars=RAW_NUMERICAL_COLS),
        showfliers=False,  # Exclude extreme outliers
    )
    plt.title("Average Engagement of Content Type (Without Outliers)")
    plt.savefig(plot_path_boxplot_content_type_no_outliers)
    plt.clf()

    # Plot boxplot of average engagement by image type without extreme outliers
    plot_path_boxplot_image_type_no_outliers = os.path.join(plot_path, "boxplot_image_type_no_outliers.png")
    plt.figure(figsize=(8, 8))
    sns.boxplot(
        x="Image_Type",
        y="value",
        hue="variable",
        data=pd.melt(metadata, id_vars=["Image_Type"], value_vars=RAW_NUMERICAL_COLS),
        showfliers=False,  # Exclude extreme outliers
    )
    plt.title("Average Engagement of Image Type (Without Outliers)")
    plt.savefig(plot_path_boxplot_image_type_no_outliers)
    plt.clf()


def parse_args():
    """
    Parse command line arguments for the script.

    Returns:
        ArgumentParser: Object containing the parsed arguments.
    """
    # Input and output directory for the text statistics files
    DATA_DIR = "data"

    # Output directory for the plots
    PLOT_DIR = "plots"

    # CSV file for raw metadata
    RAW = "metadata.csv"

    # CSV file for pre-processed metadata
    PRE_PROCESSED = "dataset.csv"

    # Text file for statistics
    STATISTICS = "statistics.txt"

    parser = ArgumentParser()

    # Set the default intput and output directory
    parser.add_argument("--data_dir", default=DATA_DIR, type=str, help="Input and Output directory.")

    # Set the default output directory for the plots
    parser.add_argument("--plot_dir", default=PLOT_DIR, type=str, help="Output directory for the plots.")

    # Set the default CSV file for raw metadata
    parser.add_argument("--raw", default=RAW, type=str, help="CSV file for raw metadata.")

    # Set the default CSV file for pre-processed metadata
    parser.add_argument("--pre-processed", default=PRE_PROCESSED, type=str, help="CSV file for pre-processed metadata.")

    # Set the default text file for statistics
    parser.add_argument("--statistics", default=STATISTICS, type=str, help="Text file for statistics.")

    return parser.parse_args()


def main():
    """
    Main function to process metadata by cleaning and preprocessing it, and then
    writing summary statistics to a log file.

    Args:
        None

    Returns:
        None
    """
    args = parse_args()

    # Paths for input raw metadata, output preprocessed metadata, and log file
    raw_path = os.path.join(args.data_dir, args.raw)
    output_path = os.path.join(args.data_dir, args.pre_processed)
    log_path = os.path.join(args.data_dir, args.statistics)
    plot_dir = os.path.join(args.data_dir, args.plot_dir)

    # Load raw metadata
    metadata = pd.read_csv(raw_path)
    log = open(log_path, "w")

    # Write initial summary statistics
    summary(metadata, log, plot_dir, sub_dir="raw")

    # Clean and preprocess metadata
    metadata = clean(metadata, log)
    metadata = preprocess(metadata)

    # Save the preprocessed metadata
    metadata.to_csv(output_path, index=False)

    # Write final summary statistics
    summary(metadata, log, plot_dir, sub_dir="pre-processed")

    # Close the log file
    log.close()


if __name__ == "__main__":
    main()
