import os
import pandas as pd
import numpy as np
from amespahdbpythonsuite import observation
from amespahdbpythonsuite.amespahdb import AmesPAHdb
import json

#--- PAHdb loading ---#
# Get the absolute path to the script directory (helios)
base_path = os.path.dirname(os.path.abspath(__file__))
pahdb_folder = os.path.join(base_path, "PAHdb")

# Ask the user which PAHdb version they want
version_choice = input("Choose PAHdb version (1.20 or 3.20): ").strip()

# Set the correct file path based on user input
if version_choice == "1.20":
    xml_file = os.path.join(pahdb_folder, "pahdb-theoretical-v1.20.xml")
elif version_choice.lower() in ["3.20", "3"]:
    xml_file = os.path.join(pahdb_folder, "pahdb-theoretical-v3.20.xml")
else:
    print("Invalid input. Defaulting to version 3.20.")
    xml_file = os.path.join(pahdb_folder, "pahdb-theoretical-v3.20.xml")

# Load the selected PAHdb version
pahdb = AmesPAHdb(
    filename=xml_file,
    check=True,
    cache=True,
)

#--- PAH search ---#
neutral_choice = input("Include 'neutral' in PAH search? (yes/no): ").strip().lower()

# Build the search query dynamically
search_query = "mg=0 fe=0 si=0 o=0 h>0 c>300"
if neutral_choice in ["yes", "y"]:
    search_query = "neutral " + search_query

# Perform the search
uids = pahdb.search(search_query)
transitions = pahdb.gettransitionsbyuid(uids)

#--- Cascade the PAHs with the solar spectrum ---#
solar_folder = os.path.join(base_path, "Sun_SORCE")
csv_path = os.path.join(solar_folder, 'sorce_processed_data.csv')

irradiance_data = pd.read_csv(csv_path)
august_data = irradiance_data[irradiance_data['month'] == 'august']
wavel = np.array(august_data['wavelength'])
irrad = np.array(august_data['irradiance'])
print("Data loaded successfully.")

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

#--- Observation data ---#
obs_path = os.path.join(base_path, "VIMS")
heights = [900, 950, 1000]  # Heights to iterate over

# Ask user for Monte Carlo sample sizes (allowing multiple)
sample_input = input("Enter Monte Carlo sample sizes (comma-separated, e.g., 500,1000,2000): ").strip()

# Convert input to a list of integers
sample_sizes = [int(s) for s in sample_input.split(",")]

#--- Compute the spectrum ONCE ---#
obs_example = observation.Observation(os.path.join(obs_path, f"titan_spec_1000_yerr.ipac"))  # Use one file for the grid
obs_example.abscissaunitsto("1/cm")
spectrum = transitions.convolve(grid=obs_example.getgrid(), fwhm=15.0, multiprocessing=False)

#--- Run MC fit for each sample size and height ---#
results = {}  # Store results for each sample size and height
for samples in sample_sizes:
    print(f"Running MC fit with {samples} samples.")

    for height in heights:
        data_file = os.path.join(obs_path, f"titan_spec_{height}_yerr.ipac")

        if not os.path.exists(data_file):
            print(f"Warning: Data file for height {height} km not found: {data_file}")
            continue

        print(f"Processing MC fitting for height: {height} km with {samples} samples.")

        # Load observation data
        obs = observation.Observation(data_file)
        obs.abscissaunitsto("1/cm")

        # Run Monte Carlo fitting
        mc_fit = spectrum.mcfit(obs, samples=samples, multiprocessing=False)

        # Extract the results properly
        fit_results = mc_fit.get()  # Extracts the fit dictionary

        # Remove 'observation' key if it exists
        fit_results.pop("observation", None)  # This safely removes the key without errors
        fit_results.pop("distribution", None)  # Remove the distribution data
        fit_results.pop("type", None)  # Remove the type data

        # Store only the necessary data
        if height not in results:
            results[height] = {}
        
        results[height][samples] = fit_results  # Store the extracted fit data

print("Finished all MC fits.")

#--- Save the results to a JSON file ---#
version_tag = f"v{version_choice.replace('.', '')}"  # e.g., "v320"
neutral_tag = "neutral" if neutral_choice in ["yes", "y"] else "ions"
sample_tag = "".join(map(str, sample_sizes))  # Convert list [500, 1000, 2000] → "50010002000"

output_filename = f"mcfit_{version_tag}_{neutral_tag}_{sample_tag}.json"
output_file = os.path.join(base_path, output_filename)

with open(output_file, "w") as f:
    json.dump(results, f, indent=4)

print(f"Saved results to {output_file}")