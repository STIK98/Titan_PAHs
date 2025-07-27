# PAHs in Titan's Upper Atmosphere

Hi! Welcome to my repository, I'm honoured that you've taken an interest in my work.

This repository contains code and data for my MSc thesis project "**Cosmic Carbon Clues:** Understanding the PAH population in Titan's upper atmosphere with IR spectroscopy". The project focuses on analysing Polycyclic Aromatic Hydrocarbons (PAHs) in the upper atmosphere (900 – 1000 km) of Titan using Cassini/VIMS spectra. Building from the work done by López-Puertas et al. (2013) \[1], we use spectral fitting techniques such as Non-Negative Least Squares (NNLS), Non-Negative Least Chi-Squared (NNLC), and Monte Carlo simulations. The goal is to identify and quantify PAHs by fitting the data with PAH emission models from the NASA Ames PAH IR Spectroscopic Database \[2, 3, 4].

We use an adapted version of the AmesPAHdbPythonSuite, but for the original NASA Ames PAHdb, we refer you to:

* Astrochem website: [https://www.astrochem.org/pahdb/](https://www.astrochem.org/pahdb/)
* Original PAHdb PythonSuite repository (for review, not download!): [https://github.com/PAHdb/AmesPAHdbPythonSuite](https://github.com/PAHdb/AmesPAHdbPythonSuite)
* PythonSuite Documentation: [https://pahdb.github.io/AmesPAHdbPythonSuite/index.html](https://pahdb.github.io/AmesPAHdbPythonSuite/index.html)

The changes we made are:

1. Updated the photon absorption cross-section to reflect the latest research by Mattioda et al. 2008 \[5]
2. Made it possible to choose NNLS or NNLC fitting, regardless of whether uncertainties are available for the data
3. Added a reduced χ² calculation for each fit
4. Included the option to normalise the PAHs in the fit to unity instead of to the highest signal

For an explanation of why we did this, see the Methods section of the thesis.

All changes are saved in a forked version of the original repository:
[https://github.com/STIK98/AmesPAHdbPythonSuite\_forked/tree/feature/norm-per-pah](https://github.com/STIK98/AmesPAHdbPythonSuite_forked/tree/feature/norm-per-pah)
This branch is synced with the original PAHdb repository up to April 2025.
For a version up to date with the original database as of July 1st 2025, use the following branch (with caution, as it has not been tested extensively):
[https://github.com/STIK98/AmesPAHdbPythonSuite\_forked/tree/combined](https://github.com/STIK98/AmesPAHdbPythonSuite_forked/tree/combined)

## Key Components

The repository contains the following elements:

### VIMS

This directory contains the CH₄-subtracted VIMS spectra from Dinelli et al. (2011) \[6].
We converted the signals from radiance (nW·m⁻²·sr⁻¹·nm⁻¹) to Jy/sr because PAHdb only accepts data in terms of Hz.

### Sun\_SORCE

This directory contains the SORCE data from July 19 and August 31 2007.
The difference between the two dates is not significant, so we use only August 31 in the cascade emission model.

### PAHdb

This is an **empty directory!** If you want to run the code in its entirety you need to download versions 1.20, 3.20, and 4.00 from the Astrochem website ([https://www.astrochemistry.org/pahdb/theoretical/3.20/download/view](https://www.astrochemistry.org/pahdb/theoretical/3.20/download/view)) and put them in this directory. We did not include them due to storage constraints.

### Other files

* `cascadespectrumpickler.py`: Python script that runs the cascade emission model from the NASA Ames PAHdb Python Suite using SORCE data as the activating energy.
  **Note:** This script is computationally very expensive and takes over 24 hours on a normal computer. We used a cluster to reduce the time to a few hours. The resulting cascades are saved (pickled) for later use.
* `Workbook_withpickles.ipynb`: Jupyter notebook for the analysis. It imports the cascade pickles, models the expected PAH signal in Titan's upper atmosphere, and performs NNLS, NNLC, and Monte Carlo fits for all heights and database versions. Results are saved in a `final_results` directory created by the script.
* `uid_molecular_formula_mapping.csv`: An Excel sheet mapping all 4919 UIDs in this research to their chemical formulas for convenience.
* MSc Thesis: Thesis document and supporting files.

## Workflow

1. Download the forked repository branch and required packages (see original repository documentation linked above)
2. Download the required PAHdb versions (linked above)
3. Download this repository
4. Run `cascadepickler.py` to generate all cascade emissions
5. Use `Workbook_withpickles.ipynb` to make the fits and generate results

Happy coding! If you have any questions or comments, please contact me at [fj.stik@hotmail.com](mailto:fj.stik@hotmail.com).

## Bibliography

## Bibliography

[1] López-Puertas, Manuel, et al. "Large abundances of polycyclic aromatic hydrocarbons in Titan's upper atmosphere." *The Astrophysical Journal* 770.2 (2013): 132.  

[2] Bauschlicher, C. W., Jr., Ricca, A., Boersma, C., Allamandola, L. J. "The NASA Ames PAH IR Spectroscopic Database: Computational Version 3.00 with Updated Content and the Introduction of Multiple Scaling Factors." *The Astrophysical Journal Supplement Series*, 234, 32 (2018).  

[3] Boersma, C., Bauschlicher, C. W., Jr., Ricca, A., Mattioda, A. L., Cami, J., Peeters, E., Sánchez de Armas, F., Puerta Saborido, G., Hudgins, D. M., Allamandola, L. J. "The NASA Ames PAH IR Spectroscopic Database Version 2.00: Updated Content, Website and On/Offline Tools." *The Astrophysical Journal Supplement Series*, 211, 8 (2014).  

[4] Mattioda, A. L., Hudgins, D. M., Boersma, C., Ricca, A., Peeters, E., Cami, J., Sánchez de Armas, F., Puerta Saborido, G., Bauschlicher, C. W., Jr., Allamandola, L. J. "The NASA Ames PAH IR Spectroscopic Database: The Laboratory Spectra." *The Astrophysical Journal Supplement Series*, 251, 22 (2020).  

[5] Mattioda, Andrew L., et al. "Near-infrared spectroscopy of nitrogenated polycyclic aromatic hydrocarbon cations from 0.7 to 2.5 μm." *The Astrophysical Journal* 680.2 (2008): 1243.  

[6] Dinelli, B. M., et al. "An unidentified emission in Titan's upper atmosphere." *Geophysical Research Letters* 40.8 (2013): 1489–1493.  


## Contributions
Feel free to submit issues or pull requests if you'd like to contribute to this project. Many thanks to Dr. Alessandra Candian and Prof. Dr. Manuel López-Puertas for their help.

## License
This project is licensed under the MIT License – see the LICENSE file for details.
