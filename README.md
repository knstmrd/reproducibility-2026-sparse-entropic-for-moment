# Reproducibility repository for "Sparse entropic quadrature for moment equations"

The `*.jl` files in this directory produce the results from the preprint "Sparse entropic quadrature for moment equations" by G. Oblapenko, M. Torrilhon, M. Herty.

To install the required packages, run TODO

The data is written to subdirectories of `output/` (if `output` does not exist, it will be created).

4 simulation setups are available: 
- [`simulations/sod_dvm.jl`](Sod shock tube simulated using DVM)
- [`simulations/sod_speqck.jl`](Sod shock tube simulated using the sparse entropic quadrature method)
- [`simulations/couette_dvm.jl`](Couette flow simulated using DVM)
- [`simulations/couette_speqck.jl`](Couette flow simulated using the sparse entropic quadrature method)

The moment-method based scripts iterate over the maximum total order of conserved moments (2,4,6), the convection schemes
(upwinding, Lax-Friedrichs, Lax-Wendroff, and sparsity parameter values.

The results can also be downloaded in HDF5 format from [Zenodo](https://doi.org/10.5281/zenodo.22768394).
The scripts list below by default assume that the data is in the `output` directory, and that plots are written to `plots/` (needs to
be created).

## Sod shock tube
The Sod shock tube problem is solved a one-dimensional domain of length 1, with the left state given having number density and temperature `(n_L, T_L)=(1,0,1)` and the right state having number density and temperature `(n_R, T_R)=(1/8, 4/5)`, corresponding to a 10:1 pressure ratio and 8:1 density ratio. Both states have their velocity set to 0.
The velocity grid has extent `[-5,5]` and 21 nodes in each velocity direction.
Two cases are simulated: 1) a case wih `mu_ref = 2e-2`, corresponding to a Knudsen number of the left state equal to approximately `2.5e-2$` and 2) a collisionless case without the BGK term (`BGK_factor=0.0`).
The equations are solved on a 400-cell grid using a timestep of $4 \times 10^{-4}$, corresponding to a CFL number of 0.8 as governed by the largest grid velocity.

## Couette flow
The Couette flow between is modelled in a channel of length 1 between two parallel plates with a wall temperature `T_w = 1` and moving in the `y`-direction with a velocity of `\± 1` (left and right wall, respectively). The reference viscosity is taken as `0.3`, corresponding to a Knudsen number of approximately `0.4`.
We use a velocity grid with extent `[-6,6]` and 16 nodes in each velocity direction.
The flow is simulated on grids with 50 and 100 cells; the DVM solution is also computed on a 400-cell grid to estimate convergence.

## Sparsity analysis script

The `couette_log_tables.py` and `sod_log_tables.py` scripts can be used to generate the sparsity tables for the Couette flow and the Sod shock tube problems by analyzing the percentage of sparsity as written to `*.log` files during the moment-based simulations.
The data is written to `output/couette/couette_table_M<M>.md` and `output/sod/sod_M<M>.md`, where `<M>` is the total order of moments conserved in the simulation.

## Plotting scripts

### Sod shock tube
To plot the Sod results, use the `plot_1D_sod.py` script.

Collisional case, plot comparison of DVM and moment solutions with upwinding and Lax-Wendroff, no sparsity:
```bash
python3 scripts/plot_1D_sod.py --files output/sod/dvm/sod_dvm_0.02_6_400_21_upwind_1.0.h5 output/sod/m2/sod_0.02_2_400_21_0.0_upwind_1.0.h5 output/sod/m2/sod_0.02_2_400_21_0.0_upwind_lw_1.0.h5 output/sod/m4/sod_0.02_4_400_21_0.0_upwind_1.0.h5 output/sod/m4/sod_0.02_4_400_21_0.0_upwind_lw_1.0.h5 output/sod/m6/sod_0.02_6_400_21_0.0_upwind_1.0.h5 output/sod/m6/sod_0.02_6_400_21_0.0_upwind_lw_1.0.h5 --labels 'DVM, upwind' '$M_{\max}=2$, upwind' '$M_{\max}=2$, L-W' '$M_{\max}=4$, upwind' '$M_{\max}=4$, L-W' '$M_{\max}=6$, upwind' '$M_{\max}=6$, L-W' --moment 2,0,0 --timestep -6 --length 1.0 --xmin 0.3 --xmax 0.7  --titletext '$\mu_{ref}=0.02$' --colors 'k' 'tab:red' 'tab:red'  'tab:orange' 'tab:orange' 'tab:blue' 'tab:blue' --linestyles 'solid' 'solid' 'dashed' 'solid' 'dashed' 'solid' 'dashed' --output plots/sod_0.02_upwind_and_lw.pdf
```

