"""
Script written to grad all experimental data and then create an output
file consisting of only the data need for parameter fitting

SAVES DATA TO: "PARM_DATA" FOLDER FOR EACH TEST
"""

import sys
import numpy as np
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import FuncFormatter
from scipy import interpolate
# from scipy import optimize
from scipy import linalg
from scipy import stats
import pickle

# relative path to module
sys.path.append(sys.path[0])
import DataAnalysisFunc as daf
REPO_DIR = os.path.dirname(sys.path[0])  # PATH TO REPOSITORY DIRECTORY

##################################
# CHOOSE ANALYSIS OPTIONS (INTEGER VALUES)
##################################
# -1 => ALLOWS FOR PLOTTING & SAVING DATA WITH NO FIT
#  0 => ALLOWS FOR PLOTTING DATA - BUT MUST HAVE A FIT TO THE DATA
#  1 => PLOT AND SAVE DATA WITH CHOSEN FIT
RUN_FIT_FDEN = 1  # SHOULD THE FIT TO FDEN BE CALCULATED

# 0 => VSTRN WILL BE FIT TO PRESSURE (LOADING)
# 1 => FIT AGAINST TIME (CREEP)
# 2 => VSTRN FIT AGAINST PRESSURE (UNLOADING)
FIT_TYPE = 1

# TO FIT A PORTION OF THE ENTIRED DOMAIN, CHOOSE ALTDOMINE_FIT_FDEN = 1
ALTDOMAIN_FIT_FDEN = 0  # FIT FDEN TO AN ALTERNATE DOMAIN THAN DEFINED BY

# 1 => Gomopertz (typically loading)
# 2 => Schnute  (typically creep)
# 3 => lineaer equation (typically unloading)
MODEL_TYPE = 3

PLOT = 1  # SHOULD THE RESULTS BE PLOTTED
SAVEFIG = 1  # SHOULD THE PLOTS BE SAVED
SAVECSV = 1  # SHOULD A .CSV OF THE RESULTS BE SAVED
PLOT_FITDATA = 0  # SHOULD RESIDUALS OF THE FIT BE PRINTED
PLOT_CSMOD = 0  # PLOT RESULTS FROM CS MODEL, MUST DEFINE FILE TO LOAD DATA
STAGE_ID = '_STAGE02'  # FOR MULTI-STAGE TESTS
ADJUST_FOR_TEMP = 0  # MODIFY FDEN WHEN MEASURED WITH ISCO (TEMP. COMPENSATE)

# IF RESULTS FROM CS MODEL ARE TO BE PLOTTED ALSO, DEFINE PATH TO DATA
PATH_CSMOD = '/Users/Lampe/GrantNo456417/Modeling/constit/' + \
             'UNM_WP_HY_175_04_OUT' + '.csv'

DUR_START = 5.001  # START PLOTTING (days), IF NO ALTDOMAIN THEN FIT ALSO
DUR_END = 10  # END PLOTTING (days), IF NO ALTDOMAIN THEN FIT ALSO
FIT_START = 0.006  # START FITTING
FIT_END = DUR_END - 0.001  # END FITTING

# COMPLETED TESTS
# FOLDER_DIR = 'UNM_WP_HY_175_01'
# FOLDER_DIR = 'UNM_WP_HY_175_03'
# FOLDER_DIR = 'UNM_WP_HY_175_04'  # ISCO FD, APPLIED TEMP CORRECTION, GOOD
# FOLDER_DIR = 'UNM_WP_HY_175_09'  # GOOD
# FOLDER_DIR = 'UNM_WP_HY_175_10'  # GOOD
# FOLDER_DIR = 'UNM_WP_HY_175_11'  # GOOD
# FOLDER_DIR = 'UNM_WP_HY_175_12'  # LOST PORE PRESSURE
# FOLDER_DIR = 'UNM_WP_HY_175_13'  # CYCLED PRESSURE DURING INITIAL LOADING
# FOLDER_DIR = 'UNM_WP_HY_175_15'  # GOOD
# FOLDER_DIR = 'UNM_WP_HY_175_16'  # GOOD
# FOLDER_DIR = 'UNM_WP_HY_90_04'
FOLDER_DIR = 'UNM_WP_HY_250_03'

# NOT COMPLETED TESTS
# FOLDER_DIR = 'UNM_WP_HY_90_02'
# FOLDER_DIR = 'UNM_WP_HY_90_03'
# FOLDER_DIR = 'UNM_WP_HY_90_08'

# interpolation spacing
INTERP_INC = 10  # SECONDS, SIZE OF INTERPOLATION INCREMENT

# TEST DETAILS
ADDED_WATER = 0.0  # PERCENT BY WEIGHT
PERCENT_UPPER = 50.773  # PERCENT FINER - VALUE ABOVE 50%
SIZE_UPPER = 3.35  # millimeter
PERCENT_LOWER = 43.149  # PERCENT FINER - VALUE BELOW 50%
SIZE_LOWER = 2.8  # MILLIMETER
SIZE_RATE = (SIZE_LOWER - SIZE_UPPER) / (PERCENT_LOWER - PERCENT_UPPER)
SIZE_MEAN = SIZE_LOWER + (50 - PERCENT_LOWER) * SIZE_RATE
MEAN_PARTICLE_SIZE = SIZE_MEAN  # millimeters
print("Average Particle Size (mm): " + str(SIZE_MEAN))

STAGE_DIR = '/' + 'PARM_DATA' + '/' + STAGE_ID[1:]

# load tests data - .csv file that has been exported directly from .xlsx
TEST_NAME = FOLDER_DIR[10:]  # + '_comp'

# DEFINE COLUMN INDEX IN .CSV FILES
COL_TIME, COL_TEMP, COL_PCON, COL_PPOR, COL_FDEN = daf.column_idx(TEST_NAME)

