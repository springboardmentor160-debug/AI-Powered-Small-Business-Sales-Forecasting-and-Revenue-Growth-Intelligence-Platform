"""
Feature Engineering Pipeline for Customer Segmentation (Milestone 2)
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

class CustomerFeatureEngineer:
    def __init__(self, source_path: str):
        self.source_path = source_path
        self.df_raw = None
        self.df_features = None
        self.scaler = StandardScaler()

    def load_data(self) -> pd.DataFrame:
        target_path = self.source_path
        if not os.path.exists(target_path):
            # Try workspace root fallback
            workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            alt_path = os.path.join(workspace_root, self.source_path)
            if os.path.exists(alt_path):
                target_path = alt_path
            else:
                # Try relative to Milestone_2
                m2_path = os.path.join(workspace_root, "Milestone_2", "data", "source", "cleaned_superstore.csv")
                if os.path.exists(m2_path):
                    target_path = m2_path
                else:
                    raise FileNotFoundError(f"Source file not found at: {self.source_path} or {alt_path}")
        
        self.df_raw = pd.read_csv(target_path)
        if 'order_date' in self.df_raw.columns:
            self.df_raw['order_date'] = pd.to_datetime(self.df_raw['order_date'])
        elif 'sale_date' in self.df_raw.columns:
            self.df_raw['order_date'] = pd.to_datetime(self.df_raw['sale_date'])
            self.df_raw['sales'] = self.df_raw['sales_amount']
        
        return self.df_raw

    def create_features(self) -> pd.DataFrame:
        if self.df_raw is None:
            self.load_data()

        max_date = self.df_raw['order_date'].max() + pd.Timedelta(days=1)

        # Aggregate per customer
        agg_dict = {
            'order_date': lambda dates: (max_date - dates.max()).days, # Recency
            'order_id': 'nunique' if 'order_id' in self.df_raw.columns else 'count', # Frequency
            'sales': ['sum', 'mean'], # Monetary & Avg Order Value
            'quantity': ['sum', 'mean'],
            'profit': 'sum' if 'profit' in self.df_raw.columns else lambda x: 0.0,
            'discount': 'mean' if 'discount' in self.df_raw.columns else lambda x: 0.0
        }

        # Keep original metadata if available
        meta_cols = {}
        if 'customer_name' in self.df_raw.columns:
            meta_cols['customer_name'] = 'first'
        if 'segment' in self.df_raw.columns:
            meta_cols['orig_segment'] = 'first'
        if 'region' in self.df_raw.columns:
            meta_cols['region'] = 'first'

        customer_grouped = self.df_raw.groupby('customer_id')
        
        recency = customer_grouped['order_date'].apply(lambda d: (max_date - d.max()).days)
        frequency = customer_grouped['order_id'].nunique() if 'order_id' in self.df_raw.columns else customer_grouped['sales'].count()
        monetary = customer_grouped['sales'].sum()
        avg_order_val = monetary / np.maximum(frequency, 1)
        total_qty = customer_grouped['quantity'].sum()
        avg_qty = customer_grouped['quantity'].mean()
        total_profit = customer_grouped['profit'].sum() if 'profit' in self.df_raw.columns else pd.Series(0, index=recency.index)
        avg_discount = customer_grouped['discount'].mean() if 'discount' in self.df_raw.columns else pd.Series(0, index=recency.index)
        
        cust_name = customer_grouped['customer_name'].first() if 'customer_name' in self.df_raw.columns else pd.Series("Unknown", index=recency.index)
        orig_segment = customer_grouped['segment'].first() if 'segment' in self.df_raw.columns else pd.Series("Unknown", index=recency.index)
        region = customer_grouped['region'].first() if 'region' in self.df_raw.columns else pd.Series("Unknown", index=recency.index)

        features_df = pd.DataFrame({
            'customer_id': recency.index,
            'customer_name': cust_name.values,
            'orig_segment': orig_segment.values,
            'region': region.values,
            'recency_days': recency.values,
            'frequency_orders': frequency.values,
            'monetary_sales': monetary.values,
            'avg_order_value': avg_order_val.values,
            'total_quantity': total_qty.values,
            'avg_quantity_per_order': avg_qty.values,
            'total_profit': total_profit.values,
            'avg_discount': avg_discount.values
        })

        self.df_features = features_df
        return features_df

    def scale_features(self, feature_cols=None) -> np.ndarray:
        if self.df_features is None:
            self.create_features()

        if feature_cols is None:
            feature_cols = ['recency_days', 'frequency_orders', 'monetary_sales', 'avg_order_value', 'total_profit', 'avg_discount']

        X = self.df_features[feature_cols].copy()
        # Log transform skewed variables like monetary and frequency
        for col in ['monetary_sales', 'frequency_orders', 'avg_order_value']:
            X[col] = np.log1p(np.maximum(X[col], 0))
        
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled, feature_cols

    def save_processed(self, output_path: str):
        if self.df_features is None:
            self.create_features()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.df_features.to_csv(output_path, index=False)
        print(f"Customer features saved to {output_path}")

if __name__ == "__main__":
    src = "Milestone_2/data/source/cleaned_superstore.csv"
    dst = "Milestone_2/data/processed/customer_features.csv"
    fe = CustomerFeatureEngineer(src)
    fe.create_features()
    fe.save_processed(dst)
