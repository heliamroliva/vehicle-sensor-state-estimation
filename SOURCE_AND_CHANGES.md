# Source inventory and packaging changes

## Original project inspection

- The original top-level `README.md` was empty. Its `requirements.txt` listed NumPy, SciPy, pandas, Matplotlib, pytest, Jupyter, and ipykernel. Only NumPy and Matplotlib are needed for this packaged nominal scenario and portfolio generation.
- `simulations/nominal.py` is the only complete simulation entry point. It imports `src/vehicle_model.py`, `src/sensors.py`, `src/kalman_filter.py`, and `src/rls.py`, then writes `results/nominal_results.npz`.
- `simulations/plot.py` analyzes that NPZ and calculates GPS and filter velocity RMSE at stored GPS measurement indices. It creates interactive plots with `plt.show()`.
- `simulations/gps_fault_test.py`, `imu_bias_test.py`, and `parameter_id_test.py`, and `src/fault_injection.py`, `metrics.py`, and `validation.py` were empty. The original tests contained only `assert True`. The `data/`, `matlab/`, and `notebooks/` directories contained no files.
- The original project already contained `results/nominal_results.npz`. Every array in the newly generated NPZ compared exactly equal to that existing NPZ, including NaN locations. The delivered NPZ is the newly generated file.

## Source preservation

All copied files under `src/` and `simulations/` are unchanged from the originals. No repair was needed to execute the nominal scenario. The class spelling `vechicle_model`, hard-coded parameters, and the original GPS sampling behavior were kept as supplied. `portfolio_analysis.py`, this documentation, the metrics JSON, figures, PDF, and ZIP are **new portfolio packaging work**, not historical project accomplishments.

## Metric and method review

The original plot script computes speed RMSE at `~np.isnan(v_gps)`. The package analysis checks 6,000 time records at 0.01 s intervals and 600 GPS samples, then uses the same mask for GPS, filter, and raw IMU integration. Filter estimates at those indices are after the corresponding GPS update. The raw IMU estimate is cumulative measured acceleration from zero speed with 0.01 s intervals. For comparison, all-step filter RMSE uses all 6,000 samples and is reported separately.

The `np.random.seed(42)` call is in the original simulation. On each loop iteration the source draws a GPS sample, but retains it only at update indices and draws a second GPS sample for the update. The initial GPS update is at 0.01 s, then every 0.1 s. The extra random draw changes the noise sequence but not the 600 stored-update cadence.

RLS estimates vary substantially and finish far from the ground-truth coefficients. The PDF uses a clearly labeled 5–60 s view for parameter trends because the full run has a large early transient (CdA ranges from about -73.8 to 1216.8 m²). The full trajectory is retained in the PNG and NPZ. No previous résumé RMSE or improvement percentage was imported.

## Public-data boundary

The included NPZ is generated entirely by this simulation. No personal, vehicle field, or third-party dataset is included. The package excludes the original virtual environment, caches, Git data, unrelated folders, empty/incomplete scenario modules, and local editor files.
