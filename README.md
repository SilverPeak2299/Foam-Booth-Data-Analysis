# 🧾 Sales Data Engineering Pipeline

This project demonstrates a complete data engineering workflow using real-world sales data from 2007–2025. It includes data ingestion, cleaning and normalization with PySpark, storage into a relational database, and exploratory data analysis (EDA) using Python.

## Project Overview

This repository outlines the steps taken to transform raw, semi-structured sales data into actionable insights:

1. **Initial Exploration (Python)**
   - Understand the structure and irregularities of the dataset.
   - Identify patterns, inconsistencies, and relationships (e.g., linking entries by invoice number).

2. **Data Cleaning & Normalization (LLM Itergration)**
   - Consolidate multi-line sale entries using invoice numbers.
   - Normalize inconsistent naming (e.g., product categories like "HD", "High Dense", "N29/200"), through the use of LLMS.
   - Apply fuzzy matching (e.g., Levenshtein distance) to standardize entries.

3. **Data Storage**
   - Load cleaned data into a PostgreSQL database (e.g., [Supabase Free Tier](https://supabase.com/)).

4. **Data Analysis & Machine Learning**
   - Perform descriptive statistics and time-series analysis.
   - Optionally apply clustering or forecasting models using Python (e.g., scikit-learn, statsmodels).

---

## Data

- Format: Raw `.txt` file (CSV-style), ~7.2MB
- Fields include:
  - Customer Name
  - Date
  - Invoice #
  - Item Type, Description, Quantity, Price, Total
- Notable challenges:
  - Multi-line sales per invoice
  - Inconsistent naming for foam types and materials
  - Spelling errors and unstructured item descriptions

---

## 🛠 Technologies Used

- **Python**: Initial exploration, EDA, ML
- Google Gemini: Tagging and strucutring complex freeform entries
- **PostgreSQL / Supabase**: Data persistence
- **Jupyter Notebook (`.ipynb`)**: Development environment
