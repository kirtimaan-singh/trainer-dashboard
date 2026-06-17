import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Define parameters
trainers = ["John Smith", "Sarah Johnson", "Mike Wilson", "Emily Davis", "Alex Martinez"]
activity_types = ["Training", "Mentoring", "Workshop", "Certification", "Assessment", "Development"]
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 3, 31)

# Generate dates
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Create sample data
data = []

for trainer in trainers:
    # Generate 30-40 activities per trainer
    num_activities = np.random.randint(30, 40)
    
    for _ in range(num_activities):
        # Random date
        activity_date = np.random.choice(date_range)
        
        # Random activity type
        activity = np.random.choice(activity_types)
        
        # Random start time (8 AM to 5 PM)
        start_hour = np.random.randint(8, 17)
        start_minute = np.random.choice([0, 30])
        start_time = f"{start_hour:02d}:{start_minute:02d}:00"
        
        # Duration between 1-4 hours
        duration = np.random.uniform(1, 4)
        
        # Calculate end time
        end_datetime = datetime.combine(activity_date.date(), datetime.strptime(start_time, "%H:%M:%S").time()) + timedelta(hours=duration)
        end_time = end_datetime.strftime("%H:%M:%S")
        
        # Make sure end time is within business hours
        if end_datetime.hour > 18:
            duration = np.random.uniform(0.5, 2)
        
        data.append({
            "Date": activity_date,
            "Trainer Name": trainer,
            "Activity Type": activity,
            "Start Time": start_time,
            "End Time": end_time,
            "Duration (Hours)": round(duration, 1)
        })

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_file = "Enhanced Trainer Activity Log (2).xlsx"
df.to_excel(output_file, index=False, engine='openpyxl')

print(f"✅ Sample dataset created successfully: {output_file}")
print(f"\n📊 Dataset Summary:")
print(f"   - Total Activities: {len(df)}")
print(f"   - Trainers: {len(df['Trainer Name'].unique())}")
print(f"   - Activity Types: {len(df['Activity Type'].unique())}")
print(f"   - Date Range: {df['Date'].min().date()} to {df['Date'].max().date()}")
print(f"   - Total Hours: {df['Duration (Hours)'].sum():.1f}")
print(f"\n📋 First few rows:")
print(df.head(10))
