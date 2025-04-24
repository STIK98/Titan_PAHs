import os
import pandas as pd
import numpy as np
from amespahdbpythonsuite import observation
from amespahdbpythonsuite.amespahdb import AmesPAHdb
import pickle

def convert_to_serializable(obj):
    """Convert non-pickleable objects (numpy types) into a saveable format."""
    if isinstance(obj, (np.float64, np.float32)):  
        return float(obj)  # Convert NumPy float to standard Python float
    elif isinstance(obj, (np.int64, np.int32)):  
        return int(obj)  # Convert NumPy int to standard Python int
    elif isinstance(obj, dict):  # Recursively process dictionaries
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):  # Recursively process lists
        return [convert_to_serializable(i) for i in obj]
    else:
        return obj  # Leave everything else unchanged

if __name__ == "__main__":
    # --- Cluster Parameters (No User Input) ---
    version_choice = "3.20"  # Use version 1.20 for this run
    neutral_choice = "test_random_mc"  # Only neutral PAHs
    # sample_sizes = [10,20,50,100,200,500,1000,2000,5000,10000]  # Monte Carlo runs
    sample_sizes = [10]  # For testing purposes
    # --- PAHdb Loading ---
    base_path = os.path.dirname(os.path.abspath(__file__))
    pahdb_folder = os.path.join(base_path, "PAHdb")

    # Construct file path based on the selected version
    xml_file = os.path.join(pahdb_folder, f"pahdb-theoretical-v{version_choice}.xml")

    # Ensure the file exists, otherwise raise an error
    if not os.path.isfile(xml_file):
        raise FileNotFoundError(f"⚠️ PAHdb file {xml_file} not found. Please check the file path.")

    # Load PAHdb
    pahdb = AmesPAHdb(
        filename=xml_file,
        check=True,
        cache=True,
    )

    # --- PAH Search ---
    search_query1 = "mg=0 fe=0 si=0 o=0 h>0 neutral c<50"  # Only cationic PAHs

    # Perform the search
    uids1 = pahdb.search(search_query1)

    search_query2 = "mg=0 fe=0 si=0 o=0 h>0 anion c<50"  # Only neutral PAHs
    uids2 = pahdb.search(search_query2)
    transitions = pahdb.gettransitionsbyuid(uids1 + uids2)

    # --- Cascade the PAHs with the Solar Spectrum ---
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

    # --- Observation Data ---
    obs_path = os.path.join(base_path, "VIMS")
    heights = [900, 950, 1000]  # Heights to iterate over

    # Compute the spectrum ONCE (uses grid from 1000 km observation)
    obs_example = observation.Observation(os.path.join(obs_path, f"titan_spec_1000_yerr.ipac"))
    obs_example.abscissaunitsto("1/cm")
    spectrum = transitions.convolve(grid=obs_example.getgrid(), fwhm=15.0, multiprocessing=False)

    # --- Run MC Fit for Each Sample Size and Height ---
    results = {}  # Store results

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
            mc_fit = spectrum.mcfit_randomized(obs, samples=samples, normalization='max', subset_size=50)

            # Extract results
            fit_results = mc_fit.get()

            for fit, result_dict in zip(mc_fit.mcfits, fit_results["mcfits"]):
                result_dict["redchi2"] = fit.redchi2

            # Remove unnecessary keys
            for key in ["observation", "distribution", "type"]:
                fit_results.pop(key, None)

            # Store results
            if height not in results:
                results[height] = {}
            
            results[height][samples] = fit_results

    print("Finished all MC fits.")
    results_folder = os.path.join(base_path, "results")
    os.makedirs(results_folder, exist_ok=True)  # Ensure results folder exists

    output_filename = f"mcfit_{version_choice}_{neutral_choice}_{sample_sizes}.pkl"
    output_file = os.path.join(results_folder, output_filename)

    for height in results:
        for sample in results[height]:
            for mcfit in results[height][sample]["mcfits"]:  
                # Ensure 'weights' is properly converted
                if "weights" in mcfit:
                    mcfit["weights"] = convert_to_serializable(mcfit["weights"])

    with open(output_file, "wb") as f:
        pickle.dump(convert_to_serializable(results), f)

    print(f"Saved results to {output_file}")
    print(results)