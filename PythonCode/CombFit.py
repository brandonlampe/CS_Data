import sys
import numpy as np
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import FuncFormatter
from scipy import interpolate
# from scipy import optimize
from scipy import linalg
import pickle

# relative path to module
sys.path.append(sys.path[0])
import DataAnalysisFunc as daf
REPO_DIR = os.path.dirname(sys.path[0])  # PATH TO REPOSITORY DIRECTORY

##################################
# CHOOSE ANALYSIS OPTIONS (INTEGER VALUES)
##################################

PLOT = 1  # SHOULD THE RESULTS BE PLOTTED
SAVEFIG = 0  # SHOULD THE PLOTS BE SAVED
SAVECSV = 0  # SHOULD A .CSV OF THE RESULTS BE SAVED
PLOT_CSMOD = 0  # PLOT RESULTS FROM CS MODEL, MUST DEFINE FILE TO LOAD DATA
STAGE_ID = '_COMB'  # '_Stage01'  # IF TEST CONSISTS OF MULTIPLE STAGES

# IF RESULTS FROM CS MODEL ARE TO BE PLOTTED ALSO, DEFINE PATH TO DATA
PATH_CSMOD = '/Users/Lampe/GrantNo456417/Modeling/constit/' + \
             'UNM_WP_HY_175_04_OUT' + '.csv'

# DEFINE THE LIMITS FOR PLOTTING - DIRECTLY FROM TEST DATA
LOAD_START = 0.00  # DAYS
LOAD_END = 0.00385  # DAYS
CREEP_START = 0.0025  # START PLOTTING (days), IF NO ALTDOMAIN THEN FIT ALSO
CREEP_END = 4.745  # END PLOTTING (days), IF NO ALTDOMAIN THEN FIT ALSO

PCON_START = 0.0  # CONFINING PRESSURE AT START (MPa)
PPOR_START = 0.0  # PORE PRESSURE AT START (MPa)

# define if/how many points shold be removed
LOAD_TRIM = 1  # NUMBER OF POINTS TO REMOVE FROM END
CREEP_TRIM = 2  # NUMBER OF POINTS TO REMOVE FROM BEGINNING


# COMPLETED TESTS
# FOLDER_DIR = 'UNM_WP_HY_175_04'
# FOLDER_DIR = 'UNM_WP_HY_175_03'
# FOLDER_DIR = 'UNM_WP_HY_175_01'

# NOT COMPLETED TESTS
# FOLDER_DIR = 'UNM_WP_HY_90_02'
# FOLDER_DIR = 'UNM_WP_HY_90_03'
FOLDER_DIR = 'UNM_WP_HY_90_04'
# FOLDER_DIR = 'UNM_WP_HY_90_08'
# FOLDER_DIR = 'UNM_WP_HY_175_09'


CREEP_DIR = 'CREEP_FIT/'
LOAD_DIR = 'LOADING_FIT/'
TEST_NAME = FOLDER_DIR[10:]
TEST_NUMBER = FOLDER_DIR[-5:]

PATH = REPO_DIR + '/' + FOLDER_DIR + '/'
CREEP_FIT_PARM_PATH = PATH + CREEP_DIR + TEST_NUMBER + '_CREEP_PARM.bin'
TEST_SPEC_PATH = PATH + CREEP_DIR + TEST_NUMBER + '_CREEP_SPEC.bin'
LOAD_FIT_PARM_PATH = PATH + LOAD_DIR + TEST_NUMBER + '_LOAD_PARM.bin'


print("Loading Data Path: " + LOAD_FIT_PARM_PATH)
# read parameter values from pickled files
with open(CREEP_FIT_PARM_PATH, 'rb') as handle:
    CREEP_PARM = pickle.loads(handle.read())

with open(LOAD_FIT_PARM_PATH, 'rb') as handle:
    LOAD_PARM = pickle.loads(handle.read())

with open(TEST_SPEC_PATH, 'rb') as handle:
    TEST_SPEC = pickle.loads(handle.read())

