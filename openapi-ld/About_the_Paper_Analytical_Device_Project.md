# Paper Analytical Devices (PAD) Project Overview

**Wikidata Entry:** [Paper Analytical Device (Q133248639)](https://www.wikidata.org/wiki/Q133248639)

## The Mission
Many of the pharmaceuticals that are purchased in the developing world are substandard or outright fake drugs. Although there is no global system for monitoring the quality of medicine, study after study reveals pervasive poor quality and products that are worthless or even harmful to patients. Many countries in the developing world do not have the technological infrastructure or regulatory resources to keep low quality medicines off the market shelves. And since the pharmaceutical trade is a lucrative global market, low quality medicine can cross borders and harm people anywhere in the world.

### Low quality pharmaceuticals are a global problem
The World Health Organization estimates that 10-30% of the pharmaceuticals that are purchased in the developing world are substandard or outright fake drugs. Many countries in the developing world do not have the technological infrastructure or regulatory resources to keep low quality medicines off the market shelves. And since the pharmaceutical trade is a lucrative global market, low quality medicine can cross borders and harm people anywhere in the world.

### We are making tools to solve this problem.
Paper analytical devices (PADs) are test cards that can quickly determine whether a drug tablet contains the correct medicines. They are cheap and easy to use. They don’t require power, chemicals, solvents, or any expensive instruments, so they can be deployed rapidly at large scale wherever a problem with pharmaceutical quality is suspected.

### We are leveling the playing field.
These little test cards could change the balance of power between sellers and buyers. Right now, most buyers have to trust what the seller tells them about the quality of the pharmaceuticals they purchase. Unscrupulous manufacturers and distributors know that there is little chance that their medicines will be screened in a lab. These paper test cards don’t need a lab, and they will enable people all over the world to quickly detect low quality medicines and remove them from the market.

## Introduction

A **Paper Analytical Device (PAD)** is a 58mm x 104mm chromatography card printed with wax lines that form hydrophobic barriers, creating multiple test lanes. It is used to identify drugs and detect potential counterfeits through a color-based reaction pattern. The process involves applying a sample (crushed drug) to a swipe line, partially submerging the card in water, and analyzing the resulting Color Barcode with a neural network.

## Card Structure

- **Dimensions:** Typically 58mm x 104mm  
- **Wax Lines:** Heated to create hydrophobic barriers, forming 12 test lanes  
- **Swipe Line:** Drawn halfway up the card for sample application  
- **Color Barcode:** A unique pattern produced above the swipe line once water and reagents interact with the drug

## Operation

1. **Sample Application:** Crush or remove the drug from packaging and smear it along the swipe line.  
2. **Partial Immersion:** Submerge the bottom 0.5″ of the card in water to initiate fluid travel upward through each lane.  
3. **Chemical Reaction:** Water dissolves and mixes with reagents, generating distinct color patterns in each lane.  
4. **Barcode Analysis:** A neural network inspects the resultant Color Barcode to identify the drug or verify authenticity.

## Infrastructure

- **Fiducial Marks & QR Code:** Each PAD card has a QR code and three additional fiducials. These enable automated image rectification (correcting camera angle distortions).  
- **App Workflow:**  
  1. The app captures a photo of the PAD.  
  2. The image is rectified to correct tombstone effects.  
  3. The rectified image is uploaded to the server, which determines the associated project.  
  4. Training and test sets can be assembled for neural network development, or the trained network is loaded for on-site drug identification.

## Database Structure

The server houses a database with multiple tables. Notably:

### Card Table

- **Fields:**  
  - **ID:** Unique, auto-generated primary key  
  - **Sample name:** The drug being tested  
  - **Test name:** Defines reagent/lanes configuration  
  - **User name:** The operator of the card  
  - **Date of creation:** Timestamp of card creation  
  - **Raw/Processed file location:** Paths to the original and processed card images  
  - **Processing date:** Timestamp for image processing  
  - **Camera type/phone used:** Noted for reference  
  - **Notes:** Free-form input  
  - **Sample ID:** The printed ID on the card  
  - **Quantity:** Percentage of the active pharmaceutical ingredient (API)  
  - **Project ID:** Links the card to a project  
  - **Deleted flag:** Indicates whether the card is removed  
  - **Issue ID:** References potential issues (e.g., leaks between lanes)

### Project Table

- **Fields:**  
  - **ID:** Unique, auto-generated primary key  
  - **Username**: The user/owner of the project  
  - **Project name & annotation**: Label and note printed on cards  
  - **Test name**: Defines the card type or layout  
  - **Sample names**: A JSON list of drugs for testing  
  - **Neutral filler**: Example filler (e.g., lactose) for <100% API  
  - **Quantities**: 20%, 50%, 80%, 100% for partial or full drug concentration  
  - **Notes**: Free-form input

### Other Tables

1. **Reagents:** Chemicals placed in lanes; they react with the drug sample.  
2. **Samples:** Lists available drugs for selection.  
3. **Neural Networks:** Stores trained networks (weights, version, projects).  
4. **Card Issues:** Records problems (leaks, water movement issues, rectification errors, etc.).  
5. **System-wide Items:** API keys and other global settings.

## The App and Website

1. **Mobile/Tablet App:**  
   - Captures the PAD card image.  
   - Rectifies and uploads it to the server.  
   - Receives on-site classification results from a trained neural network to identify the substance.  

2. **Server & API:**  
   - [Swagger/OpenAPI–compliant endpoints](https://pad.crc.nd.edu) are provided for data insertion and retrieval.  
   - Allows retrieving project data, card metadata, and images.  
   - Stores card images and relevant metadata for future training or analysis.

3. **Website:**  
   - Hosted at [https://pad.crc.nd.edu](https://pad.crc.nd.edu)  
   - Showcases the PAD projects, relevant data, and documentation.  
   - Tied to the database for real-time updates on card usage, project organization, and neural network models.

## Wikidata: Paper Analytical Device (Q133248639)

- **Instance of (P31):** Academic discipline (Q11862829)  
- **Subclass of (P279):** Chromatography (Q170050)  
- **Uses (P2283):** Artificial neural network (Q192776)  
- **Has part (P527):** Paper chromatography (Q898473)  
- **Main subject (P921):** Analytical chemistry (Q2346)  
- **Official website (P856):** [https://pad.crc.nd.edu](https://pad.crc.nd.edu)

---

Through PAD technology, quick and inexpensive drug testing is possible. By combining a simple paper-based device with image rectification and machine learning, researchers can rapidly identify potential counterfeits or unknown substances in the field.

---
## Table of Entities, Relationships and Atributes

| **Entity**          | **Description**                                                                                                                                                         | **Attributes**                                                                                                                                   | **Relationships**                                                                                                                 |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| **Analytical Card** | A chromatography-based PAD card, typically 58mm x 104mm with 12 lanes, that captures the chemical reaction result (the Color Barcode) when a drug sample is applied.     | Layout, creation date, image locations (raw & processed), camera used, notes, sample ID, quantity (concentration), operator details             | Belongs to a Project; produces a Color Barcode; is configured by a Layout; operated by a User                                    |
| **Reagent**         | A chemical applied in the lanes below the swipe line that reacts with the sample to generate visible color changes.                                                      | Reagent name, reagent notes                                                                                                                      | Incorporated in the reagent matrix of a Layout                                                                                   |
| **Sample**          | A drug or chemical substance applied to the PAD card for testing.                                                                                                      | Drug name                                                                                                                                         | Tested on Analytical Cards; may later be classified (e.g., as medication)                                                       |
| **Layout**          | The geometric configuration of a PAD card, including the lane boxes, swipe line, barcode bounding box, and reagent matrix (up to 4 reagents per lane).                | Lane boxes, swipe line, barcode_box (bounding box for the Color Barcode), reagent matrix (layout matrix)                                            | Assigned to Analytical Cards (hasLayout); defines the Color Barcode region (hasBarcodeBoundingBox); used in a Project (layoutUsed)  |
| **Project**         | An organizational unit that groups PAD cards under defined testing parameters, including samples, layout, and expected concentrations.                                  | Project name, annotation, test name, sample names, neutral filter, concentrations (e.g., [20, 50, 80, 100]), project notes                         | Analytical Cards are assigned to a Project; has a designated Layout (layoutUsed); Neural Networks are trained on data  from one or more Projects       |
| **Neural Network**  | A machine learning model trained on PAD card images to analyze the Color Barcode and identify drugs.                                                                    | Network ID, name, drugs, drug size, labels, lanes excluded, weights location, layout type, image properties, SHA256                                | Trained on data from a Project or Projects (trainedOnProject); analyzes the Color Barcode produced by an Analytical Card                        |
| **Card Group**      | A batch of PAD cards produced together, used for tracking production details such as sample ID ranges and production dates.                                             | Sample ID range, production date, group annotation, group comment                                                                                | Associated with a Project (groupProject); groups multiple Analytical Cards                                                       |
| **User**            | An individual who operates the PAD system or manages PAD projects.                                                                                                      | User name, email                                                                                                                                 | Operates Analytical Cards; associated with Projects                                                                              |
| **Color Barcode**   | The unique barcode composed of color patterns produced by the reaction of reagents with the drug sample in the PAD card's lanes above the swipe line.                   | Color pattern data (represented via the bounding box defined in the Layout)                                                                       | Produced by an Analytical Card (producesColorBarcode)                                                                            |
| **Bounding Box**    | A rectangular region defined by coordinate points that delineates the area of interest (e.g., where the Color Barcode appears on the PAD card).                         | Coordinates (list of points with x and y values)                                                                                                 | Associated with a Layout (hasBarcodeBoundingBox)                                                                                 |
| **Dataset** | A curated collection of PAD card images and metadata is used to train neural networks. The dataset is partitioned into DEV ( which can be used for training and validation) and TEST sets for robust model development and evaluation. | Metadata includes assignment of cards to training/validation/test sets; labels defining categories (e.g., sample/drug names like ["Acetaminophen", "Artesunate", "Borate", ...] and concentration values like [0, 20, 50, ...]); versioning information from the pad_dataset_registry. | Aggregates card images from multiple projects; serves as training data for neural networks; maintained and version-controlled in the pad_dataset_registry.                   |
