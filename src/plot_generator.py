import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
from datetime import datetime

def generate_karma_plot():
    """Generate a plot of karma points over time."""
    # Set style
    sns.set_theme(style="darkgrid")

    # Load karma history
    data_dir = Path(__file__).parent.parent / 'data'
    history_file = data_dir / 'karma_history.json'

    with open(history_file, 'r') as f:
        history = json.load(f)

    # Convert to DataFrame
    df = pd.DataFrame(history)
    df['date'] = pd.to_datetime(df['date'])

    # Create plot
    plt.figure(figsize=(12, 7))

    # Plot line with points
    sns.lineplot(data=df, x='date', y='karma', marker='o', color='#FF6B6B')

    # Add title and labels
    plt.title('Hacker News Karma History', pad=20, size=14, weight='bold')
    plt.xlabel('Date', size=12)
    plt.ylabel('Karma Points', size=12)

    # Customize grid
    plt.grid(True, linestyle='--', alpha=0.7)

    # Rotate x-axis labels
    plt.xticks(rotation=45)

    # Add annotations
    latest_karma = df['karma'].iloc[-1]
    plt.annotate(f'Latest: {latest_karma}',
                xy=(df['date'].iloc[-1], latest_karma),
                xytext=(10, 10),
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='#FFE66D', alpha=0.5),
                arrowprops=dict(arrowstyle='->', color='#4ECDC4'))

    # Add metadata
    plt.figtext(0.99, 0.01, f'Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                ha='right', va='bottom', size=8, style='italic')

    # Add min/max annotations
    min_karma = df['karma'].min()
    max_karma = df['karma'].max()
    min_date = df.loc[df['karma'] == min_karma, 'date'].iloc[0]
    max_date = df.loc[df['karma'] == max_karma, 'date'].iloc[0]

    plt.annotate(f'Min: {min_karma}',
                xy=(min_date, min_karma),
                xytext=(0, -20),
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='#FF6B6B', alpha=0.5),
                arrowprops=dict(arrowstyle='->'),
                ha='center')

    plt.annotate(f'Max: {max_karma}',
                xy=(max_date, max_karma),
                xytext=(0, 20),
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='#4ECDC4', alpha=0.5),
                arrowprops=dict(arrowstyle='->'),
                ha='center')

    # Adjust layout
    plt.tight_layout()

    # Save plot
    images_dir = Path(__file__).parent.parent / 'images'
    images_dir.mkdir(exist_ok=True)
    plt.savefig(images_dir / 'karma_plot.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

if __name__ == "__main__":
    generate_karma_plot()