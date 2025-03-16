import pandas as pd
import numpy as np


def calculate_error_coefficients():
    match1_df = pd.read_csv('./data/match1.csv')
    match2_df = pd.read_csv('./data/match2.csv')
    open1_df = pd.read_csv('./data/open1.csv')
    open2_df = pd.read_csv('./data/open2.csv')
    short1_df = pd.read_csv('./data/short1.csv')
    short2_df = pd.read_csv('./data/short2.csv')
    thru_df = pd.read_csv('./data/thru.csv')

    match1_df["s11m"] = match1_df["Magnitude 1"] * np.exp(1j * np.radians(match1_df["Phase 1"]))
    open1_df['s11m'] = open1_df["Magnitude 1"] * np.exp(1j * np.radians(open1_df["Phase 1"]))
    short1_df['s11m'] = short1_df["Magnitude 1"] * np.exp(1j * np.radians(short1_df["Phase 1"]))

    match2_df["s22m"] = match2_df["Magnitude 1"] * np.exp(1j * np.radians(match2_df["Phase 1"]))
    open2_df['s22m'] = open2_df["Magnitude 1"] * np.exp(1j * np.radians(open2_df["Phase 1"]))
    short2_df['s22m'] = short2_df["Magnitude 1"] * np.exp(1j * np.radians(short2_df["Phase 1"]))

    thru_df['s11m'] = thru_df["Magnitude 1"] * np.exp(1j * np.radians(thru_df["Phase 1"]))
    #thru_df['s12m'] = thru_df["Magnitude 2"] * np.exp(1j * np.radians(thru_df["Phase 2"]))
    #thru_df['s22m'] = thru_df["Magnitude 3"] * np.exp(1j * np.radians(thru_df["Phase 3"]))
    #thru_df['s21m'] = thru_df["Magnitude 4"] * np.exp(1j * np.radians(thru_df["Phase 4"]))

    errors_df = pd.DataFrame()

    errors_df['frequency'] = match1_df['Frequency']

    errors_df['e00'] = match1_df['s11m']
    errors_df['e11'] = (open1_df['s11m'] + short1_df['s11m'] - 2*errors_df['e00'])/(open1_df['s11m'] - short1_df['s11m'])
    errors_df['e1001'] = (-2*(open1_df['s11m'] - errors_df['e00'])*(short1_df['s11m'] - errors_df['e00']))/(open1_df['s11m'] - short1_df['s11m'])

    errors_df['deltae'] = errors_df['e00'] * errors_df['e11'] - errors_df['e1001']

    #errors_df['e22'] = (thru_df['s11m'] - errors_df['e00']) / (thru_df['s11m']*errors_df['e11'] - errors_df['deltae'])
    #errors_df['e1032'] = (thru_df['s21m'])*(1 - errors_df['e11']*errors_df['e22'])

    errors_df['e33'] = match2_df['s22m']
    errors_df['e_22'] = (open2_df['s22m'] + short2_df['s22m'] - 2*errors_df['e33'])/(open2_df['s22m'] - short2_df['s22m'])
    errors_df['e2332'] = (-2 * (open2_df['s22m'] - errors_df['e33']) * (short2_df['s22m'] - errors_df['e33'])) / (open2_df['s22m'] - short2_df['s22m'])

    errors_df['deltaeprima'] = errors_df['e33'] * errors_df['e_22'] - errors_df['e2332']

    #errors_df['e_11'] = (thru_df['s22m'] - errors_df['e33']) / (thru_df['s22m']*errors_df['e_22'] - errors_df['deltaeprima'])
    #errors_df['e2301'] = (thru_df['s12m'])*(1 - errors_df['e33']*errors_df['e_11'])

    errors_df.to_csv("./data/errors_df.csv")
