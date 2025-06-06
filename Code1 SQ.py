# Import required scientific computing packages  
# A units-and-constants package is needed: http://pypi.python.org/pypi/numericalunits  
import numpy as np  
import scipy.interpolate, scipy.integrate, pandas, sys  
assert sys.version_info >= (3,6), 'Requires Python 3.6+'  
  
# Import physical constants and units from custom package  
from numericalunits import W, K, nm, m, cm, s, eV, meV, V, mA, c0, hPlanck, kB, e  
Tcell = 300 * K  # Standard operating temperature for solar cells (300K)  
  
# Load AM1.5G solar spectrum data from Excel file  
worksheet = pandas.read_excel('AM 1.5G.xls')  
downloaded_array = np.array(worksheet)  
  
# Extract wavelength (column 0) and spectral irradiance (column 2)  
AM15 = downloaded_array[1:, [0,2]]  
  
# Convert units: wavelength to nm, irradiance to W/m²/nm  
AM15[:,0] *= nm  
AM15[:,1] *= W / m**2 / nm  
  
# Define wavelength range for analysis (280-4000nm)  
λ_min = 280 * nm  # Minimum wavelength (UV cutoff)  
λ_max = 4000 * nm  # Maximum wavelength (IR cutoff)  
E_min = hPlanck * c0 / λ_max  # Convert to minimum photon energy  
E_max = hPlanck * c0 / λ_min  # Convert to maximum photon energy  
  
# Create interpolation function for solar spectrum  
AM15interp = scipy.interpolate.interp1d(AM15[:,0], AM15[:,1])  
  
# Function to calculate photon flux per unit energy interval  
def SPhotonsPerTEA(Ephoton):  
    """Calculate photon flux density per unit energy interval at given photon energy. 
    Args: 
        Ephoton: Photon energy in eV 
    Returns: 
        Photon flux density in m⁻²·s⁻¹·eV⁻¹ 
    """  
    λ = hPlanck * c0 / Ephoton  # Convert energy to wavelength  
    return AM15interp(λ) * (1 / Ephoton) * (hPlanck * c0 / Ephoton**2)  
  
# Function to calculate power per unit energy interval  
PowerPerTEA = lambda E : E * SPhotonsPerTEA(E)  # Power density in W/m²/eV  
  
# Calculate total solar constant (integrated power density)  
solar_constant = scipy.integrate.quad(PowerPerTEA,E_min,E_max, full_output=1)[0]  
  
# Function to calculate integrated photon flux above bandgap  
def solar_photons_above_gap(Egap):  
    """Calculate total photon flux with energy above bandgap. 
    Args: 
        Egap: Bandgap energy in eV 
    Returns: 
        Integrated photon flux in m⁻²·s⁻¹ 
    """  
    return scipy.integrate.quad(SPhotonsPerTEA, Egap, E_max, full_output=1)[0]  
  
# Function to calculate radiative recombination rate  
def RR0(Egap):  
    """Calculate radiative recombination rate in dark equilibrium. 
    Args: 
        Egap: Bandgap energy in eV 
    Returns: 
        Recombination rate in m⁻²·s⁻¹ 
    """  
    integrand = lambda E : E**2 / (np.exp(E / (kB * Tcell)) - 1)  # Planck's law  
    integral = scipy.integrate.quad(integrand, Egap, E_max, full_output=1)[0]  # Integrate  
    return ((2 * np.pi) / (c0**2 * hPlanck**3)) * integral  # Prefactor from detailed balance  
  
# Function to calculate current density  
def current_density(voltage, Egap):  
    """Calculate current density at given voltage and bandgap. 
    Args: 
        voltage: Applied voltage in V 
        Egap: Bandgap energy in eV 
    Returns: 
        Current density in A/m² 
    """  
    return e * (solar_photons_above_gap(Egap) - RR0(Egap) * np.exp(e * voltage / (kB * Tcell)))  
  
# Short-circuit current (JSC at V=0)  
def JSC(Egap):  
    return current_density(0, Egap)  
  
# Open-circuit voltage (voltage when J=0)  
def VOC(Egap):  
    return (kB * Tcell / e) * np.log(solar_photons_above_gap(Egap) / RR0(Egap))  
  
# Optimization function to find maximum power point  
from scipy.optimize import fmin  
  
def fmax(func_to_maximize, initial_guess=0):  
    """Find the argument that maximizes a function. 
    Args: 
        func_to_maximize: Function to maximize 
        initial_guess: Starting point for optimization 
    Returns: 
        x value that maximizes the function 
    """  
    func_to_minimize = lambda x : -func_to_maximize(x)  # Convert to minimization  
    return fmin(func_to_minimize, initial_guess, disp=False)[0]  # Find minimum  
  
# Functions for maximum power point analysis  
def V_mpp(Egap):  
    """Calculate voltage at maximum power point. 
    Args: 
        Egap: Bandgap energy in eV 
    Returns: 
        Voltage in V 
    """  
    return fmax(lambda voltage : voltage * current_density(voltage, Egap))  
  
def J_mpp(Egap):  
    """Calculate current density at maximum power point. 
    Args: 
        Egap: Bandgap energy in eV 
    Returns: 
        Current density in A/m² 
    """  
    return current_density(V_mpp(Egap), Egap)  
  
def max_power(Egap):  
    """Calculate maximum power density. 
    Args: 
        Egap: Bandgap energy in eV 
    Returns: 
        Power density in W/m² 
    """  
    voltage = V_mpp(Egap)  
    return voltage * current_density(voltage, Egap)  
  
def max_efficiency(Egap):  
    """Calculate maximum conversion efficiency. 
    Args: 
        Egap: Bandgap energy in eV 
    Returns: 
        Efficiency as fraction (0-1) 
    """  
    return max_power(Egap) / solar_constant  
  
# Function to calculate fill factor  
def fill_factor(Egap):  
    """Calculate fill factor. 
    Args: 
        Egap: Bandgap energy in eV 
    Returns: 
        Fill factor (0-1) 
    """  
    return max_power(Egap) / (JSC(Egap) * VOC(Egap))  
  
# Calculate all photovoltaic parameters across bandgap range  
Egap_list = np.linspace(0.4 * eV, 3 * eV, num=100)  
JSC_list = np.array([JSC(E) for E in Egap_list])  
VOC_list = np.array([VOC(E) for E in Egap_list])  
eff_list = np.array([max_efficiency(E) for E in Egap_list])  
FF_list = np.array([fill_factor(E) for E in Egap_list])  
  
# Save calculated data to text files  
np.savetxt("eff_list1.txt", eff_list, fmt='%f', delimiter=',')  # Efficiency  
np.savetxt("VOC_list1.txt", VOC_list / V, fmt='%f', delimiter=',')  # VOC in volts  
np.savetxt("JSC_list1.txt", JSC_list / (mA / cm**2), fmt='%f', delimiter=',')  # JSC in mA/cm²  
np.savetxt("FF.txt", FF_list, fmt='%f', delimiter=',')  # Fill factor  