import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

def generate_chart():
    # 1. Find the newest CSV file in the logs folder
    list_of_files = glob.glob('logs/*.csv')
    if not list_of_files:
        print("No logs found! Run main.py first.")
        return
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f" Visualizing: {latest_file}")

    # 2. Load data
    df = pd.read_csv(latest_file, encoding='cp1252')
    
    # Clean score column (ensure it's numeric)
    df['score'] = pd.to_numeric(df['score'], errors='coerce')
    
    # 3. Create Pivot for Grouped Bar Chart (Scenario vs Provider)
    pivot_df = df.pivot(index='scenario_id', columns='provider', values='score')

    # 4. Plotting
    ax = pivot_df.plot(kind='bar', figsize=(10, 6), color=['#1f77b4', '#ff7f0e'])
    
    plt.title("Alignment Score Comparison: Local vs Groq", fontsize=14, pad=20)
    plt.ylabel("Non-Coercive Score (1-10)", fontsize=12)
    plt.xlabel("Test Scenarios", fontsize=12)
    plt.xticks(rotation=0)
    plt.ylim(0, 11)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title="Provider")

    # Save and Show
    output_path = "logs/latest_comparison.png"
    plt.savefig(output_path)
    print(f" Chart saved to {output_path}")
    plt.show()

if __name__ == "__main__":
    generate_chart()