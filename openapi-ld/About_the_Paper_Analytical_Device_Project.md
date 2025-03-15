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

## Ontology
```turtle
@prefix pad: <https://pad.crc.nd.edu/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix wd:   <http://www.wikidata.org/entity/> .
@prefix dct:   <http://purl.org/dc/terms/> .

########################################
# Classes
########################################

# AnalyticalCard: A chromatography card used for drug testing.
pad:AnalyticalCard a owl:Class ;
    rdfs:label "Analytical Card" ;
    rdfs:comment "A PAD card, typically 3″ x 4″, printed with wax barriers forming 12 lanes. It captures samples (drugs) that react with pre-applied reagents to produce a unique Color Barcode for drug identification." ;
    owl:equivalentClass wd:Q133248639 .

# Reagent: A chemical reagent applied in the lanes.
pad:Reagent a owl:Class ;
    rdfs:label "Reagent" ;
    rdfs:comment "A chemical reagent placed in the lanes below the swipe line that interacts with the sample to produce a detectable color reaction." ;
    owl:equivalentClass wd:Q2356542 .

# Sample: A substance (e.g., a drug) tested on the PAD card.
pad:Sample a owl:Class ;
    rdfs:label "Sample" ;
    rdfs:comment "A drug or chemical substance that is applied to the PAD card for testing." ;
    owl:equivalentClass wd:Q8386 .

# Layout: Defines the physical geometry of the PAD card.
pad:Layout a owl:Class ;
    rdfs:label "Layout" ;
    rdfs:comment "The geometric configuration of a PAD card, including the arrangement of 12 lanes, the matrix of reagents in each lane, the swipe line, and the bounding box that defines the Color Barcode region." .

# Project: An organizational unit that groups PAD cards under defined testing parameters.
pad:Project a owl:Class ;
    rdfs:label "Project" ;
    rdfs:comment "A grouping of PAD cards with defined test parameters, including samples to be analyzed, the layout used, and expected concentrations. Cards from multiple projects can be aggregated into a Dataset." .

# NeuralNetwork: A machine learning model used to analyze PAD card images.
pad:NeuralNetwork a owl:Class ;
    rdfs:label "Neural Network" ;
    rdfs:comment "A machine learning model trained on PAD card image data to analyze the Color Barcode and identify drugs." ;
    owl:equivalentClass wd:Q192776 .

# CardGroup: A batch grouping of PAD cards produced together.
pad:CardGroup a owl:Class ;
    rdfs:label "Card Group" ;
    rdfs:comment "A production batch of PAD cards, tracked by sample ID ranges, production date, and annotations." .

# User: An individual who operates the PAD system or manages projects.
pad:User a owl:Class ;
    rdfs:label "User" ;
    rdfs:comment "An operator or project owner involved in processing PAD cards or managing PAD projects." .

# BoundingBox: A rectangular region defined by coordinate points.
pad:BoundingBox a owl:Class ;
    rdfs:label "Bounding Box" ;
    rdfs:comment "A rectangular area defined by coordinates, used to delineate regions of interest such as the Color Barcode area on a PAD card." .

# ColorBarcode: The result of processing a PAD card, consisting of a unique pattern of colors.
pad:ColorBarcode a owl:Class ;
    rdfs:label "Color Barcode" ;
    rdfs:comment "A barcode generated from the color patterns produced by the reaction of reagents with a drug sample on a PAD card. It is used to determine the sample identity and authenticity." .

# Dataset: A curated collection of PAD card images and metadata for training, validation, and testing.
pad:Dataset a owl:Class ;
    rdfs:label "Dataset" ;
    rdfs:comment "A collection of PAD card images partitioned into training, validation, and test sets. The dataset includes metadata that defines the assignment of cards to each set and contains labels (e.g., sample/drug names, concentrations). It is maintained in the pad_dataset_registry." ;
    dct:conformsTo <http://mlcommons.org/croissant/1.0> .

########################################
# Object Properties (Relationships)
########################################

# Linking an AnalyticalCard to its Layout.
pad:hasLayout a owl:ObjectProperty ;
    rdfs:domain pad:AnalyticalCard ;
    rdfs:range pad:Layout ;
    rdfs:label "has layout" ;
    rdfs:comment "Associates a PAD card with its layout configuration." .

# Linking a Card to the Project it belongs to.
pad:belongsToProject a owl:ObjectProperty ;
    rdfs:domain pad:AnalyticalCard ;
    rdfs:range pad:Project ;
    rdfs:label "belongs to project" ;
    rdfs:comment "Links a PAD card to the project under which it is analyzed." .

# Linking a Card to the User (operator) who processed it.
pad:performedBy a owl:ObjectProperty ;
    rdfs:domain pad:AnalyticalCard ;
    rdfs:range pad:User ;
    rdfs:label "performed by" ;
    rdfs:comment "Indicates the user or operator responsible for processing the PAD card." .

# Linking a Project to its Layout.
pad:layoutUsed a owl:ObjectProperty ;
    rdfs:domain pad:Project ;
    rdfs:range pad:Layout ;
    rdfs:label "layout used" ;
    rdfs:comment "Specifies the layout configuration used for PAD cards in the project." .

# Linking a Project to the Samples (drugs) under analysis.
pad:hasSample a owl:ObjectProperty ;
    rdfs:domain pad:Project ;
    rdfs:range pad:Sample ;
    rdfs:label "has sample" ;
    rdfs:comment "Associates a project with the samples (drugs) that are analyzed." .

# Linking a Project to its Cards.
pad:hasCard a owl:ObjectProperty ;
    rdfs:domain pad:Project ;
    rdfs:range pad:AnalyticalCard ;
    rdfs:label "has card" ;
    rdfs:comment "Associates a project with the PAD cards assigned to it." .

# Linking a NeuralNetwork to the Project it was trained on.
pad:trainedOnProject a owl:ObjectProperty ;
    rdfs:domain pad:NeuralNetwork ;
    rdfs:range pad:Project ;
    rdfs:label "trained on project" ;
    rdfs:comment "Indicates the project from which data was used to train the neural network." .

# Linking a CardGroup to its Project.
pad:groupProject a owl:ObjectProperty ;
    rdfs:domain pad:CardGroup ;
    rdfs:range pad:Project ;
    rdfs:label "group project" ;
    rdfs:comment "Links a card group to the project it belongs to." .

# Linking an AnalyticalCard to the ColorBarcode it produces.
pad:producesColorBarcode a owl:ObjectProperty ;
    rdfs:domain pad:AnalyticalCard ;
    rdfs:range pad:ColorBarcode ;
    rdfs:label "produces color barcode" ;
    rdfs:comment "Indicates that a PAD card produces a Color Barcode as a result of the chemical reactions in its lanes." .

# Linking a Layout to its Barcode Bounding Box.
pad:hasBarcodeBoundingBox a owl:ObjectProperty ;
    rdfs:domain pad:Layout ;
    rdfs:range pad:BoundingBox ;
    rdfs:label "has barcode bounding box" ;
    rdfs:comment "Specifies the bounding box within the card geometry that defines the area where the Color Barcode appears." .

# Linking a Dataset to the cards it contains.
pad:containsCard a owl:ObjectProperty ;
    rdfs:domain pad:Dataset ;
    rdfs:range pad:AnalyticalCard ;
    rdfs:label "contains card" ;
    rdfs:comment "Associates a dataset with the PAD cards included in its training, validation, and test sets." .

# Linking a Dataset to the projects it aggregates.
pad:aggregatesProject a owl:ObjectProperty ;
    rdfs:domain pad:Dataset ;
    rdfs:range pad:Project ;
    rdfs:label "aggregates project" ;
    rdfs:comment "Indicates that the dataset includes cards from one or more projects." .

# Linking a Dataset to a NeuralNetwork used for training.
pad:usedForTraining a owl:ObjectProperty ;
    rdfs:domain pad:Dataset ;
    rdfs:range pad:NeuralNetwork ;
    rdfs:label "used for training" ;
    rdfs:comment "Indicates that the dataset is used to train a neural network." .

########################################
# Datatype Properties (Attributes)
########################################

# For AnalyticalCard
pad:creationDate a owl:DatatypeProperty ;
    rdfs:domain pad:AnalyticalCard ;
    rdfs:range xsd:dateTime ;
    rdfs:label "creation date" ;
    rdfs:comment "The date the PAD card was created." .

pad:imageLocation a owl:DatatypeProperty ;
    rdfs:domain pad:AnalyticalCard ;
    rdfs:range xsd:anyURI ;
    rdfs:label "image location" ;
    rdfs:comment "The URL or file path of the card's processed image." .

pad:cameraUsed a owl:DatatypeProperty ;
    rdfs:domain pad:AnalyticalCard ;
    rdfs:range xsd:string ;
    rdfs:label "camera used" ;
    rdfs:comment "The type of camera or phone used to capture the card image." .

pad:notes a owl:DatatypeProperty ;
    rdfs:domain pad:AnalyticalCard ;
    rdfs:range xsd:string ;
    rdfs:label "notes" ;
    rdfs:comment "User notes or observations recorded for the PAD card." .

pad:sampleId a owl:DatatypeProperty ;
    rdfs:domain pad:AnalyticalCard ;
    rdfs:range xsd:string ;
    rdfs:label "sample ID" ;
    rdfs:comment "The printed identifier of the sample on the card." .

pad:quantity a owl:DatatypeProperty ;
    rdfs:domain pad:AnalyticalCard ;
    rdfs:range xsd:decimal ;
    rdfs:label "quantity" ;
    rdfs:comment "The concentration (percentage) of the active substance in the sample." .

# For Reagent
pad:reagentName a owl:DatatypeProperty ;
    rdfs:domain pad:Reagent ;
    rdfs:range xsd:string ;
    rdfs:label "reagent name" ;
    rdfs:comment "The name of the reagent (chemical) used in the PAD lanes." .

pad:reagentNotes a owl:DatatypeProperty ;
    rdfs:domain pad:Reagent ;
    rdfs:range xsd:string ;
    rdfs:label "reagent notes" ;
    rdfs:comment "Additional notes or properties of the reagent." .

# For Sample
pad:drug a owl:DatatypeProperty ;
    rdfs:domain pad:Sample ;
    rdfs:range xsd:string ;
    rdfs:label "drug" ;
    rdfs:comment "The drug or chemical substance being tested on the PAD card." .

# For Layout
pad:layoutMatrix a owl:DatatypeProperty ;
    rdfs:domain pad:Layout ;
    rdfs:range xsd:string ;
    rdfs:label "layout matrix" ;
    rdfs:comment "A textual or encoded representation of the arrangement of reagents in the PAD card lanes." .

# For Project
pad:projectName a owl:DatatypeProperty ;
    rdfs:domain pad:Project ;
    rdfs:range xsd:string ;
    rdfs:label "project name" ;
    rdfs:comment "The name of the project under which PAD cards are organized." .

pad:annotation a owl:DatatypeProperty ;
    rdfs:domain pad:Project ;
    rdfs:range xsd:string ;
    rdfs:label "annotation" ;
    rdfs:comment "An annotation or remark printed on the PAD cards to summarize project information." .

pad:concentrations a owl:DatatypeProperty ;
    rdfs:domain pad:Project ;
    rdfs:range xsd:decimal ;
    rdfs:label "concentrations" ;
    rdfs:comment "The list of expected sample concentrations (e.g., 20%, 50%, 80%, 100%) used in the project." .

pad:projectNotes a owl:DatatypeProperty ;
    rdfs:domain pad:Project ;
    rdfs:range xsd:string ;
    rdfs:label "project notes" ;
    rdfs:comment "General comments or notes about the project." .

# For NeuralNetwork
pad:drugSize a owl:DatatypeProperty ;
    rdfs:domain pad:NeuralNetwork ;
    rdfs:range xsd:integer ;
    rdfs:label "drug size" ;
    rdfs:comment "The size (or count) of drug samples used in training the network." .

pad:labels a owl:DatatypeProperty ;
    rdfs:domain pad:NeuralNetwork ;
    rdfs:range xsd:string ;
    rdfs:label "labels" ;
    rdfs:comment "A comma-separated list of labels associated with the neural network's training data." .

pad:weightsLocation a owl:DatatypeProperty ;
    rdfs:domain pad:NeuralNetwork ;
    rdfs:range xsd:anyURI ;
    rdfs:label "weights location" ;
    rdfs:comment "The URL or file path where the trained weights of the neural network are stored." .

pad:layoutType a owl:DatatypeProperty ;
    rdfs:domain pad:NeuralNetwork ;
    rdfs:range xsd:string ;
    rdfs:label "layout type" ;
    rdfs:comment "The type of PAD layout on which the neural network was trained." .

pad:imageProperties a owl:DatatypeProperty ;
    rdfs:domain pad:NeuralNetwork ;
    rdfs:range xsd:string ;
    rdfs:label "image properties" ;
    rdfs:comment "Properties of the images used in network training, such as dimensions and color space." .

pad:SHA256 a owl:DatatypeProperty ;
    rdfs:domain pad:NeuralNetwork ;
    rdfs:range xsd:string ;
    rdfs:label "SHA256" ;
    rdfs:comment "A SHA256 hash of the neural network file for integrity verification." .

# For CardGroup
pad:sampleIdRange a owl:DatatypeProperty ;
    rdfs:domain pad:CardGroup ;
    rdfs:range xsd:string ;
    rdfs:label "sample ID range" ;
    rdfs:comment "The range of sample IDs included in the card group." .

pad:groupDate a owl:DatatypeProperty ;
    rdfs:domain pad:CardGroup ;
    rdfs:range xsd:dateTime ;
    rdfs:label "group date" ;
    rdfs:comment "The production date of the card group." .

pad:groupAnnotation a owl:DatatypeProperty ;
    rdfs:domain pad:CardGroup ;
    rdfs:range xsd:string ;
    rdfs:label "group annotation" ;
    rdfs:comment "An annotation printed on the card group summarizing key production details." .

pad:groupComment a owl:DatatypeProperty ;
    rdfs:domain pad:CardGroup ;
    rdfs:range xsd:string ;
    rdfs:label "group comment" ;
    rdfs:comment "Additional comments regarding the production or tracking of the card group." .

# For User
pad:userName a owl:DatatypeProperty ;
    rdfs:domain pad:User ;
    rdfs:range xsd:string ;
    rdfs:label "user name" ;
    rdfs:comment "The name or identifier of the user (operator or project owner)." .

pad:email a owl:DatatypeProperty ;
    rdfs:domain pad:User ;
    rdfs:range xsd:string ;
    rdfs:label "email" ;
    rdfs:comment "The email address of the user." .

# For Dataset
pad:datasetLabels a owl:DatatypeProperty ;
    rdfs:domain pad:Dataset ;
    rdfs:range xsd:string ;
    rdfs:label "dataset labels" ;
    rdfs:comment "A comma-separated list of labels defining categories for the dataset (e.g., drug names, concentration levels)." .

pad:datasetVersion a owl:DatatypeProperty ;
    rdfs:domain pad:Dataset ;
    rdfs:range xsd:string ;
    rdfs:label "dataset version" ;
    rdfs:comment "The version identifier for the dataset as maintained in the pad_dataset_registry." .

pad:trainingSet a owl:DatatypeProperty ;
    rdfs:domain pad:Dataset ;
    rdfs:range xsd:string ;
    rdfs:label "training set" ;
    rdfs:comment "A reference or identifier for the training set portion of the dataset." .

pad:validationSet a owl:DatatypeProperty ;
    rdfs:domain pad:Dataset ;
    rdfs:range xsd:string ;
    rdfs:label "validation set" ;
    rdfs:comment "A reference or identifier for the validation set portion of the dataset." .

pad:testSet a owl:DatatypeProperty ;
    rdfs:domain pad:Dataset ;
    rdfs:range xsd:string ;
    rdfs:label "test set" ;
    rdfs:comment "A reference or identifier for the test set portion of the dataset." .

# Object Properties for Dataset
pad:containsCard a owl:ObjectProperty ;
    rdfs:domain pad:Dataset ;
    rdfs:range pad:AnalyticalCard ;
    rdfs:label "contains card" ;
    rdfs:comment "Associates a dataset with the PAD cards included in its training, validation, and test sets." .

pad:aggregatesProject a owl:ObjectProperty ;
    rdfs:domain pad:Dataset ;
    rdfs:range pad:Project ;
    rdfs:label "aggregates project" ;
    rdfs:comment "Indicates that the dataset includes PAD cards from one or more projects." .

pad:usedForTraining a owl:ObjectProperty ;
    rdfs:domain pad:Dataset ;
    rdfs:range pad:NeuralNetwork ;
    rdfs:label "used for training" ;
    rdfs:comment "Indicates that the dataset is used to train a neural network." .
```