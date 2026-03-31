import numpy as np
import pandas as pd
from scipy.io import wavfile
from scipy.signal import chirp

def generate_bsil_session(csv_path=None):
    # 1. CONSTANTS & PARAMETERS
    fs = 44100            # Sample Rate (CD Quality)
    active_duration = 900  # 15 Minutes of active frequency
    silent_duration = 600  # 10 Minutes of Zero-Point Integration
    phi = (1 + 5**0.5) / 2 # The Golden Ratio (1.618)
    
    t_active = np.linspace(0, active_duration, fs * active_duration)
    t_silent = np.zeros(fs * silent_duration)

    # 2. BIO-WELL DATA INGESTION (Logic for Personalization)
    # Default values if no CSV is provided
    energy_mod = 1.0 
    entropy_mod = 1.0

    if csv_path:
        try:
            df = pd.read_csv(csv_path)
            # Example: Averaging 'Energy' column to set global amplitude
            avg_energy = df['Energy'].mean()
            # If energy is low (<4.0J), we boost the signal strength
            energy_mod = 1.2 if avg_energy < 4.0 else 1.0
            print(f"Bio-Well Data Loaded. Energy Multiplier: {energy_mod}")
        except Exception as e:
            print(f"Note: Using default calibration. (Error: {e})")

    # 3. CHANNEL 1: THE BED (The 'Soil' - 528Hz Base)
    # A linear sweep through the Solfeggio scale for cellular opening
    bed_signal = chirp(t_active, f0=174, f1=963, t1=active_duration, method='linear')
    bed_signal *= 0.5 * energy_mod # Normalize volume

    # 4. CHANNEL 2: THE COIL (The 'Seed' - Phi Harmonic)
    # The Coil tracks the Bed but is offset by the Golden Ratio
    coil_base = chirp(t_active, f0=174*phi, f1=963*phi, t1=active_duration, method='linear')
    
    # Apply Vortex Math Pulse (3Hz heartbeat) to prevent habituation
    pulse = 0.5 * (1 + np.sin(2 * np.pi * 3 * t_active))
    coil_signal = coil_base * pulse * 0.5

    # 5. CONCATENATE INTEGRATION SILENCE (The Zero Point)
    bed_full = np.concatenate((bed_signal, t_silent))
    coil_full = np.concatenate((coil_signal, t_silent))

    # 6. STEREO MIXING & EXPORT
    # Left = Suddath Bed | Right = Qi Coil
    stereo_output = np.vstack((bed_full, coil_full)).T
    
    # Convert to 16-bit PCM for WAV compatibility
    output_data = (stereo_output * 32767).astype(np.int16)
    
    filename = "Bio-Scalar_Feedback_Session.wav"
    wavfile.write(filename, fs, output_data)
    
    print(f"Success! '{filename}' generated.")
    print("Session Length: 25 Minutes (15m Active / 10m Silent Integration)")

if __name__ == "__main__":
    # To run with your mom's Bio-Well data:
    # generate_bsil_session('path_to_your_biowell_data.csv')
    generate_bsil_session()
