import pandas as pd
import numpy as np

def extrapole_phase(array):
    arr = np.zeros(10)
    for k in range(1,9):
        arr[k] = array[k+1] - array[k]
    delta_avg = arr.mean()
    delta_std = arr.std()

    for k in range(2,len(array)-1):
        l_inf = np.abs(array[k-1] -  array[k])
        l_sup = np.abs(array[k+1] -  array[k])

        if (l_inf > (delta_avg + 1*delta_std)) and (l_sup > (delta_avg + 1*delta_std)):
            array[k] = (array[k-1] + array[k+1]) / 2
    

def apply_extrapole():
    match1_df = pd.read_csv('./data/calib2_16_mar/match1.csv')
    match2_df = pd.read_csv('./data/calib2_16_mar/match2.csv')
    open1_df = pd.read_csv('./data/calib2_16_mar/open1.csv')
    open2_df = pd.read_csv('./data/calib2_16_mar/open2.csv')
    short1_df = pd.read_csv('./data/calib2_16_mar/short1.csv')
    short2_df = pd.read_csv('./data/calib2_16_mar/short2.csv')
    thru_df = pd.read_csv('./data/calib2_16_mar/thru.csv')

    for k in range (1,10):
        extrapole_phase(match1_df["Phase 1"])
        extrapole_phase(match2_df["Phase 1"])
        extrapole_phase(open1_df["Phase 1"])
        extrapole_phase(open2_df["Phase 1"])
        extrapole_phase(short1_df["Phase 1"])
        extrapole_phase(short2_df["Phase 1"])

    match1_df.to_csv("./data/calib2_16_mar/match1_extrapole.csv")
    match2_df.to_csv("./data/calib2_16_mar/match2_extrapole.csv")
    open1_df.to_csv("./data/calib2_16_mar/open1_extrapole.csv")
    open2_df.to_csv("./data/calib2_16_mar/open2_extrapole.csv")
    short1_df.to_csv("./data/calib2_16_mar/short1_extrapole.csv")
    short2_df.to_csv("./data/calib2_16_mar/short2_extrapole.csv")

    print("Extrapole applied")


def phase_correction(PhaseVector):
    phase = np.copy(PhaseVector)
    
    for n in range(4 , len(PhaseVector) - 4):
        avg_l = (PhaseVector[n-4] + PhaseVector[n-3] + PhaseVector[n-2] + PhaseVector[n-1]) / 4
        avg_h = (PhaseVector[n+4] + PhaseVector[n+3] + PhaseVector[n+2] + PhaseVector[n+1]) / 4
        if (PhaseVector[n] > avg_l and PhaseVector[n] < avg_h):
            phase[n] = -PhaseVector[n]
        else:
            phase[n] = PhaseVector[n]
    PhaseVector[:] = phase
#    arr = np.zeros(len(PhaseVector))
#    phase = PhaseVector
#    for n in range(1 , len(PhaseVector)):
#        avg_l = PhaseVector[n-1]
#        avg_h = PhaseVector[n+1]
#        if (PhaseVector[n] > avg_l and PhaseVector[n] < avg_h):
#            phase[n] = -PhaseVector[n]
#            arr[n] = 1
#        print (avg_l)
#        print (avg_h)
#    
#    for n in range(4 , len(PhaseVector) - 4):
#        if (arr[n] == 0) :
#            avg_l = (PhaseVector[n-4] + PhaseVector[n-3] + PhaseVector[n-2] + PhaseVector[n-1]) / 4
#            avg_h = (PhaseVector[n+4] + PhaseVector[n+3] + PhaseVector[n+2] + PhaseVector[n+1]) / 4
#            if (PhaseVector[n] > avg_l and PhaseVector[n] < avg_h):
#                phase[n] = -PhaseVector[n]
#            print ("avg_l: ",avg_l)
#            print ("avg_h: ",avg_h)
#            print ("n: ", PhaseVector[n])
#    PhaseVector = phase

def apply_phase_correction():
     
    match1_df = pd.read_csv('./data/calib2_16_mar/match1_extrapole.csv')
    match2_df = pd.read_csv('./data/calib2_16_mar/match2_extrapole.csv')
    open1_df = pd.read_csv('./data/calib2_16_mar/open1_extrapole.csv')
    open2_df = pd.read_csv('./data/calib2_16_mar/open2_extrapole.csv')
    short1_df = pd.read_csv('./data/calib2_16_mar/short1_extrapole.csv')
    short2_df = pd.read_csv('./data/calib2_16_mar/short2_extrapole.csv')
    
    phase_correction(match1_df["Phase 1"])
    phase_correction(match2_df["Phase 1"])
    phase_correction(open1_df["Phase 1"])
    phase_correction(open2_df["Phase 1"])
    phase_correction(short1_df["Phase 1"])
    phase_correction(short2_df["Phase 1"])

    match1_df.to_csv("./data/calib2_16_mar/match1_pha_corr.csv")
    match2_df.to_csv("./data/calib2_16_mar/match2_pha_corr.csv")
    open1_df.to_csv("./data/calib2_16_mar/open1_pha_corr.csv")
    open2_df.to_csv("./data/calib2_16_mar/open2_pha_corr.csv")
    short1_df.to_csv("./data/calib2_16_mar/short1_pha_corr.csv")
    short2_df.to_csv("./data/calib2_16_mar/short2_pha_corr.csv")
    print("Phase Correction applied")

apply_extrapole()
apply_phase_correction()