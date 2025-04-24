import os
import pandas as pd
import numpy as np
from amespahdbpythonsuite import observation
from amespahdbpythonsuite.amespahdb import AmesPAHdb
import pickle
import tempfile
import subprocess

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
    neutral_choice = "individualPAHs_C<29"  # Only neutral PAHs
    # sample_sizes = [10,20,50,100,200,500,1000,2000,5000,10000]  # Monte Carlo runs
    # --- PAHdb Loading ---
    base_path = os.path.dirname(os.path.abspath(__file__))
    pahdb_folder = os.path.join(base_path, "PAHdb")
    plot_folder = os.path.join(base_path, "fullish_singlePAH_fitplots_NNLC")
    os.makedirs(plot_folder, exist_ok=True)


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

    search_query1 = "mg=0 fe=0 si=0 o=0 h>0 neutral c<29"  # Only cationic PAHs
    # # Perform the search
    uids1 = pahdb.search(search_query1)
    search_query2 = "mg=0 fe=0 si=0 o=0 h>0 anion c<29"  # Only neutral PAHs
    uids2 = pahdb.search(search_query2)
    # uidsfirst = uids1 + uids2
    uids = uids1 + uids2

    # search_query3 = "mg=0 fe=0 si=0 o=0 h>0 neutral"
    # uids3 = pahdb.search(search_query3)
    # search_qeury4 = "mg=0 fe=0 si=0 o=0 h>0 anion"
    # uids4 = pahdb.search(search_qeury4)
    # uidsecond = uids3 + uids4

    # #subtract all the uid numbers from the first list from the second list
    # uids = list(set(uidsecond) - set(uidsfirst))

    
        # --- Cascade the PAHs with the Solar Spectrum ---
    solar_folder = os.path.join(base_path, "Sun_SORCE")
    csv_path = os.path.join(solar_folder, 'sorce_processed_data.csv')

    irradiance_data = pd.read_csv(csv_path)
    august_data = irradiance_data[irradiance_data['month'] == 'august']
    wavel = np.array(august_data['wavelength'])
    irrad = np.array(august_data['irradiance'])
    
    uv_spectrum = {
        "frequency": 1e7 / np.flip(wavel),
        "intensity": 1e-4 * np.flip(irrad * wavel**2) / (4 * np.pi),
    }

    print("Solar data loaded successfully.")

    indy_pah_results = {}

    for uid in uids:
        current_index = uids.index(uid) + 1
        total_uids = len(uids)
        print(f"Processing PAH: {uid} ({current_index}/{total_uids})")
        transitions = pahdb.gettransitionsbyuid(uid)

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

        print(f"Running NNLC fitting for heights: {heights} km.")

        for height in heights:
            data_file = os.path.join(obs_path, f"titan_spec_{height}_yerr.ipac")

            if not os.path.exists(data_file):
                print(f"Warning: Data file for height {height} km not found: {data_file}")
                continue

            # Load observation data
            obs = observation.Observation(data_file)
            obs.abscissaunitsto("1/cm")

            # Run Monte Carlo fitting
            NNLCfit = spectrum.fit(obs, method="NNLC", normalization="max")

            # NNLCfit.plot(wavelength=True)
            # NNLCfit.plot(wavelength=True, residual=True)

            # Extract results
            fit_results = NNLCfit.get()

            rchi2 = NNLCfit.rchi2 if hasattr(NNLCfit, "rchi2") else None

            if rchi2 is not None:
                print(f"Reduced chi-squared at {height} km: {rchi2:.2f}")

            rchi2_clean = f"{rchi2:.2f}".replace(".", "p")
            plot_filename = os.path.join(plot_folder, f"fit_uid{uid}_h{height}_rchi2_{rchi2_clean}")

            # NNLCfit.plot(
            #     wavelength=True,
            #     residual=True,
            #     save=True,
            #     output=plot_filename,  # e.g., path without extension
            #     ftype="pdf"            # file type to save
            # )

            # Remove unnecessary keys
            for key in ["observation", "distribution", "type"]:
                fit_results.pop(key, None)

            # Store results
            if height not in results:
                results[height] = {}
            
            results[height]["rchi2"] = convert_to_serializable(rchi2)
        indy_pah_results[uid] = results

    print("Finished all NNLC fits.")
    results_folder = os.path.join(base_path, "results")
    os.makedirs(results_folder, exist_ok=True)  # Ensure results folder exists

    output_filename = f"NNLCfit_{version_choice}_{neutral_choice}.pkl"
    output_file = os.path.join(results_folder, output_filename)

    # for height in results:
    #     results[height]["weights"] = convert_to_serializable(results[height]["weights"])
    #     if "gof" in results[height]:
    #         results[height]["gof"] = convert_to_serializable(results[height]["gof"])

    with open(output_file, "wb") as f:
        pickle.dump(convert_to_serializable(indy_pah_results), f)


    print(f"Saved results to {output_file}")
    #delete 'energy' from the results
    # for height in results:
    #     if "model" in results[height]:
    #         del results[height]["model"]
    #     if "version" in results[height]:
    #         del results[height]["version"]
    #     if "grid" in results[height]:
    #         del results[height]["grid"]
    #     if "units" in results[height]:
    #         del results[height]["units"]
    #     if "shift" in results[height]:
    #         del results[height]["shift"]
    #     if "fwhm" in results[height]:
    #         del results[height]["fwhm"]
    #     if "profile" in results[height]:
    #         del results[height]["profile"]

    # print(results[900].keys())
    # Create a temporary file to store the results
    # with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w") as temp_file:
    #     for height, data in results.items():
    #         temp_file.write(f"Height: {height} km\n")
    #         temp_file.write(f"{data}\n\n")
    #     temp_file_path = temp_file.name

    # # Open the temporary file in the default text editor
    # subprocess.run(["open", temp_file_path])  # Use "open" on macOS, "xdg-open" on Linux, or "notepad" on Windows
    df_data = []

    for uid, heights_dict in indy_pah_results.items():
        for height, metrics in heights_dict.items():
            df_data.append({
                "uid": uid,
                "height": height,
                "rchi2": metrics.get("rchi2", np.nan),
            })

    df = pd.DataFrame(df_data)
    df = df.sort_values(by=["height", "rchi2"])
    df_pivot = df.pivot(index="uid", columns="height", values="rchi2")
    print(df_pivot)
