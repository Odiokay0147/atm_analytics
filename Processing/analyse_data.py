import pandas as pd
import os
import matplotlib.pyplot as plt
from config.config import PROCESSED


# =========================
# LOAD DATA
# =========================
def load_data():
    files = [f for f in os.listdir(PROCESSED) if f.endswith(".csv")]

    all_data = []

    for file in files:
        path = os.path.join(PROCESSED, file)
        df = pd.read_csv(path)
        all_data.append(df)

    full_df = pd.concat(all_data, ignore_index=True)

    print("Data Loaded Successfully:", full_df.shape)

    return full_df


# =========================
# PREPROCESS
# =========================
def preprocess(df):
    df['Date'] = pd.to_datetime(df['Date'])

    df['Month'] = df['Date'].dt.strftime('%b')
    df['Week'] = df['Date'].dt.isocalendar().week
    df['Year'] = df['Date'].dt.year

    df['Weekday'] = df['Weekday'].str.strip().str.title()

    return df


# =========================
# ANALYSIS
# =========================
def monthly_analysis(df):
    month_order = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun"
    ]
    result = df.groupby('Month')['No Of Withdrawals'].sum().reindex(month_order)
    print("\nMonthly Transactions:\n", result)
    return result


def weekly_analysis(df):
    result = df.groupby('Week')['No Of Withdrawals'].sum().sort_index()
    print("\nWeekly Transactions:\n", result)
    return result


def card_analysis(df, year):
    xyz = df['No Of XYZ Card Withdrawals'].sum()
    other = df['No Of Other Card Withdrawals'].sum()

    print(f"\n--- Card Usage (Jan-Jun {year}) ---")
    print("XYZ Card:, {xyz}")
    print("Other Cards:, {other}")


def atm_analysis(df):
    result = df.groupby('ATM Name')['No Of Withdrawals'].sum().sort_values(ascending=False)
    print("\nTop ATMs:\n", result.head(10))
    return result


def weekday_analysis(df):
    weekday_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]
    result = df.groupby('Weekday')['No Of Withdrawals'].sum().reindex(weekday_order)
    print("\nWeekday Usage:\n", result)
    return result


# =========================
# PLOTTING
# =========================
def plot_chart(data, title, chart_type="bar"):
    if data.empty: 
        return
    fig = plt.figure(figsize=(8, 4))

    if chart_type == "line":
        data.plot(kind="line", marker='o')
    else:
        data.plot(kind='bar')
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# =========================
# MAIN FUNCTION
# =========================
def main():
    df = load_data()
    df = preprocess(df)
    #ppp
    target_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    df = df[df['Month'].isin(target_months)]

    years = sorted(df['Year'].unique())

    for year in years:
        print(f"\n{'='*40}")
        print(f" ANALYZING: JAN - JUN {year} ")
        print(f"{'='*40}")

        year_df = df[df['Year'] == year]

        if year_df.empty:
            print(f"No data found for {year}")
            continue

    monthly = monthly_analysis(year_df)
    plot_chart(monthly, f"Monthly Transactions (Jan-Jun {year})")

    weekly = weekly_analysis(year_df)
    plot_chart(weekly, f"Weekly Transactions (Jan-Jun {year})", chart_type="line")

    card_analysis(year_df, year)

    atm = atm_analysis(df)
    plot_chart(atm.head(10), f"Top 10 ATMs (Jan-Jun {year})")

    weekday = weekday_analysis(df)
    plot_chart(weekday, f"Weekday Transactions (Jan-Jun {year})")