RHOIS = 2160.0  # ASSUMED IN-SITU DENSITY (KG/M3), FOR STRAIN MEASURE
COL_MAX = max(COL_TIME, COL_TEMP, COL_PCON, COL_PPOR, COL_FDEN) + 1
USECOLS = (np.arange(0, COL_MAX, 1))
IMPORT_FNAME = REPO_DIR + '/' + FOLDER_DIR + '/' + TEST_NAME + '.csv'
print("File Path: " + IMPORT_FNAME)

# Import .csv file and save it as an array: IMPORT_ARR
IMPORT_ARR = np.genfromtxt(fname=IMPORT_FNAME, delimiter=',', skip_header=1,
                           usecols=USECOLS, dtype=float)

# define vectors containing all rows a selected clumns, noted with "ALL"
TIME_ALL = daf.xldate_to_datetime(IMPORT_ARR[:, COL_TIME])
TIME_SHIFT = datetime.timedelta(days=DUR_START)
TIME_START = TIME_ALL[0] + TIME_SHIFT

print("Time of analysis start: " +
      TIME_START.strftime('%Y/%m/%d %H:%M:%S.%f').rstrip('0'))

DUR_DAY_ALL = daf.duration(IMPORT_ARR[:, COL_TIME])  # ALL DURATION DATA
FDEN_ALL = IMPORT_ARR[:, COL_FDEN]  # NO TIME AVERAGEING
PCON_ALL = IMPORT_ARR[:, COL_PCON] / 145.0
TEMP_ALL = IMPORT_ARR[:, COL_TEMP]
if COL_PPOR == 0:
    PPOR_ALL = np.zeros(len(PCON_ALL))
else:
    PPOR_ALL = IMPORT_ARR[:, COL_PPOR] / 145.0

# define a subset of data, identified by DUR_START and DUR_END
# if the defined duration limits are changed, so will these values
if DUR_END > DUR_DAY_ALL[-1]:
    DUR_END = DUR_DAY_ALL[-1]
    print("DUR_END has been modified, Max. Duration = " +
          str(DUR_DAY_ALL[-1]) + " days")

IDX_MAX = daf.find_nearest(DUR_DAY_ALL, DUR_END)  # IDX, MAX. DUR VALUE
IDX_MIN = daf.find_nearest(DUR_DAY_ALL, DUR_START)  # IDX, MIN. DUR VALUE
DUR_DAY = DUR_DAY_ALL[IDX_MIN:IDX_MAX]
DUR_SEC = DUR_DAY * 24 * 3600
FDEN = FDEN_ALL[IDX_MIN:IDX_MAX]
PCON = PCON_ALL[IDX_MIN:IDX_MAX]
PPOR = PPOR_ALL[IDX_MIN:IDX_MAX]
TEMP = TEMP_ALL[IDX_MIN:IDX_MAX]

# time measures needed for interpolation
# INTERP values are evenly spaced time intervals, accounts for variable sample
# spacing
DUR_DAY_LEN = (DUR_END - DUR_START)  # scalar value, days
DUR_SEC_LEN = DUR_DAY_LEN * 24 * 3600  # scalar value, SECONDS
INTERP_NUM = int(DUR_SEC_LEN / INTERP_INC) + 1  # NUM. OF INTERPOLATION inc
print("INTERP NUM: " + str(INTERP_NUM))
DUR_DAY_INTERP = np.linspace(DUR_START, DUR_END, num=INTERP_NUM, endpoint=True)
DUR_SEC_INTERP = DUR_DAY_INTERP * 24 * 3600

# functionS for interpolating the fractional density
FUNC_FDEN_INTERP = interpolate.interp1d(DUR_DAY_ALL, FDEN_ALL)
FUNC_PCON_INTERP = interpolate.interp1d(DUR_DAY_ALL, PCON_ALL)
FUNC_PPOR_INTERP = interpolate.interp1d(DUR_DAY_ALL, PPOR_ALL)
FUNC_TEMP_INTERP = interpolate.interp1d(DUR_DAY_ALL, TEMP_ALL)

# vectors OF interpolated values
FDEN_INTERP = FUNC_FDEN_INTERP(DUR_DAY_INTERP)
PCON_INTERP = FUNC_PCON_INTERP(DUR_DAY_INTERP)
PPOR_INTERP = FUNC_PPOR_INTERP(DUR_DAY_INTERP)
TEMP_INTERP = FUNC_TEMP_INTERP(DUR_DAY_INTERP)

# CALCULATE ALTERNATE FITTING DOMAIN IF
if ALTDOMAIN_FIT_FDEN == 1:
    FIT_DAY_LEN = (FIT_END - FIT_START)
    FIT_SEC_LEN = FIT_DAY_LEN * 24 * 3600
    FIT_INTERP_NUM = int(FIT_SEC_LEN / INTERP_INC) + 1
    FIT_DUR_DAY_INTERP = np.linspace(FIT_START, FIT_END, num=FIT_INTERP_NUM,
                                     endpoint=True)
    FIT_FDEN_INTERP = FUNC_FDEN_INTERP(FIT_DUR_DAY_INTERP)
    FIT_PCON_INTERP = FUNC_PCON_INTERP(FIT_DUR_DAY_INTERP)

