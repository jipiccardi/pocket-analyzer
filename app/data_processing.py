import pandas as pd
import numpy as np


def calculate_error_coefficients():
    match1_df = pd.read_csv('./data/match1_pha_corr.csv')
    match2_df = pd.read_csv('./data/match2_pha_corr.csv')
    open1_df = pd.read_csv('./data/open1_pha_corr.csv')
    open2_df = pd.read_csv('./data/open2_pha_corr.csv')
    short1_df = pd.read_csv('./data/short1_pha_corr.csv')
    short2_df = pd.read_csv('./data/short2_pha_corr.csv')
    thru_df = pd.read_csv('./data/thru_pha_corr.csv')

     

    match1_df["s11_m1"] = match1_df["Magnitude 1"] * np.exp(1j * np.radians(match1_df["Phase 1"]))
    open1_df['s11_o1'] = open1_df["Magnitude 1"] * np.exp(1j * np.radians(open1_df["Phase 1"]))
    short1_df['s11_s1'] = short1_df["Magnitude 1"] * np.exp(1j * np.radians(short1_df["Phase 1"]))

    match2_df["s22_m2"] = match2_df["Magnitude 1"] * np.exp(1j * np.radians(match2_df["Phase 1"]))
    open2_df['s22_o2'] = open2_df["Magnitude 1"] * np.exp(1j * np.radians(open2_df["Phase 1"]))
    short2_df['s22_s2'] = short2_df["Magnitude 1"] * np.exp(1j * np.radians(short2_df["Phase 1"]))

    thru_df['s11_t'] = thru_df["Magnitude 1"] * np.exp(1j * np.radians(thru_df["Phase 1"]))
    thru_df['s12_t'] = thru_df["Magnitude 2"] * np.exp(1j * np.radians(thru_df["Phase 2"]))
    thru_df['s22_t'] = thru_df["Magnitude 3"] * np.exp(1j * np.radians(thru_df["Phase 3"]))
    thru_df['s21_t'] = thru_df["Magnitude 4"] * np.exp(1j * np.radians(thru_df["Phase 4"]))

    errors_df = pd.DataFrame()

    errors_df['frequency'] = match1_df['Frequency']

    errors_df['e00'] = match1_df['s11_m1']
    errors_df['e11'] = (open1_df['s11_o1'] + short1_df['s11_s1'] - 2*errors_df['e00'])/(open1_df['s11_o1'] - short1_df['s11_s1'])
    errors_df['e1001'] = (-2*(open1_df['s11_o1'] - errors_df['e00'])*(short1_df['s11_s1'] - errors_df['e00']))/(open1_df['s11_o1'] - short1_df['s11_s1'])

    errors_df['deltae'] = errors_df['e00'] * errors_df['e11'] - errors_df['e1001']

    errors_df['e22'] = (thru_df['s11_t'] - errors_df['e00']) / (thru_df['s11_t']*errors_df['e11'] - errors_df['deltae'])
    errors_df['e1032'] = (thru_df['s21_t'])*(1 - errors_df['e11']*errors_df['e22'])

    errors_df['e33'] = match2_df['s22_m2']
    errors_df['e_22'] = (open2_df['s22_o2'] + short2_df['s22_s2'] - 2*errors_df['e33'])/(open2_df['s22_o2'] - short2_df['s22_s2'])
    errors_df['e2332'] = (-2 * (open2_df['s22_o2'] - errors_df['e33']) * (short2_df['s22_s2'] - errors_df['e33'])) / (open2_df['s22_o2'] - short2_df['s22_s2'])

    errors_df['deltaeprima'] = errors_df['e33'] * errors_df['e_22'] - errors_df['e2332']

    errors_df['e_11'] = (thru_df['s22_t'] - errors_df['e33']) / (thru_df['s22_t']*errors_df['e_22'] - errors_df['deltaeprima'])
    errors_df['e2301'] = (thru_df['s12_t'])*(1 - errors_df['e33']*errors_df['e_11'])

    errors_df.to_csv("./data/errors_df.csv")



