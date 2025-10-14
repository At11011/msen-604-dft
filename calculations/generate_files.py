#!/usr/bin/env python3
import numpy as np
import subprocess
import os

# Conversion factor: Angstrom to Bohr
ANG_TO_BOHR = 1.88972687777

# Lattice parameters in Angstrom
lattice_params_ang = np.linspace(2.2, 2.9, 12)

# Create directory for calculations
os.makedirs('calculations', exist_ok=True)

# Template for input file
input_template = """&CONTROL
  calculation = 'scf'
  prefix = 'cu_sc_a{a_ang:.3f}'
  outdir = './tmp'
  pseudo_dir = './pseudo'
  verbosity = 'high'
/

&SYSTEM
  ibrav = 1
  celldm(1) = {a_bohr:.8f}
  nat = 1
  ntyp = 1
  ecutwfc = 21.46
  occupations = 'smearing'
  smearing = 'mv'
  degauss = 0.02
  input_dft = 'PW91'
/

&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7
/

ATOMIC_SPECIES
  Cu  63.546  Cu.pw91-n-van_ak.UPF

ATOMIC_POSITIONS crystal
  Cu  0.0  0.0  0.0

K_POINTS automatic
  12 12 12  0 0 0
"""

# Generate input files and run calculations
results = []

for i, a_ang in enumerate(lattice_params_ang):
    a_bohr = a_ang * ANG_TO_BOHR
    
    # Create input file
    input_text = input_template.format(a_ang=a_ang, a_bohr=a_bohr)
    input_filename = f'calculations/cu_a{a_ang:.3f}.in'
    output_filename = f'calculations/cu_a{a_ang:.3f}.out'
    
    with open(input_filename, 'w') as f:
        f.write(input_text)
    
    print(f"Created input file: {input_filename}")
    print(f"  Lattice parameter: {a_ang:.3f} Å ({a_bohr:.6f} Bohr)")
    
    # Run calculation (uncomment when ready to run)
    # subprocess.run(['pw.x', '<', input_filename, '>', output_filename], shell=True)

print(f"\nGenerated {len(lattice_params_ang)} input files in 'calculations/' directory")
print("\nTo run calculations, use:")
print("  pw.x < calculations/cu_aX.XXX.in > calculations/cu_aX.XXX.out")
print("\nOr uncomment the subprocess.run line in the script")