if ADJUST_FOR_TEMP == 1:  # MODIFICATION TO FDEN MEASUREMENT FOR DELTA TEMP.
    MOD_FACT = 0.0013  # 1/DEGREE C
    DELTA_TEMP = np.gradient(TEMP_INTERP)
    # plt.plot(DUR_DAY_INTERP, FDEN_INTERP, 'g-', label='Original')
    FDEN_INTERP = FDEN_INTERP + np.cumsum(DELTA_TEMP) * MOD_FACT
    if ALTDOMAIN_FIT_FDEN == 1:
        FIT_TEMP_INTERP = FUNC_TEMP_INTERP(FIT_DUR_DAY_INTERP)
        FIT_DELTA_TEMP = np.gradient(FIT_TEMP_INTERP)
        FIT_FDEN_INTERP = FIT_FDEN_INTERP + \
            np.cumsum(FIT_DELTA_TEMP) * MOD_FACT
    print("FDEN was modified for changing temp. by: " +
          str(MOD_FACT) + " (1/DEGREE C)")
    # plt.plot(DUR_DAY_INTERP, FDEN_INTERP, 'r-', label='Adjusted')
    # plt.grid()
    # plt.legend(loc=0)
    # plt.show()

PCON_AVG_PSI = np.mean(PCON_INTERP) * 145
PCON_AVG_MPA = np.mean(PCON_INTERP)
PPOR_AVG_PSI = np.mean(PPOR_INTERP) * 145
PPOR_AVG_MPA = np.mean(PPOR_INTERP)
TEMP_AVG_C = np.mean(TEMP_INTERP)

if FIT_TYPE == 1:  # CREEP
    TEST_SPEC = {}
    TEST_SPEC["percent added water by weight"] = ADDED_WATER
    TEST_SPEC["mean particle size"] = MEAN_PARTICLE_SIZE
    TEST_SPEC["average temperature"] = TEMP_AVG_C
    TEST_SPEC["average confining pressure"] = PCON_AVG_MPA
    TEST_SPEC["average pore pressure"] = PPOR_AVG_MPA

# calculated volume strain rate by fitting model to fractional density
FDEN0 = FDEN_INTERP[0]  # INITIAL FRACTIONAL DENSITY

# CALCULATE VOLUME STRAIN AND VOLUME STRAIN RATE
VSTRN = -np.log(FDEN0 / FDEN)  # POSITIVE IN COMPRESSION
VSTRN_INTERP = -np.log(FDEN0 / FDEN_INTERP)  # POSITIVE IN COMPRESSION
DELTA_VSTRN = np.gradient(VSTRN)
DELTA_VSTRN_INTERP = np.gradient(VSTRN_INTERP)
DELTA_SEC = np.gradient(DUR_SEC)
DELTA_SEC_INTERP = np.gradient(DUR_SEC_INTERP)
VSTRN_RATE = DELTA_VSTRN / DELTA_SEC
VSTRN_RATE_INTERP = DELTA_VSTRN_INTERP / DELTA_SEC_INTERP


# CALCULATE COMPRESIBILITIES
DELTA_PCON_INTERP = np.gradient(PCON_INTERP)
DENISTY_INTERP = RHOIS * FDEN_INTERP
DELTA_DENSITY_INTERP = np.gradient(DENISTY_INTERP)
COMP_DRAINED_INTERP = DENISTY_INTERP * DELTA_PCON_INTERP / DELTA_DENSITY_INTERP