print(TEST_SPEC)
# GET TEST SPECIFICATIONS
PPOR_END = TEST_SPEC["average pore pressure"]  # pore PRESSURE (MPa)
PCON_END = TEST_SPEC["average confining pressure"]  # CONFINING PRESSURE (MPa)
PARTICLE_SIZE = TEST_SPEC["mean particle size"]  # mm
ADDED_WATER = TEST_SPEC["percent added water by weight"]
TEMP = TEST_SPEC["average temperature"]  # degree C

##################################
# setup plotting domains
##################################
STEP_SIZE_SEC = np.array(([10, 100]))  # STEP SIZES (SECONS)
# LOAD (FUNCTION OF PRESSURE)
LOAD_DUR_DAY = LOAD_END - LOAD_START
LOAD_DUR_SEC = LOAD_DUR_DAY * 24 * 3600
LOAD_TIME_SEC = np.arange(0, LOAD_DUR_SEC, STEP_SIZE_SEC[0])  # TIME OF LOADING
LOAD_TIME_DAY = LOAD_TIME_SEC / (24 * 3600)
LOAD_PCON = np.linspace(PCON_START, PCON_END, num=len(LOAD_TIME_SEC))
LOAD_PPOR = np.linspace(PPOR_START, PPOR_END, num=len(LOAD_TIME_SEC))
LOAD_STEP_TOTAL = len(LOAD_TIME_SEC)
print("Number of time steps for load analysis :" + str(LOAD_STEP_TOTAL))

# CREEP (FUNCTION OF TIME)
CREEP_DUR_DAY = CREEP_END - CREEP_START
CREEP_DUR_SEC = CREEP_DUR_DAY * 24 * 3600
CREEP_TIME_END_01 = 3600  # SECONDS
CREEP_TIME_END_02 = 72000  # SECONDS
CREEP_STEP_NUMBER_FINAL = 400  # NUMBER OF INCREMENTS
CREEP_TIME_01 = np.arange(0, CREEP_TIME_END_01, STEP_SIZE_SEC[0])
CREEP_TIME_02 = np.arange(CREEP_TIME_END_01,
                          CREEP_TIME_END_02,
                          STEP_SIZE_SEC[1])
CREEP_TIME_03 = np.linspace(CREEP_TIME_END_02,
                            CREEP_DUR_SEC,
                            CREEP_STEP_NUMBER_FINAL)
CREEP_TIME_SEC = np.concatenate((CREEP_TIME_01,
                                 CREEP_TIME_02,
                                 CREEP_TIME_03), axis=0)
CREEP_TIME_DAY = CREEP_TIME_SEC / (24 * 3600)
CREEP_PCON = np.ones(len(CREEP_TIME_DAY)) * PCON_END
CREEP_PPOR = np.ones(len(CREEP_TIME_DAY)) * PPOR_END
CREEP_STEP_TOTAL = len(CREEP_TIME_SEC)
print("Number of time steps for creep analysis :" + str(CREEP_STEP_TOTAL))

##################################
# CALL FITTING FUNCTIONS
##################################
LOAD_FDEN = daf.gompertz(x=LOAD_PCON,
                         intercept=LOAD_PARM['intercept'],
                         start=LOAD_PARM['start'],
                         a=LOAD_PARM['a'],
                         b=LOAD_PARM['b'],
                         c=LOAD_PARM['c'])

CREEP_FDEN = daf.schnute(x=CREEP_TIME_DAY + CREEP_START,
                         start=CREEP_PARM['start'],
                         end=CREEP_PARM['end'],
                         a=CREEP_PARM['a'],
                         b=CREEP_PARM['b'],
                         c=CREEP_PARM['c'],
                         d=CREEP_PARM['d'])

##################################
# CALCULATE VALUES FOR EXPORT
##################################
LOAD_FDEN0 = LOAD_FDEN[0]  # INITIAL FRACTIONAL DENSITY
LOAD_VSTRN = -np.log(LOAD_FDEN0 / LOAD_FDEN)  # POSITIVE IN COMPRESSION
LOAD_DELTA_VSTRN = np.gradient(LOAD_VSTRN)
LOAD_DELTA_SEC = np.gradient(LOAD_TIME_SEC)
LOAD_VSTRN_RATE = LOAD_DELTA_VSTRN / LOAD_DELTA_SEC
LOAD_PSOL = (LOAD_PCON - (1 - LOAD_FDEN) * LOAD_PPOR) / LOAD_FDEN

