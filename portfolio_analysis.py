"""Recompute metrics and create figures/PDF from a nominal simulation run.

This is portfolio packaging code added in October 2026. The simulation and
estimator implementations in src/ and simulations/ are unmodified copies.
"""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.22,
    "savefig.dpi": 180,
})
NAVY = "#17324f"
BLUE = "#1767a3"
ORANGE = "#dc7c27"
GREEN = "#138064"
GRAY = "#5a6470"


def rmse(error: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(error))))


def label(fig, x, y, value, *, size=9, color=NAVY, weight="normal", va="top"):
    fig.text(x, y, value, ha="left", va=va, fontsize=size, color=color,
             fontweight=weight)


def page_base(number, title, subtitle):
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    label(fig, .07, .965, title, size=19, weight="bold")
    label(fig, .07, .925, subtitle, size=9, color=GRAY)
    fig.add_artist(plt.Line2D([.07, .93], [.90, .90], transform=fig.transFigure,
                              color=BLUE, linewidth=1.5))
    label(fig, .07, .055, "SIMULATION ONLY  |  Seed 42  |  Nominal scenario",
          size=7.5, color=GRAY)
    fig.text(.93, .055, f"{number} / 2", ha="right", va="top", fontsize=7.5,
             color=GRAY)
    return fig