if RUN_FIT_FDEN == 1:
    if FIT_TYPE == 1:  # fit fden agains time, creep
        if ALTDOMAIN_FIT_FDEN == 1:
            FIT_DOMAIN = FIT_DUR_DAY_INTERP
            FIT_RANGE = FIT_FDEN_INTERP
        else:
            FIT_DOMAIN = DUR_DAY_INTERP
            FIT_RANGE = FDEN_INTERP
        FDEN_FIT_INTERP, MODEL, DES_STR = daf.fit_fden(
            fden_interp=FIT_RANGE,
            dur_day_interp=FIT_DOMAIN,
            which_mod=MODEL_TYPE,
            whole_domain=DUR_DAY_INTERP)
    elif FIT_TYPE == 0:  # fit fden against pressure, load-up
        if ALTDOMAIN_FIT_FDEN == 1:
            FIT_DOMAIN = FIT_PCON_INTERP
            FIT_RANGE = FIT_FDEN_INTERP
        else:
            FIT_DOMAIN = PCON_INTERP
            FIT_RANGE = FDEN_INTERP
        FDEN_FIT_INTERP, MODEL, DES_STR = daf.fit_fden(
            fden_interp=FIT_RANGE,
            dur_day_interp=FIT_DOMAIN,
            which_mod=MODEL_TYPE,
            whole_domain=PCON_INTERP)
    elif FIT_TYPE == 2:  # fit fden against pressure, UNLOADING
        if ALTDOMAIN_FIT_FDEN == 1:
            FIT_DOMAIN = FIT_PCON_INTERP
            FIT_RANGE = FIT_FDEN_INTERP
        else:
            FIT_DOMAIN = PCON_INTERP
            FIT_RANGE = FDEN_INTERP
        FDEN_FIT_INTERP, MODEL, DES_STR = daf.fit_fden(
            fden_interp=FIT_RANGE,
            dur_day_interp=FIT_DOMAIN,
            which_mod=MODEL_TYPE,
            whole_domain=PCON_INTERP)
    # print(MODEL.best_values)
    print(MODEL.fit_report())
    # print(MODEL.ci_out)

    FIT_REPORT = MODEL.fit_report()
    FIT_CI = MODEL.ci_out
    # FIT_RESID = MODEL.residual
    FIT_RESID = FDEN_FIT_INTERP - FDEN_INTERP

    # CALCULATED THE SCALED P-NORM (2)
    FIT_RESID_NORM = linalg.norm(np.nan_to_num(FIT_RESID)) /\
        len(np.nan_to_num(FIT_RESID))**(1. / 2)
    FDEN_MEAN = np.mean(FDEN_INTERP)  # MEAN OF THE DATA
    DATA_SSE = np.sum((FDEN_INTERP - FDEN_MEAN)**2)  # VARIANCE OF THE DATA
    RESID_SSE = np.sum((np.nan_to_num(FIT_RESID))**2)
    RSQUARED = 1 - RESID_SSE / DATA_SSE
    PRINT_RSQUARED = '{:f}'.format(RSQUARED)
    PRINT_NORM = '{:e}'.format(FIT_RESID_NORM)
    print("Scaled Error Norm of Fit: " + str(PRINT_NORM))
    print("R SQUARED of Fit: " + str(PRINT_RSQUARED))

    if PLOT_FITDATA == 1:
        if FIT_TYPE == 1:  # data was fit agains time (creep)
            FIG0, FITPLOT = plt.subplots(2, figsize=(13, 8), sharex=True)
            FITPLOT[0].set_title("Test: " + FOLDER_DIR, fontsize=18)
            FITPLOT[0].plot(DUR_DAY_INTERP, FIT_RESID, 'b.-')
            FITPLOT[0].grid()
            FITPLOT[0].set_ylabel("Residual (Fractional Density)")

            LBL_FIT = ["Initial Guess", "Best Fit", "Interpolated Data"]
            FITPLOT[1].plot(FIT_DOMAIN, MODEL.init_fit, 'g--')
            FITPLOT[1].plot(FIT_DOMAIN, MODEL.best_fit, 'b.-')
            FITPLOT[1].plot(FIT_DOMAIN, FIT_RANGE, 'r.-')
            FITPLOT[1].grid()
            FITPLOT[1].set_ylabel("Fractional Density")
            FITPLOT[1].set_xlabel("Test Duration (day)")
            FITPLOT[1].legend(LBL_FIT, loc=0)
        elif FIT_TYPE != 1:  # data was fit against pressure (load or unload)
            FIG0, FITPLOT = plt.subplots(2, figsize=(13, 8), sharex=True)
            FITPLOT[0].set_title("Test: " + FOLDER_DIR +
                                 " (During Pressure Change)", fontsize=18)
            FITPLOT[0].plot(FIT_DOMAIN, FIT_RESID[0:len(FIT_DOMAIN)], 'b.-')
            FITPLOT[0].grid()
            FITPLOT[0].set_ylabel("Residual (Fractional Density)")

            LBL_FIT = ["Initial Guess", "Best Fit", "Interpolated Data"]
            FITPLOT[1].plot(FIT_DOMAIN, MODEL.init_fit, 'g--')
            FITPLOT[1].plot(FIT_DOMAIN, MODEL.best_fit, 'b.-')
            FITPLOT[1].plot(FIT_DOMAIN, FIT_RANGE, 'r.-')
            FITPLOT[1].grid()
            FITPLOT[1].set_ylabel("Fractional Density")
            FITPLOT[1].set_xlabel("Confining Pressure (MPa)")
            FITPLOT[1].legend(LBL_FIT, loc=0)
        if PLOT == 0:
            plt.show()

    VSTRN_FIT_INTERP = -np.log(FDEN0 / FDEN_FIT_INTERP)
    DELTA_VSTRN_FIT_INTERP = np.gradient(VSTRN_FIT_INTERP)
    VSTRN_RATE_FIT_INTERP = DELTA_VSTRN_FIT_INTERP / DELTA_SEC_INTERP
    DELTA_PCON_INTERP = np.gradient(PCON_INTERP)
    DENISTY_FIT_INTERP = RHOIS * FDEN_FIT_INTERP
    DELTA_DENSITY_FIT_INTERP = np.gradient(DENISTY_FIT_INTERP)
    BULK_DRAINED_FIT_INTERP = DENISTY_FIT_INTERP * (DELTA_PCON_INTERP /
                                                    DELTA_DENSITY_FIT_INTERP)
    COMP_DRAINED_FIT_INTERP = BULK_DRAINED_FIT_INTERP**(-1)

else:  # returns null vectors for fits
    FDEN_FIT_INTERP = np.zeros(len(DUR_SEC_INTERP))
    VSTRN_FIT_INTERP = np.zeros(len(DUR_SEC_INTERP))
    VSTRN_RATE_FIT_INTERP = np.zeros(len(DUR_SEC_INTERP))
    COMP_DRAINED_FIT_INTERP = np.zeros(len(DUR_SEC_INTERP))

PTER_INTERP = PCON_INTERP - PPOR_INTERP  # Terzahi pressure
PSOL_INTERP = (PCON_INTERP - PPOR_INTERP * (1 - FDEN_INTERP)) / FDEN_INTERP
LEN_SEC_INTERP = DUR_SEC_INTERP - DUR_SEC_INTERP[0]
LEN_DAY_INTERP = DUR_DAY_INTERP - DUR_DAY_INTERP[0]

OUT_INTERP_DATA = np.zeros((len(DUR_SEC_INTERP), 13))
OUT_INTERP_DATA[:, 0] = DUR_SEC_INTERP
OUT_INTERP_DATA[:, 1] = DUR_DAY_INTERP
OUT_INTERP_DATA[:, 2] = LEN_SEC_INTERP
OUT_INTERP_DATA[:, 3] = LEN_DAY_INTERP
OUT_INTERP_DATA[:, 4] = FDEN_INTERP
OUT_INTERP_DATA[:, 5] = FDEN_FIT_INTERP
OUT_INTERP_DATA[:, 6] = VSTRN_FIT_INTERP
OUT_INTERP_DATA[:, 7] = VSTRN_RATE_FIT_INTERP
OUT_INTERP_DATA[:, 8] = PCON_INTERP
OUT_INTERP_DATA[:, 9] = PPOR_INTERP
OUT_INTERP_DATA[:, 10] = PTER_INTERP
OUT_INTERP_DATA[:, 11] = PSOL_INTERP
OUT_INTERP_DATA[:, 12] = TEMP_INTERP

print("Initial Strain Rate: " + str(VSTRN_RATE_FIT_INTERP[0]))
print("Final Strain Rate: " + str(VSTRN_RATE_FIT_INTERP[-1]))
##################################
# PLOTTING/EXPORTING BELOW
##################################

