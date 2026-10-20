# vehicle-sensor-state-estimation
Python vehicle simulation with noisy IMU/GPS measurements, Kalman filtering for velocity and bias estimation, and exploratory RLS road-load parameter identification.
# Vehicle Sensor State Estimation

A Python project combining a longitudinal vehicle model, simulated sensor measurements, and state estimation.

The simulation models aerodynamic drag and rolling resistance, with IMU measurements at 100 Hz and GPS speed updates at 10 Hz. A two-state Kalman filter estimates vehicle speed and accelerometer bias. Recursive least squares explores identification of aerodynamic drag area and rolling resistance.

## Results

In a 60-second simulation with random seed 42, velocity RMSE at the same 600 GPS update timestamps was:

- Raw GPS: 0.475 m/s
- Kalman filter, after GPS updates: 0.272 m/s

This represents approximately 42.9% lower RMSE in this specific run. Estimates were compared against simulated ground truth.

## Limitations

RLS did not recover the known road-load parameters in this scenario. The project demonstrates nominal software simulation; it does not establish performance on a physical vehicle or across multiple random seeds.

Source code, reproduction instructions, result figures and a project overview PDF are included.