def calculate_dut_coefficients():
    errors_df = pd.read_csv('./data/errors_df.csv').astype(complex)
    dut_med_df = pd.read_csv('./data/dut_med_corr.csv')
    dut_med_df['s11_m'] = dut_med_df["Magnitude 1"] * np.exp(1j * np.radians(dut_med_df["Phase 1"]))
    dut_med_df['s12_m'] = dut_med_df["Magnitude 2"] * np.exp(1j * np.radians(dut_med_df["Phase 2"]))
    dut_med_df['s22_m'] = dut_med_df["Magnitude 3"] * np.exp(1j * np.radians(dut_med_df["Phase 3"]))
    dut_med_df['s21_m'] = dut_med_df["Magnitude 4"] * np.exp(1j * np.radians(dut_med_df["Phase 4"]))
    N_df = pd.DataFrame()
    N_df['N11'] = (dut_med_df['s11_m'] - errors_df['e00']) / errors_df['e1001']
    N_df['N12'] = (dut_med_df['s12_m']) / (errors_df['e2301'])
    N_df['N22'] = (dut_med_df['s22_m'] - errors_df['e33']) / errors_df['e2332']
    N_df['N21'] = (dut_med_df['s21_m']) / (errors_df['e1032'])
    D_df = pd.DataFrame()
    D_df['D'] = (1 + N_df['N11'] * errors_df['e11']) * (1 + N_df['N22'] * errors_df['e_22']) - N_df['N21'] * N_df['N12'] * errors_df['e22'] * errors_df['e_11']
    dut_c_complex_df = pd.DataFrame()
    dut_c_complex_df['s11_c'] = ((N_df['N11'] * (1 + N_df['N22'] * errors_df['e_22'])) - errors_df['e22'] * N_df['N21'] * N_df['N12']) / D_df['D']
    dut_c_complex_df['s12_c'] = (N_df['N12'] * (1 + N_df['N11'] * (errors_df['e11'] - errors_df['e_11']))) / D_df['D']
    dut_c_complex_df['s22_c'] = ((N_df['N22'] * (1 + N_df['N11'] * errors_df['e11'])) - errors_df['e_11'] * N_df['N21'] * N_df['N12']) / D_df['D']
    dut_c_complex_df['s21_c'] = (N_df['N21'] * (1 + N_df['N22'] * (errors_df['e_22'] - errors_df['e22']))) / D_df['D']
    dut_c_complex_df.to_csv("./data/dut_c_complex.csv")

    dut_c_df = pd.DataFrame()
    dut_c_df['freq'] = abs(errors_df['frequency']*1e5)
    dut_c_df['s11_mag'] = 20*np.log10(abs(dut_c_complex_df['s11_c']))
    dut_c_df['s11_pha'] = np.degrees(np.angle(dut_c_complex_df['s11_c']))
    dut_c_df['s21_mag'] = 20*np.log10(abs(dut_c_complex_df['s21_c']))
    dut_c_df['s21_pha'] = np.degrees(np.angle(dut_c_complex_df['s21_c']))
    dut_c_df['s22_mag'] = 20*np.log10(abs(dut_c_complex_df['s22_c']))
    dut_c_df['s22_pha'] = np.degrees(np.angle(dut_c_complex_df['s22_c']))
    dut_c_df['s12_mag'] = 20*np.log10(abs(dut_c_complex_df['s12_c']))
    dut_c_df['s12_pha'] = np.degrees(np.angle(dut_c_complex_df['s12_c']))
    df_cleaned = dut_c_df[~dut_c_df['freq'].duplicated(keep=False)]
    df_cleaned.to_csv("./data/dut_c.csv")
    df_cleaned.to_csv("./data/dut_c.s2p", sep='\t', header=False, index=False)

    s2p_header = "# Hz S DB R 50.000000\n"
    with open("./data/dut_c.s2p", "r") as file:
        lines = file.readlines()

    with open("./data/dut_c.s2p", "w") as file:
        file.write(s2p_header)
        file.writelines(lines)