CREEP_FDEN0 = CREEP_FDEN[0]  # INITIAL FRACTIONAL DENSITY
CREEP_VSTRN = -np.log(LOAD_FDEN0 / CREEP_FDEN)  # POSITIVE IN COMPRESSION
CREEP_DELTA_VSTRN = np.gradient(CREEP_VSTRN)
CREEP_DELTA_SEC = np.gradient(CREEP_TIME_SEC)
CREEP_VSTRN_RATE = CREEP_DELTA_VSTRN / CREEP_DELTA_SEC
CREEP_PSOL = (CREEP_PCON - (1 - CREEP_FDEN) * CREEP_PPOR) / CREEP_FDEN
# print("load fden : " + str(LOAD_FDEN[-5:]))
# print("creep fden: " + str(CREEP_FDEN[0:5]))
##################################
# COMBINE LOAD AND CREEP STAGES INTO SINGLE VECTORS
##################################
COMB_FDEN = np.concatenate((LOAD_FDEN[:-LOAD_TRIM], CREEP_FDEN[CREEP_TRIM:]),
                           axis=0)
COMB_VSTRN = np.concatenate((LOAD_VSTRN[:-LOAD_TRIM],
                             CREEP_VSTRN[CREEP_TRIM:]), axis=0)
COMB_VSTRN_RATE = np.concatenate((LOAD_VSTRN_RATE[:-LOAD_TRIM],
                                  CREEP_VSTRN_RATE[CREEP_TRIM:]), axis=0)
CREEP_TIME_ADJ = LOAD_TIME_DAY[-(LOAD_TRIM + 1)]
COMB_TIME_DAY = np.concatenate((LOAD_TIME_DAY[:-LOAD_TRIM],
                                CREEP_TIME_ADJ + CREEP_TIME_DAY[CREEP_TRIM:]),
                               axis=0)
COMB_TIME_SEC = COMB_TIME_DAY * 24 * 3600
COMB_PCON = np.concatenate((LOAD_PCON[:-LOAD_TRIM],
                            CREEP_PCON[CREEP_TRIM:]),
                           axis=0)
COMB_PPOR = np.concatenate((LOAD_PPOR[:-LOAD_TRIM],
                            CREEP_PPOR[CREEP_TRIM:]),
                           axis=0)
COMB_PSOL = np.concatenate((LOAD_PSOL[:-LOAD_TRIM],
                            CREEP_PSOL[CREEP_TRIM:]),
                           axis=0)

# CALCULATE COMPRESIBILITIES
RHOIS = 2160  # KG/M3
LOAD_DELTA_PCON = np.gradient(LOAD_PCON)
LOAD_DENISTY = RHOIS * LOAD_FDEN
LOAD_DELTA_DENSITY = np.gradient(LOAD_DENISTY)
LOAD_BULK_DRAINED = LOAD_DENISTY * LOAD_DELTA_PCON / LOAD_DELTA_DENSITY  # MPA
LOAD_COMP_DRAINED = 1 / LOAD_BULK_DRAINED

# CREATE ARRAYS FOR OUTPUT
OUT_LOAD = np.zeros((len(LOAD_TIME_DAY[:-LOAD_TRIM]), 10))
OUT_LOAD[:, 0] = LOAD_TIME_SEC[:-LOAD_TRIM]
OUT_LOAD[:, 1] = LOAD_TIME_DAY[:-LOAD_TRIM]
OUT_LOAD[:, 2] = LOAD_PCON[:-LOAD_TRIM]
OUT_LOAD[:, 3] = LOAD_PPOR[:-LOAD_TRIM]
OUT_LOAD[:, 4] = LOAD_FDEN[:-LOAD_TRIM]
OUT_LOAD[:, 5] = LOAD_VSTRN[:-LOAD_TRIM]
OUT_LOAD[:, 6] = LOAD_VSTRN_RATE[:-LOAD_TRIM]
OUT_LOAD[:, 7] = PARTICLE_SIZE * np.ones(len(LOAD_TIME_DAY[:-LOAD_TRIM]))  # mm
OUT_LOAD[:, 8] = ADDED_WATER * np.ones(len(LOAD_TIME_DAY[:-LOAD_TRIM]))  # % weight
OUT_LOAD[:, 9] = TEMP * np.ones(len(LOAD_TIME_DAY[:-LOAD_TRIM]))  # degree C