Collisionless case, plot comparison of DVM and moment solutions with upwinding and Lax-Wendroff, no sparsity:
```bash
python3 scripts/plot_1D_sod.py --files output/sod/dvm/sod_dvm_0.02_6_400_21_upwind_1.0.h5 output/sod/m2/sod_0.2_2_400_21_0.0_upwind_0.0.h5 output/sod/m2/sod_0.2_2_400_21_0.0_upwind_lw_0.0.h5  output/sod/m4/sod_0.2_4_400_21_0.0_upwind_0.0.h5 output/sod/m4/sod_0.2_4_400_21_0.0_upwind_lw_0.0.h5 output/sod/m6/sod_0.2_6_400_21_0.0_upwind_0.0.h5 output/sod/m6/sod_0.2_6_400_21_0.0_upwind_lw_0.0.h5 --labels 'DVM, upwind' '$M_{\max}=2$, upwind' '$M_{\max}=2$, L-W' '$M_{\max}=4$, upwind' '$M_{\max}=4$, L-W' '$M_{\max}=6$, upwind' '$M_{\max}=6$, L-W' --moment 2,0,0 --timestep -6 --length 1.0 --xmin 0.3 --xmax 0.7  --titletext 'collisionless' --colors 'k' 'tab:red' 'tab:red'  'tab:orange' 'tab:orange' 'tab:blue' 'tab:blue' --linestyles 'solid' 'solid' 'dashed' 'solid' 'dashed' 'solid' 'dashed' --output plots/sod_nocoll_upwind_and_lw.pdf
```

Collisional case, impact of sparsity
```bash
python3 scripts/plot_1D_sod.py --files output/sod/dvm/sod_dvm_0.02_6_400_21_upwind_1.0.h5 output/sod/m4/sod_0.02_4_400_21_0.0_upwind_1.0.h5 output/sod/m4/sod_0.02_4_400_21_1.0e-6_upwind_1.0.h5 output/sod/m4/sod_0.02_4_400_21_0.0001_upwind_1.0.h5 output/sod/m4/sod_0.02_4_400_21_0.01_upwind_1.0.h5 output/sod/m6/sod_0.02_6_400_21_0.0_upwind_1.0.h5 output/sod/m6/sod_0.02_6_400_21_1.0e-6_upwind_1.0.h5 output/sod/m6/sod_0.02_6_400_21_0.0001_upwind_1.0.h5 --labels 'DVM, upwind' '$M_{\max}=4$, $\lambda=0$' '$M_{\max}=4$, $\lambda=10^{-6}$' '$M_{\max}=4$, $\lambda=10^{-4}$' '$M_{\max}=4$, $\lambda=10^{-2}$' '$M_{\max}=6$, $\lambda=0$' '$M_{\max}=6$, $\lambda=10^{-6}$' '$M_{\max}=6$, $\lambda=10^{-4}$' --moment 2,0,0 --timestep -6 --length 1.0 --xmin 0.3 --xmax 0.7  --titletext '$\mu_{ref}=0.02$' --colors 'k' 'tab:orange' 'tab:orange' 'tab:orange' 'tab:orange' 'tab:blue' 'tab:blue' 'tab:blue' --linestyles 'solid' 'solid' 'dashed' 'dashdot' 'dotted' 'solid' 'dashed' 'dashdot' --output plots/sod_0.02_upwind_sparsity.pdf
```

Collisionless case, impact of sparsity
```bash
python3 scripts/plot_1D_sod.py --files output/sod/dvm/sod_dvm_0.2_6_400_21_upwind_0.0.h5 output/sod/m4/sod_0.2_4_400_21_0.0_upwind_0.0.h5 output/sod/m4/sod_0.2_4_400_21_1.0e-6_upwind_0.0.h5 output/sod/m4/sod_0.2_4_400_21_0.0001_upwind_0.0.h5  output/sod/m6/sod_0.2_6_400_21_0.0_upwind_0.0.h5 output/sod/m6/sod_0.2_6_400_21_1.0e-6_upwind_0.0.h5 output/sod/m6/sod_0.2_6_400_21_0.0001_upwind_0.0.h5 --labels 'DVM, upwind' '$M_{\max}=4$, $\lambda=0$' '$M_{\max}=4$, $\lambda=10^{-6}$' '$M_{\max}=4$, $\lambda=10^{-4}$' '$M_{\max}=6$, $\lambda=0$' '$M_{\max}=6$, $\lambda=10^{-6}$' '$M_{\max}=6$, $\lambda=10^{-4}$' --moment 2,0,0 --timestep -6 --length 1.0 --xmin 0.3 --xmax 0.7  --titletext 'collisionless' --colors 'k' 'tab:orange' 'tab:orange' 'tab:orange' 'tab:blue' 'tab:blue' 'tab:blue' --linestyles 'solid' 'solid' 'dashed' 'dashdot' 'solid' 'dashed' 'dashdot' --output plots/sod_nocoll_upwind_sparsity.pdf
```