def main():
    with np.load(RESULTS / "nominal_results.npz") as d:
        data = {key: d[key].copy() for key in d.files}
    t = data["time"]
    v_true = data["v_true"]
    v_gps = data["v_gps"]
    v_hat = data["v_hat"]
    bias_hat = data["bias_hat"]
    cda = data["CdA_hat"]
    crr = data["Crr_hat"]
    p = data["P"]
    if len(t) != 6000 or not np.allclose(np.diff(t), .01):
        raise ValueError("Unexpected time base; review metric definitions.")
    gps = np.isfinite(v_gps)
    if int(gps.sum()) != 600:
        raise ValueError("Unexpected GPS sample count; review comparison.")
    v_imu = np.cumsum(data["a_m"]) * .01
    errors = np.column_stack((v_true - v_hat, .1 - bias_hat))
    nees = np.einsum("ni,nij,nj->n", errors, np.linalg.inv(p), errors)
    metrics = {
        "scenario": "nominal simulated longitudinal vehicle",
        "random_seed": 42,
        "duration_s": float(t[-1]),
        "imu_and_filter_rate_hz": 100,
        "gps_update_count": int(gps.sum()),
        "gps_first_update_s": float(t[gps][0]),
        "gps_last_update_s": float(t[gps][-1]),
        "comparison": "RMSE against simulated true velocity at GPS update indices; KF state after GPS update",
        "gps_velocity_rmse_m_per_s": rmse(v_gps[gps] - v_true[gps]),
        "kf_velocity_rmse_at_gps_times_m_per_s": rmse(v_hat[gps] - v_true[gps]),
        "kf_velocity_rmse_all_steps_m_per_s": rmse(v_hat - v_true),
        "raw_imu_integration_rmse_at_gps_times_m_per_s": rmse(v_imu[gps] - v_true[gps]),
        "true_imu_bias_m_per_s2": .1,
        "final_estimated_imu_bias_m_per_s2": float(bias_hat[-1]),
        "true_CdA_m2": .65,
        "final_estimated_CdA_m2": float(cda[-1]),
        "final_CdA_absolute_relative_error_percent": float(abs(cda[-1] - .65) / .65 * 100),
        "true_Crr": .015,
        "final_estimated_Crr": float(crr[-1]),
        "final_Crr_absolute_relative_error_percent": float(abs(crr[-1] - .015) / .015 * 100),
        "single_run_mean_NEES_2_states": float(np.mean(nees)),
        "final_true_velocity_m_per_s": float(v_true[-1]),
        "final_estimated_velocity_m_per_s": float(v_hat[-1]),
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
            "platform": platform.platform(),
        },
    }
    (RESULTS / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    # Standalone evidence figures, generated directly from this run's NPZ.
    velocity = plt.figure(figsize=(10, 5.8))
    ax1 = velocity.add_subplot(211)
    ax2 = velocity.add_subplot(212, sharex=ax1)
    ax1.plot(t, v_true, color=NAVY, label="Simulated truth", linewidth=1.4)
    ax1.scatter(t[gps], v_gps[gps], s=3, alpha=.35, color=ORANGE, label="GPS samples")
    ax1.plot(t, v_hat, color=BLUE, label="KF estimate", linewidth=1)
    ax1.set_ylabel("Velocity [m/s]")
    ax1.legend(loc="upper left", ncol=3, fontsize=8)
    ax2.plot(t, v_hat - v_true, color=BLUE, label="KF error", linewidth=.9)
    ax2.scatter(t[gps], v_gps[gps] - v_true[gps], s=3, alpha=.35,
                color=ORANGE, label="GPS error")
    ax2.axhline(0, color=GRAY, linewidth=.7)
    ax2.set(xlabel="Time [s]", ylabel="Velocity error [m/s]")
    ax2.legend(loc="lower left", ncol=2, fontsize=8)
    velocity.tight_layout()
    velocity.savefig(FIGURES / "velocity_estimation.png")
    plt.close(velocity)

    parameters = plt.figure(figsize=(10, 5.8))
    p1 = parameters.add_subplot(211)
    p2 = parameters.add_subplot(212, sharex=p1)
    p1.plot(t, cda, color=BLUE, label="RLS estimate")
    p1.axhline(.65, color=ORANGE, linestyle="--", label="Simulated truth")
    p1.set_ylabel("CdA [m²]")
    p1.legend(fontsize=8)
    p2.plot(t, crr, color=BLUE, label="RLS estimate")
    p2.axhline(.015, color=ORANGE, linestyle="--", label="Simulated truth")
    p2.set(xlabel="Time [s]", ylabel="Crr [-]")
    parameters.tight_layout()
    parameters.savefig(FIGURES / "parameter_estimation.png")
    plt.close(parameters)

    with PdfPages(ROOT / "Project_Overview.pdf", metadata={
        "Title": "Vehicle and Sensor Estimation | Project Overview",
        "Subject": "Reproducible nominal simulation; no physical vehicle validation",
    }) as pdf:
        page = page_base(1, "Vehicle & Sensor Estimation",
                         "Graduate Systems Engineering  /  Integration  /  Verification & Validation")
        label(page, .07, .865, "PURPOSE", size=10, weight="bold")
        label(page, .07, .842,
              "Estimate longitudinal speed and IMU bias from simulated acceleration and GPS speed.\n"
              "Use the same run to explore recursive identification of road load parameters.",
              size=9, color=GRAY)
        label(page, .07, .778, "MY PROJECT WORK (AS REPRESENTED IN SOURCE)", size=10,
              weight="bold")
        label(page, .07, .752,
              "• Force-balance vehicle model with aerodynamic drag and rolling resistance\n"
              "• Noisy 100 Hz IMU and 10 Hz GPS simulation; two-state Kalman filter\n"
              "• Recursive least squares (RLS) for CdA and rolling resistance coefficient",
              size=8.8, color=GRAY)
        label(page, .07, .648, "SYSTEM FLOW", size=10, weight="bold")
        label(page, .07, .619,
              "Drive force → vehicle model → simulated truth → IMU / GPS → Kalman filter\n"
              "                                                         ↓\n"
              "                                            bias-corrected acceleration + speed → RLS",
              size=8.3, color=GRAY)
        label(page, .07, .523, "NOMINAL-RUN EVIDENCE", size=10, weight="bold")
        ax = page.add_axes([.12, .31, .79, .185])
        ax.plot(t, v_true, color=NAVY, label="Simulated truth", linewidth=1.3)
        ax.scatter(t[gps], v_gps[gps], s=3, color=ORANGE, alpha=.35, label="GPS")
        ax.plot(t, v_hat, color=BLUE, label="KF", linewidth=.9)
        ax.set(xlabel="Time [s]", ylabel="Velocity [m/s]")
        ax.legend(ncol=3, loc="upper left", fontsize=7.5)
        ax2 = page.add_axes([.12, .125, .79, .145], sharex=ax)
        ax2.plot(t, v_hat - v_true, color=BLUE, linewidth=.8, label="KF error")
        ax2.scatter(t[gps], v_gps[gps] - v_true[gps], s=3, alpha=.35,
                    color=ORANGE, label="GPS error")
        ax2.axhline(0, color=GRAY, linewidth=.7)
        ax2.set(xlabel="Time [s]", ylabel="Error [m/s]")
        ax2.legend(ncol=2, loc="lower left", fontsize=7.5)
        pdf.savefig(page)
        page.savefig(FIGURES / "overview_page_1.png", dpi=180)
        plt.close(page)

        page = page_base(2, "Verification Snapshot",
                         "Recomputed from results/nominal_results.npz generated with the supplied model")
        label(page, .07, .862, "MEASUREMENT-CADENCE MATCHED RESULTS", size=10,
              weight="bold")
        label(page, .07, .832,
              "Velocity RMSE vs simulated truth at 600 GPS updates (0.01–59.91 s):",
              size=8.8, color=GRAY)
        label(page, .09, .795, "GPS", size=9, color=GRAY, weight="bold")
        label(page, .09, .775,
              f"{metrics['gps_velocity_rmse_m_per_s']:.3f} m/s", size=15,
              color=ORANGE, weight="bold")
        label(page, .55, .795, "KALMAN FILTER", size=9, color=GRAY, weight="bold")
        label(page, .55, .775,
              f"{metrics['kf_velocity_rmse_at_gps_times_m_per_s']:.3f} m/s",
              size=15, color=BLUE, weight="bold")
        label(page, .07, .729,
              "The KF value uses the state after each GPS update. Raw IMU integration at the same\n"
              f"timestamps: {metrics['raw_imu_integration_rmse_at_gps_times_m_per_s']:.3f} m/s RMSE; 100 Hz all-step KF RMSE: "
              f"{metrics['kf_velocity_rmse_all_steps_m_per_s']:.3f} m/s.",
              size=8.3, color=GRAY)
        label(page, .07, .681, "PARAMETER IDENTIFICATION: LIMITATION", size=10,
              weight="bold")
        label(page, .07, .654,
              f"Final CdA = {cda[-1]:.3f} m² (truth 0.650); Crr = {crr[-1]:.3f} (truth 0.015). Plot: 5–60 s.",
              size=8.8, color=GRAY)
        late = t >= 5
        p1 = page.add_axes([.12, .455, .79, .17])
        p1.plot(t[late], cda[late], color=BLUE, linewidth=1, label="RLS")
        p1.axhline(.65, color=ORANGE, linestyle="--", linewidth=1, label="Truth")
        p1.set_ylabel("CdA [m²]")
        p1.legend(ncol=2, fontsize=7.5)
        p2 = page.add_axes([.12, .27, .79, .145], sharex=p1)
        p2.plot(t[late], crr[late], color=BLUE, linewidth=1)
        p2.axhline(.015, color=ORANGE, linestyle="--", linewidth=1)
        p2.set(xlabel="Time [s]", ylabel="Crr [-]")
        label(page, .07, .224, "WHAT THIS RUN DOES AND DOES NOT SHOW", size=10,
              weight="bold")
        label(page, .07, .196,
              "KF has lower speed RMSE than GPS against simulated truth in this seeded run.\n"
              "RLS parameters do not recover the known values; identification needs further study.\n"
              "No real vehicle, hardware-in-loop, fault-injection or multi-seed validation is shown.",
              size=8.5, color=GRAY)
        label(page, .07, .103,
              "Method: seed 42; 60 s; 0.01 s step; constant 3000 N drive force.\n"
              "Source, exact metrics and reproduction commands are included in the ZIP.",
              size=7.8, color=GRAY)
        pdf.savefig(page)
        page.savefig(FIGURES / "overview_page_2.png", dpi=180)
        plt.close(page)

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