OUT_CREEP = np.zeros((len(CREEP_TIME_DAY[CREEP_TRIM:]), 10))
OUT_CREEP[:, 0] = CREEP_TIME_SEC[CREEP_TRIM:]
OUT_CREEP[:, 1] = CREEP_TIME_DAY[CREEP_TRIM:]
OUT_CREEP[:, 2] = CREEP_PCON[CREEP_TRIM:]
OUT_CREEP[:, 3] = CREEP_PPOR[CREEP_TRIM:]
OUT_CREEP[:, 4] = CREEP_FDEN[CREEP_TRIM:]
OUT_CREEP[:, 5] = CREEP_VSTRN[CREEP_TRIM:]
OUT_CREEP[:, 6] = CREEP_VSTRN_RATE[CREEP_TRIM:]
OUT_CREEP[:, 7] = PARTICLE_SIZE * np.ones(len(CREEP_TIME_DAY[CREEP_TRIM:]))  # mm
OUT_CREEP[:, 8] = ADDED_WATER * np.ones(len(CREEP_TIME_DAY[CREEP_TRIM:]))  # % weight
OUT_CREEP[:, 9] = TEMP * np.ones(len(CREEP_TIME_DAY[CREEP_TRIM:]))  # degree C

OUT_COMB = np.zeros((len(COMB_TIME_DAY), 10))
OUT_COMB[:, 0] = COMB_TIME_SEC
OUT_COMB[:, 1] = COMB_TIME_DAY
OUT_COMB[:, 2] = COMB_PCON
OUT_COMB[:, 3] = COMB_PPOR
OUT_COMB[:, 4] = COMB_FDEN
OUT_COMB[:, 5] = COMB_VSTRN
OUT_COMB[:, 6] = COMB_VSTRN_RATE
OUT_COMB[:, 7] = PARTICLE_SIZE * np.ones(len(COMB_TIME_DAY))  # mm
OUT_COMB[:, 8] = ADDED_WATER * np.ones(len(COMB_TIME_DAY))  # % weight
OUT_COMB[:, 9] = TEMP * np.ones(len(COMB_TIME_DAY))  # degree C
##################################
# PLOTTING/EXPORTING BELOW
##################################

# # LOAD DATA FROM CS MODEL SIMULATION TO PLOT AGAINST EXPERIMENTAL RESULTS
# if PLOT_CSMOD == 1:
#     COL_CSTIME_SEC = 1
#     COL_CSFDEN = 9
#     COL_CSMSTRS = 15
#     COL_CSDSTRS = 16
#     COL_CSTEMP = 23
#     COL_CSVSTRN_RATE = 26
#     COL_CSMOD_IMPORT = (COL_CSTIME_SEC, COL_CSFDEN, COL_CSTEMP,
#                         COL_CSVSTRN_RATE, COL_CSMSTRS, COL_CSDSTRS)
#     CSMOD_ARR = np.genfromtxt(fname=PATH_CSMOD, delimiter=',', skip_header=2,
#                               usecols=COL_CSMOD_IMPORT, dtype=float)
#     print("CS Model data loaded")
#     CS_DUR_DAY = DUR_START + CSMOD_ARR[:, 0] / (3600 * 24)  # PLOTTING TIME
#     CS_FDEN = CSMOD_ARR[:, 1]
#     CS_TEMP = CSMOD_ARR[:, 2]
#     CS_VSTRN_RATE = CSMOD_ARR[:, 3] * (-1)
#     CS_PCON = CSMOD_ARR[:, 3]
#     CS_PDEV = CSMOD_ARR[:, 4]

##################################
FS = 14  # FONT SIZE FOR PLOTTING
##################################
# # # print color list
# for name, hex in matplotlib.colors.cnames.iteritems():
#     print(name, hex)

######################################################################
# PLOTTING DURING LOAD UP ONLY BELOW
######################################################################
FIG1 = plt.figure(figsize=(13, 10))

