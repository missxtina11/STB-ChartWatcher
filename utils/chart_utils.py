import matplotlib.pyplot as plt
import os
import tempfile
<<<<<<< HEAD

# Use CHART_OUTPUT_PATH from .env or system tmp
OUTPUT_DIR = os.getenv("CHART_OUTPUT_PATH") or tempfile.gettempdir()


def plot_holder_distribution(token: str) -> str:
    """
    Draw a simple pie chart for holder distribution.
    Replace dummy data with real stats when available.
    """
    holders = ["Top 1", "Top 2", "Others"]
    shares = [25, 15, 60]

    fig, ax = plt.subplots()
    ax.pie(shares, labels=holders, autopct="%1.1f%%")
    ax.set_title(f"{token} Holder Distribution")

    path = os.path.join(OUTPUT_DIR, f"{token}_holders_chart.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path

=======

# Where to save charts.
# 1) If CHART_OUTPUT_PATH exists in .env, use it
# 2) Otherwise fall back to the OS temp dir
OUTPUT_DIR = os.getenv("CHART_OUTPUT_PATH") or tempfile.gettempdir()

def plot_holder_distribution() -> str:
    """Create a sample holder-distribution pie chart and return the file path."""
    holders = ["Top 1", "Top 2", "Others"]
    shares  = [25, 15, 60]

    fig, ax = plt.subplots()
    ax.pie(shares, labels=holders, autopct="%1.1f%%")
    ax.set_title("STB Holder Distribution")

    path = os.path.join(OUTPUT_DIR, "holders_chart.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path

>>>>>>> 96bef16 (Fix chart path to use temp dir)
