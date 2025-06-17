#!/usr/bin/env python3
"""
Generate three synthetic OBD-II CSVs, using relative output paths.

Usage in VS Code terminal (with your venv activated):

  cd c:/Users/aalla/obd_backend
  python Filter_obs_csv.py

Outputs in your working directory:
  - clean_may_1-21.csv
  - april_1-21_20pct.csv
  - march_1-21_50pct_allfaults.csv
"""
import os
import uuid
import argparse
import numpy as np
import pandas as pd


def generate_base_df(start_date, end_date, n):
    start_ts = pd.Timestamp(start_date).timestamp()
    end_ts = pd.Timestamp(end_date).timestamp()
    rand_ts = np.random.uniform(start_ts, end_ts, size=n)
    return pd.DataFrame({
        'user_id': [str(uuid.uuid4()) for _ in range(n)],
        'timestamp': pd.to_datetime(rand_ts, unit='s'),
        'ENGINE_RUN_TIME': np.random.uniform(0, 3600, n),
        'ENGINE_RPM': np.random.uniform(0, 6000, n),
        'VEHICLE_SPEED': np.random.uniform(0, 200, n),
        'THROTTLE': np.random.uniform(0, 100, n),
        'ENGINE_LOAD': np.random.uniform(0, 100, n),
        'COOLANT_TEMPERATURE': np.random.uniform(70, 100, n),
        'LONG_TERM_FUEL_TRIM_BANK_1': np.random.uniform(-10, 10, n),
        'INTAKE_MANIFOLD_PRESSURE': np.random.uniform(20, 50, n),
        'CONTROL_MODULE_VOLTAGE': np.random.uniform(11, 15, n),
        'PEDAL_D': np.random.uniform(0, 100, n),
        # add additional columns as needed
    })


def detect_fault(r):
    if r.COOLANT_TEMPERATURE > 120:
        return 'Overheating'
    if r.CONTROL_MODULE_VOLTAGE < 11:
        return 'Low Voltage'
    if (r.PEDAL_D > 50) and (r.THROTTLE < 15):
        return 'Throttle Lag'
    if (r.INTAKE_MANIFOLD_PRESSURE > 55) and (r.LONG_TERM_FUEL_TRIM_BANK_1 > 20):
        return 'Vacuum Leak'
    return None


def inject_faults(df, pct, types):
    df = df.copy()
    n = len(df)
    df['injected_fault_type'] = None
    df['is_synthetic'] = 0
    df['source'] = 'clean'

    num = int(pct * n)
    if num > 0 and types:
        idx = np.random.choice(n, num, replace=False)
        chunks = np.array_split(idx, len(types))
        for fault, ids in zip(types, chunks):
            if fault == 'Overheating':
                df.loc[ids, 'COOLANT_TEMPERATURE'] = 130
            elif fault == 'Throttle Lag':
                df.loc[ids, 'PEDAL_D'] = 60
                df.loc[ids, 'THROTTLE'] = 10
            elif fault == 'Low Voltage':
                df.loc[ids, 'CONTROL_MODULE_VOLTAGE'] = 9
            elif fault == 'Vacuum Leak':
                df.loc[ids, 'INTAKE_MANIFOLD_PRESSURE'] = 60

            df.loc[ids, 'injected_fault_type'] = fault
            df.loc[ids, 'is_synthetic'] = 1
            df.loc[ids, 'source'] = 'injected'

    df['detected_fault'] = df.apply(detect_fault, axis=1)
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir", "-o",
        default=".",
        help="Directory to save CSVs (defaults to current folder)"
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    n = 50000

    # 1) Clean May 1–21, 2025
    df1 = generate_base_df('2025-05-01', '2025-05-21', n)
    df1 = inject_faults(df1, 0.0, [])
    df1.to_csv(os.path.join(args.output_dir, "clean_may_1-21.csv"), index=False)

    # 2) April 1–21, 2025 with 20% faults (Overheating & Throttle Lag)
    df2 = generate_base_df('2025-04-01', '2025-04-21', n)
    df2 = inject_faults(df2, 0.2, ['Overheating','Throttle Lag'])
    df2.to_csv(os.path.join(args.output_dir, "april_1-21_20pct.csv"), index=False)

    # 3) March 1–21, 2025 with 50% mixed faults (Overheating, Throttle Lag, Low Voltage, Vacuum Leak)
    df3 = generate_base_df('2025-03-01', '2025-03-21', n)
    df3 = inject_faults(df3, 0.5, ['Overheating','Throttle Lag','Low Voltage','Vacuum Leak'])
    df3.to_csv(os.path.join(args.output_dir, "march_1-21_50pct_allfaults.csv"), index=False)

    print("All CSV files written to:", os.path.abspath(args.output_dir))

if __name__ == "__main__":
    main()
