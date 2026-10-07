# M5 Forecasting - Accuracy Dataset

MarketMindAI uses the Walmart M5 dataset as a secondary forecasting
source for item/store demand intelligence.

## Required files

Place the following files in this directory:

- calendar.csv
- sales_train_validation.csv
- sales_train_evaluation.csv
- sell_prices.csv

## Source

M5 Forecasting - Accuracy:
https://www.kaggle.com/competitions/m5-forecasting-accuracy/data

## Purpose

UCI Online Retail II:
- customer behavior
- transaction intelligence
- revenue analysis
- customer segmentation

M5:
- item-level demand
- store-level demand
- calendar/event features
- weekly selling-price features
- demand forecasting

## Important

The raw M5 files are intentionally excluded from Git because
they are large external source files.

The application code, transformations, validation logic,
and forecasting artifacts are version controlled.