# PAHs in Titan's Upper Atmosphere

Hi! Welcome to my repository, I'm honoured that you've taken an interest in my work. 

This repository contains code and data for my MSc thesis project "**Cosmis Carbon Clues:** Understanding the PAH population in Titan's upper atmosphere with IR spectroscopy". The project focuses on analysing Polycyclic Aromatic Hydrocarbons (PAHs) in the upper atmosphere (900 - 1000 km) of Titan using Cassini/VIMS spectra. Building from the work done by López-Puertas et al. (2013) [1], we utilise various spectral fitting techniques such as Non-Negative Least Squares (NNLS) and Least Chi Squared (NNLC), and Monte Carlo simulations. The goal is to identify and quantify PAHs by fitting the data with PAH emission models from the NASA Ames PAH IR Spectroscopic Database [2,3,4]. 

We use an adapted version of the AmesPAHdbPythonSuite, but or the original NASA Ames PAHdb, we refer you to the:
- Astrochem website: https://www.astrochem.org/pahdb/
- Original PAHdb PythonSuite repository (for review, not download!): https://github.com/PAHdb/AmesPAHdbPythonSuite
- PythonSuite Documentation: https://pahdb.github.io/AmesPAHdbPythonSuite/index.html

The changes we made are the following:
1. Update the Photon Absorption Cross section to reflect the latest research by Mattioda et al. 2008. [5]
2. Make it possible to choose NNLS or NNLC fitting, regardless of wheter uncertainties are available for the data
3. Add in a reduced $\chi^2$ calculation for each fit
4. Include the option to normalise the PAHs that go into the fit to unity, instead of to the hightst signal.

For an explination on why we did this, read the thesis methods' section.

All the changes are saved in a forked version of the original repository: https://github.com/STIK98/AmesPAHdbPythonSuite_forked/tree/feature/norm-per-pah. This branch is synced with the original PAHdb repository up to April 2025. For a version that is up to date with the original database on July 1st 2025 you can use the following branch (with caution, because it has not been tested extensively): https://github.com/STIK98/AmesPAHdbPythonSuite_forked/tree/combined. 



## Key Components:
The repository contains the following elements:

### VIMS:
This directory contains the CH$_4$-subtracted VIMS spectra from Dinelli et al. (2011) [6]. We converted the signals from radiance (nW m$^{−2}$ sr$^{−1} nm$^{−1}) to Jy/sr, because PAHdb only accepts data in terms of Hz.

### Sun_SORCE
This directory contains the SORCE data from July 19 and August 31 2007. The difference between the two dates is not significant so we use only Augst 31 in cascade emission model. 

### PAHdb
This is an **empty repository!** If you want to run the code in its interity you need to download version 1.20, 3.20, and 4.00 from the Astrochem website (https://www.astrochemistry.org/pahdb/theoretical/3.20/download/view) and input them in this directory. We did not include them due to storage capacity.

### other Files:
- cascadespectrumpickler.py: this is the python scripts that runs the cascade emission model from the NASA Ames PAHdb Python Suite with the SORCE data as the activating energy. This script is **computationally very expensive** and takes a long time to run on a normal computer with limited CPU capacity (+24 hours). We used a cluster to run these calculation and significanlty reduce the time to only a few hours. The cascades are pickled for use later.
- Workbook_withpickles.ipynb: In this notebook we perform the analysis. We import the cascade pickles made in the previous script and use it to model the pah signal as we would expect it to be in Titan's upper atmosphere. We make NNLS, NNLC, and Monte Carlo fits for all the heights and all the different versions of the database we want to test. Results are output into a "final_results" directory that is made when you run the script.
- uid_molecular_formula_mapping.csv: out of the graciousness of my heart (and because I got a little bit annoyed by never knowing the UID to Chemical Formula conversion, I made an excel sheet that maps all the UIDs in this research (4919) to the corresponding formula, so you can look it up while you work. 

### Methods:
- NNLS Fitting: Used for fast, non-negative fitting of spectral data.
- Monte Carlo Simulations: Applied to explore uncertainties and probabilistic fitting.

### Objectives:
- Investigate how PAHs form and evolve in Titan’s atmosphere.
- Correlate PAH concentrations with the atmospheric composition and conditions observed by Cassini.
- Publish findings in a comprehensive thesis and contribute to the ongoing research on Titan's atmosphere.

## Contributions

Feel free to submit issues or pull requests if you'd like to contribute to this project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
