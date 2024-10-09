import re
import matplotlib.pyplot as plt

# Path to the file
# file_path = 'sorce_sim_L3_c24h_0240nm_2413nm_20030414_20200225.txt'
# file_path = 'sorce_tsi_L3_c24h_m29_v19_20030225_20200225.txt'
file_path = '/Users/floorstikkelbroeck/Documents/Titan/SORCE/sorce_L3_combined_c24h_20030225_20200225.txt' #SORCE SSI, XPS, SOLSTICE and SIM data  

# Initialize lists for each day
wavelengths_july = []
irradiances_july = []
errors_july = []
wavelengths_august = []
irradiances_august = []
errors_august = []

# Regular expression pattern to extract relevant data, including date and errors
pattern = re.compile(r'(\d{8}\.\d)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+\d+\s+\d+\s+(\d\.\d+e[+-]\d+)\s+(\d\.\d+e[+-]\d+)')

# Read the file and extract data for July 19th and August 31st
with open(file_path, 'r') as file:
    for line in file:
        match = pattern.search(line)
        if match:
            date = match.group(1)  # Date in format YYYYMMDD
            wavelength_min = float(match.group(3))  # Min wavelength in nm
            irradiance = float(match.group(5))      # Irradiance in W/m^2/nm
            irradiance_error = float(match.group(6))  # Irradiance uncertainty

            # Filter data for July 19th and August 31st
            if wavelength_min >= 115:
                if date.startswith('20070719'):
                    wavelengths_july.append(wavelength_min)
                    irradiances_july.append(irradiance)
                    errors_july.append(irradiance_error)
                elif date.startswith('20070831'):
                    wavelengths_august.append(wavelength_min)
                    irradiances_august.append(irradiance)
                    errors_august.append(irradiance_error)

#30 - 31 bin has high peak, why?
#skip the 30th entry of each list, midpoints, irradiances_july, irradiances_august
# Constants
# Constants
AU_EARTH = 1.0  # Astronomical Unit for Earth in AU
AU_TITAN = 9.58  # Titan's average distance from the Sun in AU

# Calculate solar flux at Titan using the inverse-square law for July
solar_flux_titan_july = [irradiance * (AU_EARTH / AU_TITAN) ** 2 for irradiance in irradiances_july]

# Calculate solar flux at Titan using the inverse-square law for August
solar_flux_titan_august = [irradiance * (AU_EARTH / AU_TITAN) ** 2 for irradiance in irradiances_august]

print(solar_flux_titan_july[:5])  # Print first 5 values for verification
print(solar_flux_titan_august[:5])  # Print first 5 values for verification

#calulate the corresponding errors to the new values
solar_flux_titan_july_error = [error * (AU_EARTH / AU_TITAN) ** 2 for error in errors_july]
solar_flux_titan_august_error = [error * (AU_EARTH / AU_TITAN) ** 2 for error in errors_august]

# Define a function to collect the data
def collect_irradiance_data():
    data = {
        'july': {
            'wavelengths': wavelengths_july,
            'irradiances': irradiances_july,
            'errors': errors_july
        },
        'august': {
            'wavelengths': wavelengths_august,
            'irradiances': irradiances_august,
            'errors': errors_august
        }
    }
    return data

# Collect the data
irradiance_data = collect_irradiance_data()

# Example usage: print the first 5 wavelengths for July
print(len(irradiance_data['july']['irradiances']))