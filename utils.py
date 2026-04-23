import pandas as pd
import numpy as np
import time

# Pre-defined categories for realistic data
LOCATIONS = ['Mumbai', 'Delhi', 'Bangalore', 'London', 'New York', 'Dubai', 'Singapore']
MERCHANTS = ['Grocery', 'Electronics', 'Luxury', 'Restaurant', 'Online Retail', 'Gas Station', 'Travel']
SPENDING_HABITS = ['Low', 'Medium', 'High']

def generate_transaction(is_fraud=None):
    """Generates a single random transaction."""
    if is_fraud is None:
        # 2% chance of fraud by default
        is_fraud = np.random.choice([0, 1], p=[0.98, 0.02])
    
    # Base features with significant overlap to create non-binary risk scores
    timestamp = time.time()
    # Amount has a wide log-normal distribution
    amount = np.random.lognormal(mean=4, sigma=1.0) 
    avg_30d = np.random.uniform(50, 500)
    velocity = np.random.poisson(lam=3)
    distance = np.random.exponential(scale=15)
    
    # Categorical features
    location = np.random.choice(LOCATIONS)
    merchant = np.random.choice(MERCHANTS)
    habit = np.random.choice(SPENDING_HABITS)
    
    # Flags with some noise
    is_new_device = np.random.choice([0, 1], p=[0.98, 0.02])
    is_online = np.random.choice([0, 1], p=[0.4, 0.6])
    is_late_night = np.random.choice([0, 1], p=[0.85, 0.15])
    failed_attempts = np.random.choice([0, 1, 2], p=[0.99, 0.008, 0.002])

    # Inject fraud patterns with OVERLAP
    if is_fraud:
        # Some fraud is high amount, some is normal (stealthy)
        if np.random.random() > 0.3:
            amount *= np.random.uniform(3, 10)
            velocity += np.random.randint(5, 15)
            distance += np.random.uniform(200, 1000)
            is_new_device = np.random.choice([0, 1], p=[0.2, 0.8])
            failed_attempts = np.random.choice([0, 1, 2], p=[0.3, 0.4, 0.3])
        else:
            # Stealthy fraud: looks very similar to genuine
            amount *= np.random.uniform(1.1, 2.0)
            velocity += np.random.randint(1, 3)
            location = np.random.choice(LOCATIONS) # Random location
            
        location = np.random.choice(['London', 'New York', 'Dubai', 'Singapore'])
        merchant = np.random.choice(['Luxury', 'Electronics', 'Online Retail', 'Travel'])

    return {
        'Time': float(timestamp),
        'Amount': float(amount),
        'Location': str(location),
        'MerchantType': str(merchant),
        'SpendingHabit': str(habit),
        'Avg30dAmount': float(avg_30d),
        'Velocity24h': int(velocity),
        'DistanceFromHome': float(distance),
        'IsNewDevice': int(is_new_device),
        'IsOnline': int(is_online),
        'IsLateNight': int(is_late_night),
        'FailedAttempts': int(failed_attempts),
        'Class': int(is_fraud)
    }

def generate_bulk_data(num_records=5000):
    """Generates a bulk dataset for training."""
    data = [generate_transaction() for _ in range(num_records)]
    return pd.DataFrame(data)

def preprocess_df(df, le_dict=None, scaler=None):
    """Preprocesses a dataframe for model training or inference."""
    df_processed = df.copy()
    
    # Encode categorical features
    from sklearn.preprocessing import LabelEncoder
    
    cat_cols = ['Location', 'MerchantType', 'SpendingHabit']
    
    if le_dict is None:
        le_dict = {}
        for col in cat_cols:
            le = LabelEncoder()
            df_processed[col] = le.fit_transform(df_processed[col])
            le_dict[col] = le
    else:
        for col in cat_cols:
            # Handle unknown categories if any
            le = le_dict[col]
            df_processed[col] = df_processed[col].map(lambda x: x if x in le.classes_ else le.classes_[0])
            df_processed[col] = le.transform(df_processed[col])
            
    # Scale numerical features
    num_cols = ['Time', 'Amount', 'Avg30dAmount', 'Velocity24h', 'DistanceFromHome', 'FailedAttempts']
    
    if scaler is None:
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        df_processed[num_cols] = scaler.fit_transform(df_processed[num_cols])
    else:
        df_processed[num_cols] = scaler.transform(df_processed[num_cols])
        
    return df_processed, le_dict, scaler
