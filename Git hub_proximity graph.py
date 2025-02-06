# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 10:39:22 2025

@author: SHRIVARDHINI INDLA
"""

import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
proximity_file = "C:/Users/SHRIVARDHINI INDLA/Downloads/proximity_data_20250206_015135.csv"  # Update with correct file path
proximity_df = pd.read_csv(proximity_file)

# Convert Timestamp to datetime format
proximity_df['Timestamp'] = pd.to_datetime(proximity_df['Timestamp'], format="%M:%S.%f", errors='coerce')

# Sort by Device Address and Timestamp
proximity_df = proximity_df.sort_values(['Device Address', 'Timestamp'])

# Calculate time difference in seconds for each device
proximity_df['Time_Diff'] = proximity_df.groupby('Device Address')['Timestamp'].diff().dt.total_seconds()

# Fill NaN values (first appearance of each device) with 0
proximity_df['Time_Diff'] = proximity_df['Time_Diff'].fillna(0)

# Aggregate total time spent per device
device_time_spent = proximity_df.groupby('Device Address')['Time_Diff'].sum().reset_index()

# Sort devices by time spent for better visualization
device_time_spent = device_time_spent.sort_values(by="Time_Diff", ascending=False)

# Plot bar chart
plt.figure(figsize=(12, 6))
plt.bar(device_time_spent["Device Address"], device_time_spent["Time_Diff"], color='skyblue')

# Label the chart
plt.xticks(rotation=45, ha='right')
plt.xlabel("Device Address")
plt.ylabel("Total Time Spent (Seconds)")
plt.title("Total Time Spent by Each Device in the Proximity Area")
plt.show()
