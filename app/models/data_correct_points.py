import pandas as pd
import numpy as np
pha_measure_name = {
    1: "Phase 1",
    2: "Phase 2",
    3: "Phase 3",
    4: "Phase 4",
}
mag_measure_name = {
    1: "Magnitude 1",
    2: "Magnitude 2",
    3: "Magnitude 3",
    4: "Magnitude 4",
}
def extrapole_phase(data,flag=0):
    arr = np.zeros(10)
    if flag == 0:   
        for k in range(1,9):
            arr[k] = data["Phase 1"][k+1] - data["Phase 1"][k]
        delta_avg = arr.mean()
        delta_std = arr.std()

        for k in range(2,len(data["Phase 1"])-1):
            l_inf = np.abs(data["Phase 1"][k-1] -  data["Phase 1"][k])
            l_sup = np.abs(data["Phase 1"][k+1] -  data["Phase 1"][k])

            if (l_inf > (delta_avg + 2*delta_std)) and (l_sup > (delta_avg + 2*delta_std)):
                data["Phase 1"][k] = (data["Phase 1"][k-1] + data["Phase 1"][k+1]) / 2
                data["Magnitude 1"][k] = (data["Magnitude 1"][k-1] + data["Magnitude 1"][k+1]) / 2         
    elif flag == 1:
        for n in range (1,4):
            measure = pha_measure_name[n]
            measure_mag = mag_measure_name[n]
            for k in range(1,9):
                arr[k] = data[measure][k+1] - data[measure][k]
            delta_avg = arr.mean()
            delta_std = arr.std()

            for k in range(2,len(data[measure])-1):
                l_inf = np.abs(data[measure][k-1] -  data[measure][k])
                l_sup = np.abs(data[measure][k+1] -  data[measure][k])

                if (l_inf > (delta_avg + 2*delta_std)) and (l_sup > (delta_avg + 2*delta_std)):
                    data[measure][k] = (data[measure][k-1] + data[measure][k+1]) / 2
                    data[measure_mag][k] = (data[measure_mag][k-1] + data[measure_mag][k+1]) / 2   
    

def apply_extrapole(flag = 0):
    if flag == 0:
        match1_df = pd.read_csv('./data/match1.csv')
        match2_df = pd.read_csv('./data//match2.csv')
        open1_df = pd.read_csv('./data/open1.csv')
        open2_df = pd.read_csv('./data/open2.csv')
        short1_df = pd.read_csv('./data/short1.csv')
        short2_df = pd.read_csv('./data/short2.csv')
        thru_df = pd.read_csv('./data/thru.csv')
        

        for k in range (1,10):
            extrapole_phase(match1_df)
            extrapole_phase(match2_df)
            extrapole_phase(open1_df)
            extrapole_phase(open2_df)
            extrapole_phase(short1_df)
            extrapole_phase(short2_df)
            extrapole_phase(thru_df,1)

        match1_df.to_csv("./data/match1_extrapole.csv",index=False)
        match2_df.to_csv("./data/match2_extrapole.csv",index=False)
        open1_df.to_csv("./data/open1_extrapole.csv",index=False)
        open2_df.to_csv("./data/open2_extrapole.csv",index=False)
        short1_df.to_csv("./data/short1_extrapole.csv",index=False)
        short2_df.to_csv("./data/short2_extrapole.csv",index=False)
        thru_df.to_csv("./data/thru_extrapole.csv",index=False)
    
    else :
        dut_df = pd.read_csv('./data/dut_med.csv')

        for k in range (1,10):
            extrapole_phase(dut_df,1)
        dut_df.to_csv("./data/dut_med_extrapole.csv",index=False)
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

def apply_phase_correction(flag = 0):
    if flag == 0:
        match1_df = pd.read_csv('./data/match1_extrapole.csv')
        match2_df = pd.read_csv('./data/match2_extrapole.csv')
        open1_df = pd.read_csv('./data/open1_extrapole.csv')
        open2_df = pd.read_csv('./data/open2_extrapole.csv')
        short1_df = pd.read_csv('./data/short1_extrapole.csv')
        short2_df = pd.read_csv('./data/short2_extrapole.csv')
        thru_df = pd.read_csv('./data/thru_extrapole.csv')
        
        phase_correction(match1_df["Phase 1"])
        phase_correction(match2_df["Phase 1"])
        phase_correction(open1_df["Phase 1"])
        phase_correction(open2_df["Phase 1"])
        phase_correction(short1_df["Phase 1"])
        phase_correction(short2_df["Phase 1"])
        phase_correction(thru_df["Phase 1"])
        phase_correction(thru_df["Phase 2"])
        phase_correction(thru_df["Phase 3"])
        phase_correction(thru_df["Phase 4"])

        match1_df.to_csv("./data/match1_pha_corr.csv",index=False)
        match2_df.to_csv("./data/match2_pha_corr.csv",index=False)
        open1_df.to_csv("./data/open1_pha_corr.csv",index=False)
        open2_df.to_csv("./data/open2_pha_corr.csv",index=False)
        short1_df.to_csv("./data/short1_pha_corr.csv",index=False)
        short2_df.to_csv("./data/short2_pha_corr.csv",index=False)
        thru_df.to_csv("./data/thru_pha_corr.csv",index=False)

    else:
        dut_df = pd.read_csv('./data/dut_med_extrapole.csv')

        phase_correction(dut_df["Phase 1"])
        phase_correction(dut_df["Phase 2"])
        phase_correction(dut_df["Phase 3"])
        phase_correction(dut_df["Phase 4"])

        dut_df.to_csv("./data/dut_med_corr.csv",index=False)


    print("Phase Correction applied")
