# Pixabay Image Dataset
**Repository Link**: [GitHub Repository](https://github.com/kuiyuanc/ai-capstone-project-1.git)

## Overview
This dataset contains metadata and images collected from [Pixabay](https://pixabay.com), an open-source image platform. The dataset consists of **2,400 rows** of metadata and **2,329 corresponding images**. The discrepancy is due to **71 duplicate rows** in the metadata.

## Date
The data were all collected at 2025/03/18.

## Data Source
- **External Source**: [Pixabay](https://pixabay.com)
- **License**: Pixabay images are free to use under [their license](https://pixabay.com/service/terms/), but always verify terms before reuse.

## Dataset Composition
The dataset includes images categorized by content type (human-authored vs. AI-generated) and image type (photo vs. illustration). Each combination contains **600 images**, but some of them are duplicated.
The images corresponding to the metadata rows are stored in the `pixabay` directory, with each image named according to its unique ID (`<ID>.jpg`).

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

## Usage
This dataset can be used for various **computer vision** and **AI research tasks**, including:
- **AI vs. Human Image Classification**
- **Image Sentiment Analysis (based on tags and engagement metrics)**
- **Feature Extraction for Style Transfer Models**