AX1 = FIG1.add_subplot(311)
AX1.set_title("Test: " + FOLDER_DIR, fontsize=18)

LBL_FDEN = ["Fractional Density: Loading"]
LBL_STRN = ["Volumetric Strain"]
LBL_PRES = ["Pressure: Confining"]
AX1.plot(LOAD_TIME_SEC, LOAD_FDEN, linestyle='-', linewidth=2,
         marker='s', markersize=4, color='cyan', alpha=1)
AX1.grid(True)

AX1A = AX1.twinx()
AX1A.plot(LOAD_TIME_SEC, LOAD_PCON, linestyle='-',
          linewidth=1, marker='.', markersize=8, color='r',
          alpha=1)
# AX1A.plot(LOAD_TIME_SEC, LOAD_PSOL, linestyle='-',
#           linewidth=1, marker='s', markersize=4, color='m',
#           alpha=1)
AX1A.tick_params(labelsize=FS)
AX1.tick_params(labelsize=FS, pad=10)

AX1.legend(LBL_FDEN, frameon=1, framealpha=1, loc=2, fontsize=FS)
AX1A.legend(LBL_PRES, frameon=1, framealpha=1, loc=4, fontsize=FS)
AX1.set_ylabel("Fractional Density", fontsize=FS)
AX1A.set_ylabel("Pressure (MPa)", fontsize=FS)
AX1.set_xlabel("Loading Time (sec)",
               fontsize=FS, labelpad=0)

#################################
AX2 = FIG1.add_subplot(312)

LBL_FDEN = ["Fractional Density: Loading", "Fractional Density: Creep"]
LBL_STRN_RATE = ["Strain Rate: Loading", "Strain Rate: Creep"]
# AX2.plot(COMB_TIME_DAY, COMB_FDEN, linestyle='-', linewidth=2,
#          marker='.', markersize=4, color='b', alpha=1)
AX2.plot(LOAD_TIME_DAY[:-LOAD_TRIM], LOAD_FDEN[:-LOAD_TRIM],
         linestyle='-', linewidth=2,
         marker='s', markersize=4, color='cyan', alpha=1)
AX2.plot(CREEP_TIME_DAY[CREEP_TRIM:] + CREEP_TIME_ADJ, CREEP_FDEN[CREEP_TRIM:],
         linestyle='-', linewidth=2,
         marker='.', markersize=8, color='darkblue', alpha=1)
AX2.grid(True)

AX2A = AX2.twinx()
# AX2A.semilogy(COMB_TIME_DAY, COMB_VSTRN_RATE, linestyle='-',
#               linewidth=1, marker='.', markersize=4, color='darkorange',
#               alpha=1)
AX2A.semilogy(LOAD_TIME_DAY[:-LOAD_TRIM], LOAD_VSTRN_RATE[:-LOAD_TRIM],
              linestyle='-', linewidth=2,
              marker='.', markersize=8, color='limegreen', alpha=1)
AX2A.semilogy(CREEP_TIME_DAY[CREEP_TRIM:] + CREEP_TIME_ADJ,
              CREEP_VSTRN_RATE[CREEP_TRIM:],
              linestyle='-', linewidth=2,
              marker='.', markersize=4, color='orange', alpha=1)
AX2A.tick_params(labelsize=FS)
AX2.tick_params(labelsize=FS, pad=10)

AX2.legend(LBL_FDEN, frameon=1, framealpha=0.5, loc=0, fontsize=FS)
AX2A.legend(LBL_STRN_RATE, frameon=1, framealpha=.85, loc=1, fontsize=FS)
AX2.set_ylabel("Fractional Density", fontsize=FS)
AX2A.set_ylabel(r'Strain Rate $\left( \frac{1}{sec} \right)$', fontsize=FS)
AX2.set_xlabel("Total Test Time (days)", fontsize=FS, labelpad=0)

#################################
LBL_STRN_RATE = ["Strain Rate: Loading", "Strain Rate: Creep"]
LBL_PRES = ["Confining Pressure", "Solid Pressure"]
AX3 = FIG1.add_subplot(313)
AX3.semilogy(LOAD_FDEN[:-LOAD_TRIM], LOAD_VSTRN_RATE[:-LOAD_TRIM],
             linestyle='-',
             linewidth=2, marker='.', markersize=8,
             color='limegreen', alpha=1)
