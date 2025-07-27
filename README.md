# PAHs in Titan's Atmosphere

Hi! Welcome to my repository, I'm honoured that you've taken an interest in my work. 

This repository contains code and data for my MSc thesis project "**Cosmis Carbon Clues:** Understanding the PAH population in Titan's upper atmosphere with IR spectroscopy". The project focuses on analysing Polycyclic Aromatic Hydrocarbons (PAHs) in the upper atmosphere (900 - 1000 km) of Titan using Cassini/VIMS spectra. Building from the work done by López-Puertas et al. (2013), we utilise various spectral fitting techniques such as Non-Negative Least Squares (NNLS) and Least Chi Squared (NNLC), and Monte Carlo simulations. The goal is to identify and quantify PAHs by fitting the data with PAH emission models from the NASA Ames PAH IR Spectroscopic Database. 

We use an adapted version of the AmesPAHdbPythonSuite, but or the original NASA Ames PAHdb, we refer you to the:
- Astrochem website: https://www.astrochem.org/pahdb/
- Original PAHdb PythonSuite repository (for review, not download!): https://github.com/PAHdb/AmesPAHdbPythonSuite
- PythonSuite Documentation: https://pahdb.github.io/AmesPAHdbPythonSuite/index.html

The changes we made are the following:
1. Update the Photon Absorption Cross section to reflect the latest research by Mattioda et al. 2008.
2. Make it possible to choose NNLS or NNLC fitting, regardless of wheter uncertainties are available for the data
3. Add in a reduced $\chi^2$ calculation for each fit
4. Include the option to normalise the PAHs that go into the fit to unity, instead of to the hightst signal.

For an explination on why we did this, read the thesis methods' section.

All the changes are saved in a forked version of the original repository: https://github.com/STIK98/AmesPAHdbPythonSuite_forked/tree/feature/norm-per-pah. This branch is synced with the original PAHdb repository up to April 2025. For a version that is up to date with the original database on July 1st 2025 you can use the following branch (with caution, because it has not been tested extensively): https://github.com/STIK98/AmesPAHdbPythonSuite_forked/tree/combined. 



## Key Components:
### Data:
- Cassini VIMS-IR and CIRS observational data.
- Expanded NASA Ames PAH IR Database for spectral matching.

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
