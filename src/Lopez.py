#This file compiles the cascade of the PAHs on Titan's atmosphere
import numpy as np
from amespahdbpythonsuite import observation
from amespahdbpythonsuite.amespahdb import AmesPAHdb
import matplotlib.pyplot as plt
from SORCE import collect_irradiance_data # type: ignore
import pandas as pd
from astropy.table import Table

class PAHPipeline:
    """
    A pipeline to process and analyze PAHs for Titan's atmosphere.
    Manages all intermediate steps (PAHdb loading, filtering, cascading, etc.)
    and avoids redundant computations through lazy evaluation.
    """
    def __init__(self, version="1.20", height=1000, filter_version="short"):
        self.version = version
        self.height = height
        self.filter_version = filter_version
        self.pahdb_instance = None
        self.transitions = None
        self.obs = None
        self.irradiance_data = None
        self.spectrum = None
        self.PAH_fit = None

    def get_pahdb_instance(self):
        if self.pahdb_instance is None:
            self.pahdb_instance = pahdb(version=self.version)
        return self.pahdb_instance

    def get_observations(self):
        if self.obs is None:
            self.obs = observations(height=self.height)
        return self.obs

    def get_transitions(self):
        if self.transitions is None:
            self.transitions = uidfilter(self.get_pahdb_instance(), version=self.filter_version)
        return self.transitions

    def get_irradiance_data(self):
        if self.irradiance_data is None:
            self.irradiance_data = collect_irradiance_data()
        return self.irradiance_data

    def get_spectrum(self):
        if self.spectrum is None:
            transitions, spectrum = cascade_PAHs(
                transitions=self.get_transitions(),
                obs=self.get_observations(),
                irradiance_data=self.get_irradiance_data()
            )
            self.transitions = transitions
            self.spectrum = spectrum
        return self.spectrum

    def run_fit(self):
        if self.PAH_fit is None:
            self.PAH_fit = fit_spectrum(self.get_spectrum(), self.get_observations())
        return self.PAH_fit

    def fit_new_height(self, new_height):
        """
        Fit the precomputed spectrum to a new observation at a different height.
        Avoids recalculating the cascade.
        """
        new_obs = observations(height=new_height)
        return fit_spectrum(self.get_spectrum(), new_obs)


#1. Import the PAH database from NASA Ames xml file
def pahdb(version: str = "1.20", base_path: str = "/Users/floorstikkelbroeck/Documents/Titan/PAHdb/") -> AmesPAHdb:
    """
    Load in the PAHdb with the specified version. Defaults to version 1.20.
    """
    if version == "1.20":
        xml_file = f"{base_path}pahdb-theoretical-v1.20.xml"
    else:
        xml_file = f"{base_path}pahdb-theoretical.xml"

    pahdb = AmesPAHdb(
        filename=xml_file,
        check=False,
        cache=True,
    )
    return pahdb

#2. Filter the PAH database for neutral PAHs, or choose a specific set of PAHs for faster cascade
def uidfilter(pahdb: AmesPAHdb, version: str = "short"):
    """
    Filter the PAHdb for neutral PAHs. Defaults to 'one'.
    """
    if version == 'long':
        uids = pahdb.search("neutral mg=0 fe=0 si=0 o=0 h>0")
        transitions = pahdb.gettransitionsbyuid(uids)
    elif version == 'short':
        transitions = pahdb.gettransitionsbyuid([143, 527, 356, 174, 276, 493, 299, 149, 108, 473, 600, 333, 385, 105, 519, 267, 159, 339, 358])
    else:
        transitions = pahdb.gettransitionsbyuid([108])
    return transitions

#3. Read observation data from Titan's atmosphere at the given tangent height
def observations(height: float = 1000, base_path: str = "/Users/floorstikkelbroeck/Documents/Titan/") -> observation:
    """
    Read observation data from Titan's atmosphere at the given tangent height.
    Defaults to height 900.
    """
    data_files = {
        900: f"{base_path}titan_spec_900_yerr.ipac",
        950: f"{base_path}titan_spec_950_yerr.ipac",
        1000: f"{base_path}titan_spec_1000_yerr.ipac",
    }
    data_file = data_files.get(height, data_files[1000])  # Default to height 1000 if height is invalid

    obs = observation.Observation(data_file)
    obs.abscissaunitsto("1/cm")  # Convert the wavelength to wavenumbers
    return obs

#4. Cascade the PAHs in the PAHdb with a given energy from the solar spectrum
def cascade_PAHs(transitions=None, obs=None, irradiance_data=None, pahdb_instance=None):
    """
    Cascade the PAHs in the PAHdb with a given energy from the solar spectrum.
    If no parameters are provided, standardized defaults are used.
    Returns the processed transitions and spectrum.
    """
    # Standardized defaults
    if transitions is None:
        if pahdb_instance is None:
            pahdb_instance = pahdb()  # Load the default PAHdb instance
        transitions = uidfilter(pahdb_instance)  # Default filtering

    if obs is None:
        obs = observations()  # Default observation data

    if irradiance_data is None:
        irradiance_data = collect_irradiance_data()  # Default solar irradiance

    # Process the UV spectrum
    wavel = np.array(irradiance_data['august']['wavelengths'])
    irrad = np.array(irradiance_data['august']['irradiances'])

    uv_spectrum = {
        "frequency": 1e7 / np.flip(wavel),
        "intensity": 1e-4 * np.flip(irrad * wavel**2) / (4 * np.pi),
    }

    # Cascade the UV spectrum
    transitions.cascade(
        uv_spectrum, star=True, stellar_model=True, convolved=True, 
        multiprocessing=False, cache=True
    )
    transitions.shift(-15.0)
    spectrum = transitions.convolve(grid = obs.getgrid(), fwhm=15.0, multiprocessing=False)

    # Return both transitions and spectrum
    return transitions, spectrum

#5. Fit the spectrum to the observation data
def fit_spectrum(spectrum: AmesPAHdb, obs: observation) -> AmesPAHdb:
    """
    Fit the spectrum to the observation data.
    """
    PAH_fit = spectrum.fit(obs)
    return PAH_fit

#6. Run the full analysis pipeline with customizable parameters
def run_analysis(version: str = "1.20", height: float = 900, filter_version: str = "one"):
    """
    Run the full analysis pipeline with customizable parameters.
    Returns the final fit result.
    """
    pipeline = PAHPipeline(version=version, height=height, filter_version=filter_version)
    return pipeline.run_fit()


if __name__ == "__main__":
    fit = run_analysis()