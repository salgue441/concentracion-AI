# Advanced AI Course - Big Data & NLP 🧠

Instituto Tecnológico y de Estudios Superiores de Monterrey | School of Engineering

![Banner](/images/readme_banner.jpg)

## Repository Structure 📁

This repository contains projects and implementations for two main areas:

### 1. Big Data & Cloud Computing 📊

Animal Image Classification system using PySpark and TensorFlow:

- **Dataset**: 64 animal classes with 10,000+ high-resolution images (6.1 GB)
- **Architecture**:
  - PySpark for data processing and management
  - TensorFlow for deep learning (ResNet50V2 backbone)
  - Mixed precision training for GPU optimization

#### Key Features

- Distributed data processing
- Efficient image loading and preprocessing
- Data augmentation based on class analysis
- Hybrid model approach (TensorFlow + Spark MLlib)

#### Results

- TensorFlow Model: 99.30% accuracy
- Spark ML Model: 98.19% accuracy
- High precision and recall across all classes

#### Project Structure

```bash
big-data-project
│
├── data/                  # Raw and processed data
│   ├── images/
│   │   ├── antelopes/
│   │   ├── ...
│   │   └── wolf/
├── images/                # Images for the notebook
├── notebooks/             # Jupyter notebooks
│   ├── solution.ipynb
├── docs/                  # PDF report of the notebook
├── scripts/               # Metadata extraction scripts and csv file
│   ├── extraction.py
├── tableau/               # Tableau workbook for data visualization
```

### 2. Natural Language Processing 🔤

Language processing techniques implementation including:

- Word embeddings with GloVe
- Text classification with LSTM
- Large Language Models

#### Project Structure

```bash
nlp
│
├── embeddings/                                           # Word embeddings with GloVe
│   ├── cache/                                            # GloVe embeddings cache
│   ├── solution.ipynb                                    # Solution notebook
│   ├── TC3007B_NLP_HW1_embeddings.ipynb                  # Instructions notebook
├── text_classifier/                                      # Text classification with LSTM
│   ├── data/                                             # News dataset
│   ├── solution.ipynb                                    # Solution notebook
│   ├── TC3007B_NLP_HW2_AD2024_text_classifier-1.ipynb    # Instructions notebook
├── transformers/                                         # Transformers and Large Language Models
│   ├── data/                                             # English and Spanish datasets
│   ├── output/                                           # Model outputs
│   ├── solution.ipynb                                    # Solution notebook
│   ├── solution-transformer.ipynb                        # Kaggle notebook with outputs
│   ├── TC3007B_NLP_Transformer-2.ipynb                   # Instructions notebook

```

#### Technologies Used 🛠️

- PyTorch & TensorFlow
- PySpark
- scikit-learn
- NumPy & Pandas
- Matplotlib & Seaborn

## Project Features ✨

- Mixed precision training
- GPU optimization
- Distributed computing
- Advanced visualization techniques
- Model evaluation and comparison
- Data augmentation

## Setup & Requirements 🛠️

Each project has its own requirements and setup instructions. Please refer to the individual project directories for specific details.

## Results & Performance 📈

Big Data Project:

- TensorFlow Model: 99.30% accuracy
- Spark ML Model: 98.19% accuracy
- Balanced precision and recall

NLP Project:

- Text classification
- Word similarity analysis
- Semantic relationship modeling

## License 📄

This project is part of the academic coursework for TC3007B at Tecnológico de Monterrey.