# LOAD DATA FROM CS MODEL SIMULATION TO PLOT AGAINST EXPERIMENTAL RESULTS
if PLOT_CSMOD == 1:
    COL_CSTIME_SEC = 1
    COL_CSFDEN = 9
    COL_CSMSTRS = 15
    COL_CSDSTRS = 16
    COL_CSTEMP = 23
    COL_CSVSTRN_RATE = 26
    COL_CSMOD_IMPORT = (COL_CSTIME_SEC, COL_CSFDEN, COL_CSTEMP,
                        COL_CSVSTRN_RATE, COL_CSMSTRS, COL_CSDSTRS)
    CSMOD_ARR = np.genfromtxt(fname=PATH_CSMOD, delimiter=',', skip_header=2,
                              usecols=COL_CSMOD_IMPORT, dtype=float)
    print("CS Model data loaded")
    CS_DUR_DAY = DUR_START + CSMOD_ARR[:, 0] / (3600 * 24)  # PLOTTING TIME
    CS_FDEN = CSMOD_ARR[:, 1]
    CS_TEMP = CSMOD_ARR[:, 2]
    CS_VSTRN_RATE = CSMOD_ARR[:, 3] * (-1)
    CS_PCON = CSMOD_ARR[:, 3]
    CS_PDEV = CSMOD_ARR[:, 4]

##################################
FS = 14  # FONT SIZE FOR PLOTTING
NUM_SUBPLOT = 3
# ######################################################################
# PLOTTING FOR CREEP ONLY
# ######################################################################
if FIT_TYPE == 1:
    FIG1, AXARR = plt.subplots(NUM_SUBPLOT, figsize=(13, 10), sharex=True)
    AXARR[0].set_title("Test: " + FOLDER_DIR,
                       fontsize=18)

    LBL_FDEN = ["Measured", "Interpolated", "Fit", "CS Model"]
    AXARR[0].plot(DUR_DAY, FDEN, linestyle='-', linewidth=1,
                  marker='.', markersize=4, color='r', alpha=1)
    AXARR[0].plot(DUR_DAY_INTERP, FDEN_INTERP, linestyle='-', linewidth=1,
                  marker='.', markersize=4, color='y', alpha=1)
    if RUN_FIT_FDEN == 1:
        AXARR[0].plot(DUR_DAY_INTERP, FDEN_FIT_INTERP, linestyle='-',
                      linewidth=4, marker=None, markersize=1, color='b',
                      alpha=.5)
    if PLOT_CSMOD == 1:
        AXARR[0].plot(CS_DUR_DAY, CS_FDEN, linestyle='-',
                      linewidth=2, marker=None, markersize=1, color='g',
                      alpha=1)
    AXARR[0].grid(True)
    AXARR[0].set_ylabel("Fractional Density", fontsize=FS)
    YMIN, YMAX = AXARR[0].get_ylim()
    YMIN = -np.log(FDEN0 / YMIN)
    YMAX = -np.log(FDEN0 / YMAX)
    AX2A = AXARR[0].twinx()
    AX2A.plot(DUR_DAY_INTERP, VSTRN_INTERP, 'r-', lw=3)
    AX2A.yaxis.set_minor_formatter(FormatStrFormatter("%.2f"))
    AX2A.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    AX2A.set_ylabel("Approx. Volumetric Strain", fontsize=FS)
    AX2A.tick_params(labelsize=FS)
    AX2A.set_ylim(ymin=YMIN, ymax=YMAX)
    AX2A.lines[0].remove()
    AXARR[0].legend(LBL_FDEN, frameon=1, framealpha=1, loc=0, fontsize=FS)
    AXARR[0].tick_params(labelsize=FS)
    AXARR[0].tick_params(labelsize=FS, pad=10)
    #################################
    LBL_STRNRATE = ["Interpolated", "Measured", "Fit", "CS Model"]
    LBL_INTERVAL = ["Sampling"]

    if MODEL_TYPE != 3:
        AXARR[1].semilogy(DUR_DAY_INTERP, VSTRN_RATE_INTERP, linestyle='-',
                                          linewidth=1, marker='.', markersize=4,
                                          color='y', alpha=1)
        AXARR[1].semilogy(DUR_DAY, VSTRN_RATE, linestyle='-',
                          linewidth=1, marker='.', markersize=4,
                          color='r', alpha=1)
        if RUN_FIT_FDEN == 1:
            AXARR[1].semilogy(DUR_DAY_INTERP, VSTRN_RATE_FIT_INTERP, linestyle='-',
                              linewidth=4, marker='None', markersize=4,
                              color='b', alpha=1)
        if PLOT_CSMOD == 1:
            AXARR[1].semilogy(CS_DUR_DAY, CS_VSTRN_RATE, linestyle='-',
                              linewidth=2, marker='None', markersize=4,
                              color='G', alpha=1)

    AXARR[1].grid(True)
    AXARR[1].set_ylabel(r'Strain Rate (sec$^{-1}$)', fontsize=FS)

    AX2B = AXARR[1].twinx()
    AX2B.semilogy(DUR_DAY, DELTA_SEC, linestyle='-',
                  linewidth=1, marker='.', markersize=4,
                  color='k', alpha=1)
    AX2B.set_ylabel("Seconds Per Sample", fontsize=FS)
    AX2B.tick_params(labelsize=FS)
    AXARR[1].legend(LBL_STRNRATE, frameon=1, framealpha=0.75, loc=1,
                    fontsize=FS)
    AX2B.legend(LBL_INTERVAL, frameon=1, framealpha=0.85, loc=4, fontsize=FS)

    AXARR[1].tick_params(labelsize=FS)
    AXARR[1].tick_params(labelsize=FS, pad=10)
    #################################
    LBL_STRS = ["Confining", "Pore", "Difference",
                "Solid"]
    LBL_TEMP = ["Temperature"]
    AXARR[2].plot(DUR_DAY_INTERP, PCON_INTERP, linestyle='-',
                  linewidth=1, marker='.', markersize=4,
                  color='b', alpha=1)
    AXARR[2].plot(DUR_DAY_INTERP, PPOR_INTERP, linestyle='-',
                  linewidth=1, marker='.', markersize=4,
                  color='g', alpha=1)
    AXARR[2].plot(DUR_DAY_INTERP, PTER_INTERP, linestyle='-',
                  linewidth=1, marker='.', markersize=4,
                  color='r', alpha=1)
    # AXARR[2].plot(DUR_DAY_INTERP, PSOL_INTERP, linestyle='-',
    #               linewidth=1, marker='.', markersize=4,
    #               color='c', alpha=1)
    # AXARR[2].yaxis.set_major_formatter(FuncFormatter(
    #     lambda x, p: format(int(x), ',')))
    AXARR[2].grid(True)
    AXARR[2].set_ylabel('Pressure (MPa)', fontsize=FS)

    AX2C = AXARR[2].twinx()
    AX2C.plot(DUR_DAY_INTERP, TEMP_INTERP, linestyle='-',
              linewidth=1, marker='None', markersize=4,
              color='k', alpha=0.5)
    AX2C.set_ylabel(r'Temperature ($^o$C)', fontsize=FS)
    AX2C.tick_params(labelsize=FS)

    AXARR[2].legend(LBL_STRS, frameon=1, framealpha=.85, loc=4, fontsize=FS)
    AX2C.legend(LBL_TEMP, frameon=1, framealpha=0.85, loc=3, fontsize=FS)

    AXARR[2].tick_params(labelsize=FS)
    AXARR[2].tick_params(labelsize=FS, pad=10)
    #################################
    LOWEST_CHART = NUM_SUBPLOT - 1
    AXARR[LOWEST_CHART].set_xlabel("Test Duration [days]", fontsize=FS,
                                   labelpad=10)
    # MAJORFORMATTER = FormatStrFormatter('%2.3f')
    # AXARR[LOWEST_CHART].xaxis.set_major_formatter(MAJORFORMATTER)
    AXARR[LOWEST_CHART].tick_params(labelsize=FS, pad=10)