AX3.semilogy(CREEP_FDEN[CREEP_TRIM:], CREEP_VSTRN_RATE[CREEP_TRIM:],
             linestyle='-',
             linewidth=2, marker='.', markersize=6,
             color='orange', alpha=1)
AX3.grid(True)

AX3A = AX3.twinx()
AX3A.plot(COMB_FDEN, COMB_PCON, linestyle='-',
          linewidth=1, marker='.', markersize=8, color='r',
          alpha=1)
# AX3A.plot(COMB_FDEN, COMB_PSOL, linestyle='-',
#           linewidth=1, marker='.', markersize=4, color='m',
#           alpha=1)

AX3A.tick_params(labelsize=FS)
AX3A.set_ylabel("Pressure (MPa)", fontsize=FS)
AX3.tick_params(labelsize=FS, pad=10)
AX3.legend(LBL_STRN_RATE, frameon=1, framealpha=.85, loc=1,
           fontsize=FS).set_zorder(2)
AX3A.legend(LBL_PRES, frameon=1, framealpha=.75, loc=3,
            fontsize=FS).set_zorder(2)
AX3.set_ylabel(r'Strain Rate $\left( \frac{1}{sec} \right)$', fontsize=FS)
AX3.set_xlabel("Fractional Density", fontsize=FS, labelpad=0)

# adjust spacing around subplots
FIG1.subplots_adjust(left=0.1, right=0.925, bottom=0.06,
                     top=0.95, wspace=0.2, hspace=0.25)
#################################

FIG1_NAME = TEST_NAME + STAGE_ID + "_PLOTS.pdf"
PATH = REPO_DIR + '/' + FOLDER_DIR + '/FINAL/'

if SAVEFIG != 0:
    FIG1.savefig(PATH + FIG1_NAME)
    print("Figure Saved As: " + FIG1_NAME)
if SAVECSV != 0:
    # SAVE RESULTS TO .CSV FILE
    OUT_LOAD_FILENAME = PATH + TEST_NAME + '_LOAD.csv'
    OUT_CREEP_FILENAME = PATH + TEST_NAME + '_CREEP.csv'
    OUT_COMB_FILENAME = PATH + TEST_NAME + '_COMB.csv'

    LINE00 = "Analysis by Brandon Lampe, performed on: " +\
             datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S').rstrip('0')
    LINE01 = "Time (sec),Time (day)," +\
             "Confining Pressure (MPa),Pore Pressure (MPa)," +\
             "Fractional Density," +\
             "Volume Strain,Volume Strain Rate (1/sec)," +\
             "Mean Particle Size (mm),Added Water (percent by weight)," +\
             "Temperature (C)"
    HEADER = '\n'.join([LINE00, LINE01])
    np.savetxt(OUT_LOAD_FILENAME, OUT_LOAD, fmt='%.6e', delimiter=',',
               newline='\n', header=HEADER, comments="")
    np.savetxt(OUT_CREEP_FILENAME, OUT_CREEP, fmt='%.6e', delimiter=',',
               newline='\n', header=HEADER, comments="")
    np.savetxt(OUT_COMB_FILENAME, OUT_COMB, fmt='%.6e', delimiter=',',
               newline='\n', header=HEADER, comments="")
    print("Saved Data As: " + OUT_LOAD_FILENAME)

    # WRITE PICKLED BINARIES
    OUT_LOAD_FILENAME_BIN = PATH + TEST_NAME + '_LOAD'
    OUT_CREEP_FILENAME_BIN = PATH + TEST_NAME + '_CREEP'
    OUT_COMB_FILENAME_BIN = PATH + TEST_NAME + '_COMB'

    np.save(OUT_LOAD_FILENAME_BIN, OUT_LOAD)
    np.save(OUT_CREEP_FILENAME_BIN, OUT_CREEP)
    np.save(OUT_COMB_FILENAME_BIN, OUT_COMB)

    # script to load the pickled binary files:
    # TEST = np.load(OUT_LOAD_FILENAME_BIN + '.npy')

if PLOT != 0:
    plt.show()