### Couette flow
Comparison of DVM solutions.
```bash
python3 scripts/plot_1D_couette.py --files output/couette/dvm/couette_dvm_0.3_6_50_16_upwind.h5 output/couette/dvm/couette_dvm_0.3_6_50_16_global.h5 output/couette/dvm/couette_dvm_0.3_6_100_16_upwind.h5 output/couette/dvm/couette_dvm_0.3_6_100_16_global.h5 output/couette/dvm/couette_dvm_0.3_6_500_16_upwind.h5 --labels 'DVM, 50 cells, upwind' 'DVM, 50 cells, L-F' 'DVM, 100 cells, upwind' 'DVM, 100 cells, L-F' 'DVM, 500 cells, upwind' --moment 1,1,0 --timestep -1 --length 1.0 --xmin 0.0 --xmax 1.0 --colors 'tab:orange' 'tab:orange' 'tab:blue' 'tab:blue' 'k' --linestyles 'solid' 'dashed' 'solid' 'dashed' 'solid'  --output plots/couette_dvm.pdf
```

DVM solutions and M=2 case:
```bash
python3 scripts/plot_1D_couette.py --files output/couette/dvm/couette_dvm_0.3_6_100_16_upwind.h5 output/couette/m2/couette_0.3_2_100_16_0.0_upwind.h5  --labels 'DVM, upwind' '$M_{\max}=2$, upwind' --moment 1,1,0 --timestep -1 --length 1.0 --xmin 0.0 --xmax 1.0 --colors 'k' 'tab:red' --linestyles 'solid' 'solid'  --output plots/couette_upwind_m2.pdf
```

DVM solutions and M=4, M=6, no sparsity:
```bash
python3 scripts/plot_1D_couette.py --files output/couette/dvm/couette_dvm_0.3_6_100_16_upwind.h5 output/couette/dvm/couette_dvm_0.3_6_100_16_global.h5 output/couette/m4/couette_0.3_4_100_16_0.0_upwind.h5 output/couette/m4/couette_0.3_4_100_16_0.0_lf.h5 output/couette/m4/couette_0.3_4_100_16_0.0_upwind_lw.h5 output/couette/m6/couette_0.3_6_100_16_0.0_upwind.h5 output/couette/m6/couette_0.3_6_100_16_0.0_lf.h5 output/couette/m6/couette_0.3_6_100_16_0.0_upwind_lw.h5  --labels 'DVM, upwind' 'DVM, L-F' '$M_{\max}=4$, upwind' '$M_{\max}=4$, L-F' '$M_{\max}=4$, L-W'  '$M_{\max}=6$, upwind' '$M_{\max}=6$, L-F' '$M_{\max}=6$, L-W' --moment 1,1,0 --timestep -1 --length 1.0 --xmin 0.0 --xmax 1.0 --colors 'k' 'k' 'tab:orange' 'tab:orange' 'tab:orange' 'tab:blue' 'tab:blue' 'tab:blue' --linestyles 'solid' 'dashed' 'solid' 'dashed' 'dashdot' 'solid' 'dashed' 'dashdot' --output plots/couette_upwind_and_lf.pdf
```

Impact of sparsity:
```bash
python3 scripts/plot_1D_couette.py --files output/couette/dvm/couette_dvm_0.3_6_100_16_upwind.h5 output/couette/m4/couette_0.3_4_100_16_0.0_upwind.h5 output/couette/m4/couette_0.3_4_100_16_1.0e-6_upwind.h5 output/couette/m4/couette_0.3_4_100_16_0.0001_upwind.h5 output/couette/m4/couette_0.3_4_100_16_0.01_upwind.h5 output/couette/m6/couette_0.3_6_100_16_0.0_upwind.h5 output/couette/m6/couette_0.3_6_100_16_1.0e-6_upwind.h5 output/couette/m6/couette_0.3_6_100_16_0.0001_upwind.h5   --labels 'DVM' '$M_{\max}=4$, $\lambda=0$' '$M_{\max}=4$, $\lambda=10^{-6}$' '$M_{\max}=4$, $\lambda=10^{-4}$' '$M_{\max}=4$, $\lambda=10^{-2}$' '$M_{\max}=6$, $\lambda=0$' '$M_{\max}=6$, $\lambda=10^{-6}$' '$M_{\max}=6$, $\lambda=10^{-4}$'  --moment 1,1,0 --timestep -1 --length 1.0 --xmin 0.0 --xmax 1.0 --colors 'k' 'tab:orange' 'tab:orange' 'tab:orange' 'tab:orange' 'tab:blue' 'tab:blue' 'tab:blue' --linestyles 'solid' 'solid' 'dashed' 'dashdot' 'dotted' 'solid' 'dashed' 'dashdot'  --output plots/couette_sparsity.pdf
```
