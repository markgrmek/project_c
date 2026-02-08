# Machine Learning Approach for Classifying Natural and Anthropogenic Seismic Events

**Authors: Saeid Zarifikoliaee and Mark Grmek**

This repository provides code and resources for training and evaluating two machine learning models—a Convolutional Neural Network (CNN) and a PCA+SVM model—designed to classify seismic events according to their origin, distinguishing between anthropogenic and natural sources.

[Full Project Report](report/report.pdf)

## Environment Setup

It is **highly recommended to use Conda** to manage the Python environment and dependencies. To create the environment from the provided YAML file:

```bash
conda env create -f environment.yml
conda activate my_env

## Data Preparation

- The training data can be obtained using the script data/waveform_fetch.py
- The original event dataset is filtered using filter_events.py (note: only needs to be run once)

## Model Training
- CNN Model: Training and evaluation are done in CNN.ipynb
- PCA+SVM Model: raining and evaluation are done in PCA_SVM.ipynb