# ######################################################################
# PLOTTING DURING LOAD UP ONLY BELOW
# ######################################################################
if FIT_TYPE == 0:  # for loading or unloading
    FIG1 = plt.figure(figsize=(13, 10))

    AX1 = FIG1.add_subplot(311)
    AX1.set_title("Test: " + FOLDER_DIR, fontsize=18)
    LBL_FDEN = ["Fractional Density: Measure", "Fractional Denisty: Fit"]
    LBL_PRES = ["Confining Pressure"]
    AX1.plot(DUR_DAY_INTERP, FDEN_INTERP, linestyle='-', linewidth=1,
             marker='.', markersize=4, color='y', alpha=1)
    if RUN_FIT_FDEN == 1:
        AX1.plot(DUR_DAY_INTERP, FDEN_FIT_INTERP, linestyle='-',
                 linewidth=2, marker='o', markersize=1, color='b',
                 alpha=.5)
    AX1.grid(True)

    AX1A = AX1.twinx()
    AX1A.plot(DUR_DAY_INTERP, PCON_INTERP, linestyle='-',
              linewidth=1, marker='s', markersize=4, color='r',
              alpha=1)
    AX1A.set_ylabel("Pressure (MPa)", fontsize=FS)
    AX1A.tick_params(labelsize=FS)

    AX1.tick_params(labelsize=FS)
    AX1.tick_params(labelsize=FS, pad=10)

    AX1.legend(LBL_FDEN, frameon=1, framealpha=1, loc=2, fontsize=FS)
    AX1A.legend(LBL_PRES, frameon=1, framealpha=1, loc=4, fontsize=FS)
    AX1.set_ylabel("Fractional Density", fontsize=FS)
    AX1.set_xlabel("Duration (days)", fontsize=FS, labelpad=0)

    #################################
    LBL_STRN = ["Fit", "Measure"]
    # LBL_INTERVAL = ["Sampling"]
    AX2 = FIG1.add_subplot(312)
    AX2.plot(PCON_INTERP, VSTRN_FIT_INTERP, linestyle='-',
             linewidth=2, marker='o', markersize=1,
             color='b', alpha=0.5)
    AX2.plot(PCON_INTERP, VSTRN_INTERP, linestyle='-',
             linewidth=1, marker='.', markersize=4,
             color='y', alpha=1)
    AX2.grid(True)
    AX2.set_ylabel('Volume Strain', fontsize=FS)
    AX2.set_xlabel("Confining Pressure (MPa)", fontsize=FS, labelpad=0)
    AX2.legend(LBL_STRN, frameon=1, framealpha=0.75, loc=4, fontsize=FS)
    # AX2B.legend(LBL_INTERVAL, frameon=1, framealpha=0.85, loc=4, fontsize=FS)

    AX2.tick_params(labelsize=FS)
    AX2.tick_params(labelsize=FS, pad=10)
    AX2.tick_params(labelsize=FS, pad=10)
    #################################
    LBL_STRN_RATE = ["Volumetric Strain Rate"]
    LBL_COMP = ["Drained"]

    AX3 = FIG1.add_subplot(313)
    AX3.semilogy(FDEN_FIT_INTERP, VSTRN_RATE_FIT_INTERP, linestyle='-',
                 linewidth=2, marker='.', markersize=4,
                 color='m', alpha=0.75)

    # AX3A = AX3.twinx()
    # AX3A.semilogy(FDEN_FIT_INTERP, BULK_DRAINED_FIT_INTERP, linestyle='-',
    #               linewidth=2, marker='s', markersize=4,
    #               color='c', alpha=0.75)
    AX3.grid(True)
    AX3.set_ylabel(r'Strain Rate $\left( \frac{1}{sec} \right)$', fontsize=FS)
    # AX3A.set_ylabel(r'Bulk Modulus (MPa)',
    #                 fontsize=FS)
    # AX3A.tick_params(labelsize=FS)

    AX3.legend(LBL_STRN_RATE, frameon=1, framealpha=.85, loc=0, fontsize=FS)
    # AX3A.legend(LBL_COMP, frameon=1, framealpha=0.85, loc=4, fontsize=FS)

    AX3.tick_params(labelsize=FS)
    AX3.tick_params(labelsize=FS, pad=10)
    AX3.set_xlabel("Fractional Density", fontsize=FS, labelpad=0)
    AX3.tick_params(labelsize=FS, pad=10)

    FIG1.subplots_adjust(left=0.1, right=0.925, bottom=0.06, top=0.95,
                         wspace=0.2, hspace=0.3)
