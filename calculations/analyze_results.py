#!/usr/bin/env python3
import numpy as np
from scipy.optimize import curve_fit
import re
import glob


def extract_energy(filename):
    """Extract total energy from QE output file"""
    with open(filename, 'r') as f:
        content = f.read()
        # Look for final energy
        match = re.search(r'!\s+total energy\s+=\s+([-\d.]+)\s+Ry', content)
        if match:
            return float(match.group(1))
    return None


def birch_murnaghan(V, E0, V0, B0, B0_prime):
    """Birch-Murnaghan equation of state"""
    eta = (V0/V)**(2/3)
    E = E0 + (9*V0*B0/16) * ((eta - 1)**2 *
                             (6 - 4*eta + B0_prime*(eta - 1)))
    return E


# Conversion factor: 1 Ry = 13.605693122994 eV
RY_TO_EV = 13.605693122994

# Collect results
lattice_params = []
energies = []

output_files = sorted(glob.glob('calculations/cu_a*.out'))

for filename in output_files:
    # Extract lattice parameter from filename
    match = re.search(r'cu_a([\d.]+)\.out', filename)
    if match:
        a_ang = float(match.group(1))
        energy = extract_energy(filename)

        if energy is not None:
            lattice_params.append(a_ang)
            energies.append(energy * RY_TO_EV)  # Convert to eV
            print(f"a = {a_ang:.3f} Å: E = {energy * RY_TO_EV:.6f} eV")

if len(energies) == 0:
    print("No energies extracted. Check that calculations have completed.")
    exit(1)

# Convert to numpy arrays
lattice_params = np.array(lattice_params)
energies = np.array(energies)

# Sort by lattice parameter
sort_idx = np.argsort(lattice_params)
lattice_params = lattice_params[sort_idx]
energies = energies[sort_idx]

# Fit polynomial to find minimum
coeffs = np.polyfit(lattice_params, energies, 4)
poly = np.poly1d(coeffs)

# Find minimum
a_fine = np.linspace(lattice_params.min(), lattice_params.max(), 1000)
e_fine = poly(a_fine)
min_idx = np.argmin(e_fine)
a_eq = a_fine[min_idx]
e_min = e_fine[min_idx]

print(f"\n{'='*50}")
print(f"Equilibrium lattice parameter: {a_eq:.4f} Å")
print(f"Minimum energy: {e_min:.6f} eV/atom")
print(f"{'='*50}")

# Generate TikZ/pgfplots code
tikz_code = r"""\begin{tikzpicture}
\begin{axis}[
    width=12cm,
    height=8cm,
    xlabel={Lattice Parameter (\AA)},
    ylabel={Total Energy (eV/atom)},
    title={Energy vs Lattice Parameter for Simple Cubic Cu},
    grid=major,
    grid style={dashed, gray!30},
    legend pos=north east,
    legend style={font=\small},
    tick label style={font=\small},
    label style={font=\footnotesize},
    title style={font=\bfseries}
]

% Calculated points
\addplot[
    only marks,
    mark=*,
    mark size=2.5pt,
    color=blue,
] coordinates {
"""

# Add calculated points
for a, e in zip(lattice_params, energies):
    tikz_code += f"    ({a:.6f}, {e:.6f})\n"

tikz_code += r"""};
\addlegendentry{Calculated points}

% Polynomial fit
\addplot[
    color=red,
    line width=1.2pt,
    smooth,
] coordinates {
"""

# Add fitted curve points (subsample for smaller file size)
subsample = 100
indices = np.linspace(0, len(a_fine)-1, subsample, dtype=int)
for idx in indices:
    tikz_code += f"    ({a_fine[idx]:.6f}, {e_fine[idx]:.6f})\n"

tikz_code += r"""};
\addlegendentry{4th order polynomial fit}

% Vertical line at minimum
\addplot[
    color=green!70!black,
    dashed,
    line width=1pt,
] coordinates {
"""

# Add vertical line at equilibrium
y_min = energies.min()
y_max = energies.max()
y_range = y_max - y_min
y_bottom = y_min - 0.1 * y_range
y_top = y_max + 0.1 * y_range

tikz_code += f"    ({a_eq:.6f}, {y_bottom:.6f})\n"
tikz_code += f"    ({a_eq:.6f}, {y_top:.6f})\n"

tikz_code += r"""};
\addlegendentry{Minimum at $a=""" + f"{a_eq:.4f}" + r"""$ \AA}

\end{axis}
\end{tikzpicture}"""

# Save TikZ code to file
with open('../assets/lattice_optimization.tex', 'w') as f:
    f.write(tikz_code)

print("\nTikZ plot saved as 'lattice_optimization.tex'")
print("\nTo use this in LaTeX, include the following in your preamble:")
print("  \\usepackage{pgfplots}")
print("  \\pgfplotsset{compat=1.18}")
print("\nThen include the file with: \\input{lattice_optimization.tex}")
