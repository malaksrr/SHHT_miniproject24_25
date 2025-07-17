import pandas as pd
import numpy as np
import os
np.random.seed(42)

def generate_custom_hours(low, high, preferred_range, n_samples):
    """Generate hours with a preferred distribution in the middle."""
    values = np.random.uniform(low, high, n_samples * 3)
    mask = (values >= preferred_range[0]) & (values <= preferred_range[1])
    preferred = values[mask]
    
    # Mix some extreme values too for realism
    extremes = np.random.uniform(low, high, n_samples - len(preferred))
    combined = np.concatenate([preferred[:n_samples - len(extremes)], extremes])
    return np.round(np.random.choice(combined, n_samples, replace=False), 1)

def generate_student_data(n_samples):
    # Custom-distributed values
    study_hours = generate_custom_hours(1, 20, (6, 10), n_samples)
    sleep_hours = generate_custom_hours(2, 15, (6, 8), n_samples)
    break_frequency = np.random.randint(5, 61, size=n_samples)
    concentration_level = np.random.randint(1, 6, size=n_samples)

    data = []

    for i in range(n_samples):
        s = study_hours[i]
        sl = sleep_hours[i]
        b = break_frequency[i]
        c = concentration_level[i]

        # Burnout risk formula
        burnout_risk = (
            5.5 * s
            - 4.5 * sl
            + 0.3 * (60 - b)
            + 7 * (5 - c)
            + np.random.normal(0, 6)
        )

        burnout_risk = np.clip(burnout_risk, 0, 100)

        data.append([
            s, sl, b, c, round(burnout_risk, 2)
        ])

    df = pd.DataFrame(data, columns=[
        "study_hours", "sleep_hours", "break_frequency", "concentration_level", "burnout_risk"
    ])
    return df

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'burnout_data.csv')

# === Generate and save ===
df = generate_student_data(15000)

# Ensure the directory exists
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

# Save the file
df.to_csv(DATA_PATH, index=False)
print(df.head())