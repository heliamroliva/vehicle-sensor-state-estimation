# Reproduction and verification record

**Execution date:** 2026-10-20 (Asia/Shanghai)  
**Platform:** Windows 11 (`Windows-11-10.0.26200-SP0`)  
**Interpreter:** Python 3.13.15, from the original project's existing `.venv`  
**Packages:** NumPy 2.5.3, Matplotlib 3.11.2  
**Working directory:** `linkedin_portfolio/`  
**Random seed:** 42, set by the unmodified simulation source  
**External input data:** none

Commands executed successfully (exit code 0):

```powershell
..\.venv\Scripts\python.exe -m simulations.nominal
..\.venv\Scripts\python.exe portfolio_analysis.py
```

The first command wrote `results/nominal_results.npz` and printed final true velocity `72.64206675984856` m/s and estimated velocity `72.52613541570916` m/s. The second wrote `results/metrics.json`, two evidence plots, a two-page PDF, and PNG previews of both PDF pages. Its cadence checks passed: 6,000 samples, 600 GPS updates. The generated NPZ arrays were checked against the source project's pre-existing NPZ and matched exactly for every key and value, including NaNs.

The run succeeded without changes to copied source. The pinned dependency installation command in the README was **not** separately exercised in a new virtual environment; the installed versions in the existing environment were used. See `results/metrics.json` for exact unrounded values and method definitions.

The two page previews were visually inspected at 180 dpi for readable text, visible axes, and no clipping or overlap. The PDF is generated from the same page figures. This is a layout inspection, not a separate PDF-renderer test.
