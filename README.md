# Pixabay Image Dataset
**Repository Link**: [GitHub Repository](https://github.com/kuiyuanc/ai-capstone-project-1.git)

## Overview
This dataset contains metadata and images collected from [Pixabay](https://pixabay.com), an open-source image platform. The dataset consists of **2,400 rows** of metadata and **2,329 corresponding images**. The discrepancy is due to **71 duplicate rows** in the metadata.

## Data Source
- **External Source**: [Pixabay](https://pixabay.com)
- **License**: Pixabay images are royalty-free to use under [their license](https://pixabay.com/service/terms/)

## Dataset Composition
The dataset includes images categorized by content type (human-authored vs. AI-generated) and image type (photo vs. illustration). Each combination contains **600 images**, but some of them are duplicated.
The images corresponding to the metadata rows are stored in the `images/` directory, with each image named according to its unique ID (`<ID>.jpg`).

### **Breakdown**
- **Content Types**:
  - `authentic` (Human-created)
  - `ai` (AI-generated)
- **Image Types**:
  - `photo` (Real-world photography)
  - `illustration` (Digitally created artwork)
- **Metadata Count**: 2,400 rows
- **Unique Images**: 2,329
- **Duplicate Metadata Entries**: 71

## Data Format
The dataset is stored as a **CSV file (`metadata.csv`)** with the following **13 columns**:

| Column Name      | Data Type | Description |
|-----------------|-----------|-------------|
| `ID`            | Integer   | Unique identifier of the image |
| `Content_Type`  | String    | Type of image source (`authentic` or `ai`) |
| `Image_Type`    | String    | Image format (`photo` or `illustration`) |
| `Category`      | String    | Image category (e.g., `nature`, `people`) |
| `Colors`        | String    | Dominant colors in the image |
| `Editor_Choice` | Boolean   | Whether the image was selected as an Editor’s Choice |
| `Order`         | String    | Search sorting order (`popular`, `latest`) |
| `Tags`          | String    | Comma-separated list of descriptive tags |
| `Views`         | Integer   | Number of times the image was viewed |
| `Downloads`     | Integer   | Number of times the image was downloaded |
| `Likes`         | Integer   | Number of likes received by the image |
| `Comments`      | Integer   | Number of comments on the image |
| `URL`           | String    | Direct link to the image on Pixabay |

## Example Data Entry

```
ID: 9467451
Content_Type: authentic
Image_Type: photo
Category: Unknown
Colors: Unknown
Editor_Choice: Unknown
Order: popular
Tags: crimson rosella, parrot, bird, animal, rosella, feathers, plumage, wildlife, nature, platycercus elegans, ornithology, avian, birdwatching, red bird, wings, colourful, wild, close up
Views: 1798
Downloads: 1504
Likes: 43
Comments: 23
URL: https://pixabay.com/get/g48e481c8442bd6d9d70f4df16604de5da7f025b6e43a2f82e9a62ca297f65e26ce59a569bd906843c0f372d4561d9839ccd5598b6362ca334a26174e0304f5fa_1280.jpg
```


## Data Collection
The images and their metadata are downloaded from [Pixabay](https://pixabay.com) using an automated script (`crawl.py`).

### Conditions
- **Date**: 2025/03/18
- **API Used**: [Pixabay API](https://pixabay.com/api/docs/)
- **Collected Data**:
  - Image metadata in `metadata.csv`
  - Corresponding image files in `images/` directory

### Software Used
- **Programming Language**: Python 3
- **External Libraries**:
  - `requests`: Handling API calls
  - `pandas`: Processing metadata
  - `tqdm`: Displaying progress bars

### Detailed Process
#### **1. Fetch Metadata**
First, retrieve metadata using the Pixabay API:
1. Sends API requests for images with different `content_type` and `image_type`.
2. Retrieves metadata for each image, including **ID, tags, image type, views, downloads, likes, comments, and URL**.
3. Stores the metadata in a CSV file (`metadata.csv`).

- **Query Parameters Used**
  - **Content Type**: `authentic`, `ai`
  - **Image Type**: `photo`, `illustration`
  - **Results per Page**: `200`
  - **Number of Images per Category**: `600`
  - **Order**: `popular` (default sorting order used by the Pixabay API, so implicitly used)
- **Query Parameters Unused**
  - **Category**
  - **Colors**
  - **Editor_Choice**

#### **2. Download Images**
Once metadata is collected, the script:
1. Iterates through each image URL.
2. Downloads images that **haven’t been previously downloaded**.
3. Saves images in the `images/` directory.