# ######################################################################
# PLOTTING DURING unloading ONLY BELOW
# ######################################################################
if FIT_TYPE == 2:  # for unloading
    FIG1 = plt.figure(figsize=(13, 10))

    AX1 = FIG1.add_subplot(311)
    AX1.set_title("Test: " + FOLDER_DIR  + " (Unloading)", fontsize=18)
    LBL_FDEN = ["Fractional Density: Measure", "Fractional Denisty: Fit"]
    LBL_PRES = ["Confining Pressure"]
    AX1.plot(DUR_DAY_INTERP, FDEN_INTERP, linestyle='-', linewidth=1,
             marker='.', markersize=4, color='y', alpha=1)
    if RUN_FIT_FDEN == 1:
        AX1.plot(DUR_DAY_INTERP, FDEN_FIT_INTERP, linestyle='-',
                 linewidth=2, marker='o', markersize=1, color='b',
                 alpha=.5)
    AX1.grid(True)

    AX1A = AX1.twinx()
    AX1A.plot(DUR_DAY_INTERP, PCON_INTERP, linestyle='-',
              linewidth=1, marker='s', markersize=4, color='r',
              alpha=1)
    AX1A.set_ylabel("Pressure (MPa)", fontsize=FS)
    AX1A.tick_params(labelsize=FS)

    AX1.tick_params(labelsize=FS, pad=10)

    AX1.legend(LBL_FDEN, frameon=1, framealpha=1, loc=1, fontsize=FS)
    AX1A.legend(LBL_PRES, frameon=1, framealpha=1, loc=3, fontsize=FS)
    AX1.set_ylabel("Fractional Density", fontsize=FS)
    AX1.set_xlabel("Duration (days)", fontsize=FS, labelpad=0)

    #################################
    LBL_BULK = ["Bulk Modulus: Drained"]
    LBL_FDEN = ["Fractional Density: Fit"]
    AX2 = FIG1.add_subplot(312)
    AX2.plot(PCON_INTERP, BULK_DRAINED_FIT_INTERP, linestyle='-',
             linewidth=2, marker='o', markersize=1,
             color='darkorange', alpha=1)
    AX2A = AX2.twinx()
    AX2A.plot(PCON_INTERP, FDEN_FIT_INTERP, linestyle='-',
              linewidth=2, marker='.', markersize=4,
              color='b', alpha=0.5)
    AX2.grid(True)
    AX2.set_ylabel('Bulk Modulus (MPa)', fontsize=FS)
    AX2A.set_ylabel('Fractional Density', fontsize=FS)
    AX2.set_xlabel("Confining Pressure (MPa)", fontsize=FS, labelpad=0)
    AX2.legend(LBL_BULK, frameon=1, framealpha=0.75, loc=2, fontsize=FS)
    AX2A.legend(LBL_FDEN, frameon=1, framealpha=0.85, loc=4, fontsize=FS)

    AX2.tick_params(labelsize=FS, pad=10)
    #################################
    LBL_BULK = ["Bulk Modulus: Drained"]

    AX3 = FIG1.add_subplot(313)
    AX3.plot(FDEN_FIT_INTERP, BULK_DRAINED_FIT_INTERP, linestyle='-',
             linewidth=2, marker='.', markersize=4,
             color='darkorange', alpha=1)

    # AX3A = AX3.twinx()
    # AX3A.plot(FDEN_FIT_INTERP, BULK_DRAINED_FIT_INTERP, linestyle='-',
              # linewidth=2, marker='s', markersize=4,
              # color='c', alpha=0.75)
    # Y_FMT = FormatStrFormatter('%2.1e')
    # AX3.yaxis.set_major_formatter(Y_FMT)
    AX3.grid(True)
    AX3.set_ylabel("Bulk Modulus (MPa)", fontsize=FS)
    # AX3A.set_ylabel(r'Bulk Modulus (MPa)',
                    # fontsize=FS)

    AX3.legend(LBL_BULK, frameon=1, framealpha=.85, loc=2, fontsize=FS)
    AX3.set_xlabel("Fractional Density", fontsize=FS, labelpad=0)
    AX3.tick_params(labelsize=FS, pad=10)

    # adjust spacing around subplots
    FIG1.subplots_adjust(left=0.1, right=0.925, bottom=0.06, top=0.95,
                         wspace=0.2, hspace=0.3)
#################################
# DEFINE WHAT/WHERE STUFF IS SAVED
#################################
FIG0_NAME = TEST_NAME + STAGE_ID + "_PLOTS_RESID.pdf"
FIG1_NAME = TEST_NAME + STAGE_ID + "_PLOTS.pdf"
PATH = REPO_DIR + '/' + FOLDER_DIR + STAGE_DIR + '/'

