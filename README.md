# Machine Learning Approach for Classifying Natural and Anthropogenic Seismic Events

**Co-athor: [Saeid Zarifikoliaee](https://github.com/saeidzk)**

This repository provides code and resources for training and evaluating two machine learning models—a Convolutional Neural Network (CNN) and a PCA+SVM model—designed to classify seismic events according to their origin, distinguishing between anthropogenic and natural sources.

All the methods and resources used for this project are described in detail in the [Project Report](report/report.pdf)

## Environment Setup

It is **highly recommended to use Conda** to manage the Python environment and dependencies. To create the environment from the provided YAML file:

```bash
conda env create -f environment.yml
conda activate project_c_env
```

## Data Preparation

- The training data is obtained using the script [waveform_fetch.py](data/waveform_fetch.py)
- The original seismic event dataset is filtered using [filter_events.py](data/filter_events.py) (only needs to be run once)

## Model Training
- CNN Model: Training and evaluation are done in [CNN.ipynb](CNN.ipynb)
- PCA+SVM Model: Training and evaluation are done in [PCA_SVM.ipynb](PCA_SVM.ipynb)
