import matplotlib.pyplot as plt

def apply_thesis_style():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',  # Dyslexia-friendly sans-serif font
        'font.size': 12,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'lines.linewidth': 2,
        'lines.markersize': 3.5,
        'figure.dpi': 100
    })

def apply_presentation_style():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',  # Dyslexia-friendly sans-serif font
        'font.size': 16,
        'axes.labelsize': 18,
        'xtick.labelsize': 16,
        'ytick.labelsize': 16,
        'legend.fontsize': 16,
        'axes.titlesize': 18,
        'lines.linewidth': 2.5,
        'lines.markersize': 8,
        'figure.dpi': 100,
    })