if SAVEFIG != 0:
    if PLOT_FITDATA == 1:
        FIG0.savefig(PATH + FIG0_NAME, bbox='tight')
    print(PATH + FIG1_NAME)
    FIG1.savefig(PATH + FIG1_NAME)
    print("Figure Saved As: " + FIG1_NAME)
if SAVECSV != 0:
    # SAVE RESULTS TO .CSV FILE
    OUT_FILENAME = PATH + TEST_NAME + '_OUT.csv'
    OUT_FILENAME_REPORT = PATH + TEST_NAME + '_FITREPORT.csv'
    OUT_FILENAME_PARM = PATH + TEST_NAME + '_PARM.bin'
    OUT_FILENAME_SPEC = PATH + TEST_NAME + '_SPEC.bin'
    # OUT_FILENAME = PATH + ADD_DIR + TEST_NAME + STAGE_ID + FIT_ID + '_OUT.csv'
    # OUT_FILENAME_REPORT = PATH + ADD_DIR + TEST_NAME + STAGE_ID + FIT_ID +\
    #     '_FITREPORT.csv'
    # OUT_FILENAME_PARM = PATH + ADD_DIR + TEST_NAME + STAGE_ID + FIT_ID +\
    #     '_PARM.bin'
    # OUT_FILENAME_SPEC = PATH + ADD_DIR + TEST_NAME + STAGE_ID + FIT_ID +\
    #     '_SPEC.bin'
    # HEADER = "Interpolated Data For Test: " + str(TEST_NAME) + "/n"
    LINE00 = "Analysis by Brandon Lampe, performed on: " +\
             datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S').rstrip('0')
    LINE01 = "Experimental results below begin at: " +\
             TIME_START.strftime('%Y/%m/%d %H:%M:%S').rstrip('0')

    LINE02 = "Duration (sec),Duration (day)," +\
             "Elapsed Time (sec),Elapsed Time (day)," +\
             "Interpolated Fractional Density,Fit to Fractional Density," +\
             "Fit to Volume Strain,Fit to Volume Strain Rate (1/sec)," +\
             "Confining Pressure (MPa),Pore Pressure (MPa)," +\
             "Terzaghi Pressure (MPa),Solid Pressure (MPa)," +\
             "Temperature (C))"
    HEADER = '\n'.join([LINE00, LINE01, LINE02])
    np.savetxt(OUT_FILENAME, OUT_INTERP_DATA, fmt='%.6e', delimiter=',',
               newline='\n', header=HEADER, comments="")
    print("Saved Data As: " + OUT_FILENAME)

    # WRITE FIT REPORT
    if RUN_FIT_FDEN == 1:
        BLANK = ''
        LINE10 = LINE00
        LINE11 = 'The following model was used to fit the fractional density:'
        LINE12 = DES_STR
        LINE13 = 'Scaled Error Norm: ' + str(PRINT_NORM)
        LINE14 = 'Fit Report (from LMFIT):'
        LINE15 = FIT_REPORT
        LINE16 = 'Model was fit to the following domain (x) -> Duration (days)'
        if ALTDOMAIN_FIT_FDEN == 1:
            LINE17 = 'Start, ' + str(FIT_START)
            LINE18 = 'End, ' + str(FIT_END)
        else:
            LINE17 = 'Start, ' + str(DUR_START)
            LINE18 = 'End, ' + str(DUR_END)
        LINE19 = 'Raw data was interpolated every ' + str(INTERP_INC) + ' sec.'

        if FIT_TYPE == 2:  # UNLOADING TO FIND BULK MODULUS
            FDEN_AVG = np.mean(FDEN_FIT_INTERP)
            BULK_MOD_AVG = np.mean(BULK_DRAINED_FIT_INTERP)
            LINE20 = 'Average Confining Pressure (MPa): ' + str(PCON_AVG_MPA)
            LINE21 = 'Average Pore Pressure (MPa): ' + str(PPOR_AVG_MPA)
            LINE22 = 'Average Fractional Density: ' + str(FDEN_AVG)
            LINE23 = 'Average Temperature (C): ' + str(TEMP_AVG_C)
            LINE24 = 'Average Bulk Modulus (MPa): ' + str(BULK_MOD_AVG)
            FIT_REPORT = '\n'.join([LINE10, BLANK, LINE11, LINE12, BLANK,
                                    LINE13,
                                    BLANK, LINE14, LINE15, LINE16, LINE17,
                                    LINE18, BLANK, LINE19, BLANK, LINE20,
                                    LINE21, LINE22, LINE23, LINE24, BLANK])
            print(LINE24)
        else:
            FIT_REPORT = '\n'.join([LINE10, BLANK, LINE11, LINE12, BLANK,
                                    LINE13,
                                    BLANK, LINE14, LINE15, LINE16, LINE17,
                                    LINE18, BLANK, LINE19, BLANK])
        OUT = open(OUT_FILENAME_REPORT, 'w')
        OUT.write(FIT_REPORT)

        # WRITE PARAMETER VALUES ONLY, for input into python later
        with open(OUT_FILENAME_PARM, 'wb') as handle:
            pickle.dump(MODEL.best_values, handle)

        if FIT_TYPE == 1:
            with open(OUT_FILENAME_SPEC, 'wb') as handle:
                pickle.dump(TEST_SPEC, handle)

        # # read parameter values from pickled file
        # with open(OUT_FILENAME_PARM, 'rb') as handle:
        #     TEST_READ = pickle.loads(handle.read())

        print("Saved Fit Report As: " + OUT_FILENAME_REPORT)
        print("Saved Parameters As: " + OUT_FILENAME_PARM)
        print("Saved Test Specification As: " + OUT_FILENAME_SPEC)
if PLOT != 0:
    plt.show()
