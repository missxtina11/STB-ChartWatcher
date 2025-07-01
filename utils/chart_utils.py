import matplotlib.pyplot as plt
import os
import tempfile
from typing import Optional

OUTPUT_DIR = os.getenv("CHART_OUTPUT_PATH") or tempfile.gettempdir()

def plot_holder_distribution(token_code: Optional[str] = None) -> str:
    """Placeholder pie-chart for token holder distribution."""
    holders = ["Top 1", "Top 2", "Others"]
    shares = [25, 15, 60]

    fig, ax = plt.subplots()
    ax.pie(shares, labels=holders, autopct="%1.1f%%")
    ax.set_title(f"{token_code or 'STB'} Holder Distribution")

    path = os.path.join(OUTPUT_DIR, f"{(token_code or 'STB').lower()}_holders_chart.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path

