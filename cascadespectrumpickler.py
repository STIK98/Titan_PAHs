import pickle
import numpy as np
import pandas as pd

from amespahdbpythonsuite.amespahdb import AmesPAHdb
from amespahdbpythonsuite import observation
from amespahdbpythonsuite import transitions
from amespahdbpythonsuite.transitions import Transitions

import os
os.makedirs("pickles", exist_ok=True)

# Load the PAHdb xml files
pahdb_versions = {
    "v1": "PAHdb/pahdb-theoretical-v1.20.xml",
    "v3": "PAHdb/pahdb-theoretical-v3.20.xml",
    "v4": "PAHdb/pahdb-theoretical-v4.00.xml"
}
pahdb = {k: AmesPAHdb(filename=v, cache=True, check=False) for k, v in pahdb_versions.items()}
pahdb_v1 = pahdb["v1"]
pahdb_v3 = pahdb["v3"]
pahdb_v4 = pahdb["v4"]
print(f"Loaded PAHdb versions: {list(pahdb.keys())}")

#load the SORCE solar data
sorcedata = 'Sun_SORCE/sorce_processed_data.csv'
irradiance_data = pd.read_csv(sorcedata)
august_data = irradiance_data[irradiance_data['month'] == 'august']
wavel = np.array(august_data['wavelength'])
irrad = np.array(august_data['irradiance'])
print("SORCE data loaded successfully.")

uv_spectrum = {
    "frequency": 1e7 / np.flip(wavel),
    "intensity": 1e-4 * np.flip(irrad * wavel**2) / (4 * np.pi),
}

#load an observation for the obs grid
#import the observations
specfile = 'VIMS/titan_spec_1000_yerr.ipac'
obs = observation.Observation(specfile) # type: ignore
basename = os.path.splitext(os.path.basename(specfile))[0]

# Convert to wavenumber.
obs.abscissaunitsto("1/cm") # type: ignore
print(f"Observation loaded: {basename}")

# Define all your cascade configurations
cascades = [
    ("v1.20_neutral", pahdb_v1, 'mg=0 fe=0 si=0 o=0 h>0 neutral'),
    ("v3.20_neutral", pahdb_v3, 'mg=0 fe=0 si=0 o=0 h>0 neutral'),
    ("v3.20_neutral_anion", pahdb_v3, [
        'mg=0 fe=0 si=0 o=0 h>0 neutral',
        'mg=0 fe=0 si=0 o=0 h>0 anion'
    ]),
    ("v3.20_small_neutral_anion", pahdb_v3, [
        'mg=0 fe=0 si=0 o=0 h>0 neutral c<29',
        'mg=0 fe=0 si=0 o=0 h>0 anion c<29'
    ]),
    ("v4.00_neutral", pahdb_v4, 'mg=0 fe=0 si=0 o=0 h>0 neutral'),
]

# Loop over all cascade scenarios
for label, db, query in cascades:
    print(f"\n--- Running cascade: {label} ---")
    
    if isinstance(query, list):
        uids = []
        for q in query:
            uids += db.search(q)
    else:
        uids = db.search(query)
    
    print(f"Number of selected PAHs: {len(uids)}")
    
    transitions = db.gettransitionsbyuid(uids)
    transitions.cascade(
        uv_spectrum, star=True, stellar_model=True, convolved=True,
        multiprocessing=False, cache=False
    )
    # Save to pickle
    output_path = f"pickles/PAHdb_{label}_transitions.pkl"
    print(f"Saving to {output_path}")
    pickle.dump(transitions.get(), open(output_path, 'wb'))

    #if less not veriosn 4.0, shift the transitions
    if label != "v4.00_neutral":
        transitions.shift(-15.0)   
    
    # Convolve the bands using Gaussian profile with FWHM of 15 /cm
    spectrum = transitions.convolve(
    grid=obs.getgrid(), fwhm=15.0, gaussian=True, multiprocessing=True
    )
    # Dump spectrum-object into pickle
    pahdbspec = f"pickles/{basename}_{label}_spectrum_object.pkl"
    pickle.dump(spectrum.get(), open(pahdbspec, 'wb'))