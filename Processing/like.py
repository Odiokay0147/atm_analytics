import pandas as pd
import os
import matplotlib.pyplot as plt
from config.config import PROCESSED

OUTPUT = "charts"
os.makedirs(OUTPUT, exist_ok=True)

# =========================
# LOAD DATA (With Column Normalization)
# =========================
def load_data():
    files = [f for f in os.listdir(PROCESSED) if f.endswith(".csv")]
    all_data = []

    for file in files:
        path = os.path.join(PROCESSED, file)
        df = pd.read_csv(path)

        # fix column names and case
        df.columns = [c.strip().replace('_', ' ').title() for c in df.columns]
        
        # rename column name ATM
        df = df.rename(columns={
            'Atm Name': 'ATM Name',
            'No Of XYZ Card Withdrawals': 'No Of XYZ Card Withdrawals'
        })
        
        print(f"Loaded {file}. Columns found: {list(df.columns)}")
        all_data.append(df)

    full_df = pd.concat(all_data, ignore_index=True)
    return full_df

def preprocess(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.strftime('%b')
    df['Week'] = df['Date'].dt.isocalendar().week
    df['Weekday'] = df['Weekday'].str.strip().str.title()
    return df

# =========================
# UPDATED ANALYSIS & SAVING
# =========================
def save_yearly_charts(df, year):
    
    cols = df.columns
    total_withdrawals_col = 'No Of Withdrawals'
    total_amount_col = 'Total Amount Withdrawn'

    # 1. ATM EFFICIENCY (Transaction Size)
    if total_amount_col in cols and total_withdrawals_col in cols:
        plt.figure(figsize=(10, 5))
        # Avoid division by zero
        safe_df = df[df[total_withdrawals_col] > 0].copy()
        safe_df['Avg_Txn_Size'] = safe_df[total_amount_col] / safe_df[total_withdrawals_col]
        
        avg_size = safe_df.groupby('Month')['Avg_Txn_Size'].mean().reindex(["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
        avg_size.plot(kind='line', marker='s', color='darkblue', linewidth=2)
        plt.title(f"ATM Efficiency: Avg Withdrawal Size - {year} (Jan-Jun)")
        plt.ylabel("Average Amount per Transaction")
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT, f"efficiency_{year}.png"))
        plt.close()

    # 2. WORKING DAY ANALYSIS
    if 'Working Day' in cols:
        plt.figure(figsize=(8, 5))
        # Grouping by Working Day (Usually 0 for holiday/weekend, 1 for workday)
        workday_avg = df.groupby('Working Day')[total_withdrawals_col].mean()
        # Attempt to label index if it's numeric
        if all(x in workday_avg.index for x in [0, 1]):
            workday_avg.index = ['Holiday/Weekend', 'Working Day']
        
        workday_avg.plot(kind='bar', color=['#FFD700', '#4B5320']) # Gold and Olive
        plt.title(f"Average Daily Withdrawals: Work Day vs Holiday - {year}")
        plt.ylabel("Avg Number of Withdrawals")
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT, f"workday_impact_{year}.png"))
        plt.close()

    # 3. FESTIVAL ANALYSIS
    if 'Festival Religion' in cols:
        # Filter out rows where no festival is occurring (e.g., 'None', 'No Festival', or empty)
        fest_df = df[~df['Festival Religion'].isin(['None', 'no_festival', 'No Festival', ' '])].copy()
        
        if not fest_df.empty:
            plt.figure(figsize=(10, 6))
            fest_impact = fest_df.groupby('Festival Religion')[total_amount_col].sum().sort_values()
            fest_impact.plot(kind='barh', color='crimson')
            plt.title(f"Total Amount Withdrawn per Festival - {year}")
            plt.xlabel("Total Amount")
            plt.tight_layout()
            plt.savefig(os.path.join(OUTPUT, f"festival_impact_{year}.png"))
            plt.close()
        else:
            print(f"No active festivals found in Jan-Jun {year} data.")

    target_col = next((c for c in cols if 'Withdrawals' in c and 'XYZ' not in c and 'Other' not in c), cols[0])
    xyz_col = next((c for c in cols if 'Xyz' in c), None)
    other_col = next((c for c in cols if 'Other' in c), None)
    # monthly (Jan-Jun)
    plt.figure(figsize=(10, 6))
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    
    monthly = df.groupby('Month')[target_col].sum().reindex(month_order)
    monthly.plot(kind='bar', color='skyblue')
    plt.title(f"Monthly Transactions - {year} (Jan-Jun)")
    plt.savefig(os.path.join(OUTPUT, f"monthly_{year}.png"))
    plt.close()

    # weekly
    plt.figure(figsize=(10, 6))
    weekly = df.groupby('Week')[target_col].sum().sort_index()
    weekly = weekly[weekly.index <= 27]
    weekly.plot(kind='line', marker='o', color='green')
    plt.title(f"Weekly Transactions - {year}")
    plt.savefig(os.path.join(OUTPUT, f"weekly_{year}.png"))
    plt.close()

    # ATM Analysis 
    if 'ATM Name' in df.columns:
        plt.figure(figsize=(12, 6))
        atm = df.groupby('ATM Name')[target_col].sum().sort_values(ascending=False).head(10)
        atm.plot(kind='bar', color='orange')
        plt.title(f"Top 5 ATMs - {year}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT, f"atm_{year}.png"))
        plt.close()

    else:
        print(f"Skipping ATM chart for {year}: 'ATM Name' column not found.")

    # CARD TYPE ANALYSIS
    if xyz_col and other_col:
        plt.figure(figsize=(8, 5))
        xyz_total = df[xyz_col].sum()
        other_total = df[other_col].sum()
        
        card_series = pd.Series({'XYZ Card': xyz_total, 'Other Cards': other_total})
        card_series.plot(kind='bar', color=['navy', 'darkgrey'])
        
        plt.title(f"Card Usage Comparison - {year}")
        plt.ylabel("Total Count")
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT, f"card_comparison_{year}.png"))
        plt.close()
    else:
        print(f"Skipping Card Chart for {year}: Could not find XYZ or Other columns.")

def monthly_growth_chart(df):

    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

    # Pivot table for comparison
    pivot = df.pivot_table(
        values='No Of Withdrawals',
        index='Month',
        columns='Year',
        aggfunc='sum'
    ).reindex(month_order)

    plt.figure(figsize=(10,6))
    pivot.plot(kind='bar')

    plt.title("Monthly ATM Withdrawal Growth Comparison (Jan–Jun)")
    plt.xlabel("Month")
    plt.ylabel("Total Withdrawals")

    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT, "monthly_growth_comparison.png"))
    plt.close()

def main():
    df = load_data()
    df = preprocess(df)

    # Analyse by Month (Jan-Jun)
    target_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    df = df[df['Month'].isin(target_months)]
    
    # Filter by Week (1 to 27)
    df = df[df['Week'] <= 27]

    monthly_growth_chart(df)

    available_years = sorted(df['Year'].unique())
    
    for year in available_years:
        year_df = df[df['Year'] == year].copy()
        if not year_df.empty:
            save_yearly_charts(year_df, year)
            print(f"Generated charts for {year}")