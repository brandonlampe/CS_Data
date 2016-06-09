import numpy as np
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import FuncFormatter
from scipy import interpolate
# from scipy import optimize
from scipy import linalg
# import lmfit

# relative path to module
sys.path.append(sys.path[0])
import DataAnalysisFunc as daf
REPO_DIR = os.path.dirname(sys.path[0])  # PATH TO REPOSITORY DIRECTORY

##################################
# CHOOSE ANALYSIS OPTIONS
##################################
PLOT = 0
SAVEFIG = 0
SAVECSV = 1
PLOT_RESID = 1
PLOT_CSMOD = 1  # PLOT RESULTS FROM CS MODEL, MUST DEFINE FILE TO LOAD DATA
PATH_CSMOD = '/Users/Lampe/GrantNo456417/Modeling/constit/UNM_WP_HY_175_09_OUT.csv'

DUR_START = 0.006  # START PLOTTING
DUR_END = 0.95  # END PLOTTING
INTERP_INC = 10  # SECONDS, SIZE OF INTERPOLATION INCREMENT

# TESTNAME = 'UNM_WP_HY_90_02'
# TESTNAME = 'UNM_WP_HY_90_03'
# TESTNAME = 'UNM_WP_HY_90_04'
# TESTNAME = 'UNM_WP_HY_90_08'
# TESTNAME = 'UNM_WP_HY_175_01'
# TESTNAME = 'UNM_WP_HY_175_03'
# TESTNAME = 'UNM_WP_HY_175_04'
FOLDER_DIR = 'UNM_WP_HY_175_09'

# load tests data - .csv file that has been exported directly from .xlsx
TEST_NAME = FOLDER_DIR[-6:]

# DEFINE COLUMNS FOR:
# 'UNM_WP_HY_175_09'
COL_TIME = 1
COL_TEMP = 8
COL_PCON = 2
COL_PPOR = 14
COL_FDEN = 31

# print(daf.col_lbl(31))
RHOIS = 2160.0  # ASSUMED IN-SITU DENSITY (KG/M3), FOR STRAIN MEASURE
USECOLS = (np.arange(0, 32, 1))
IMPORT_FNAME = REPO_DIR + '/' + FOLDER_DIR + '/' + TEST_NAME + '.csv'
# print("Imported Test: " + TESTNAME)
print("File Path: " + IMPORT_FNAME)

# Import .csv file and save it as an array: IMPORT_ARR
IMPORT_ARR = np.genfromtxt(fname=IMPORT_FNAME, delimiter=',', skip_header=1,
                           usecols=USECOLS, dtype=float)

# define vectors containing all rows a selected clumns, noted with "ALL"
DUR_DAY_ALL = daf.duration(IMPORT_ARR[:, COL_TIME])  # ALL DURATION DATA
FDEN_ALL = IMPORT_ARR[:, COL_FDEN]  # NO TIME AVERAGEING
PCON_ALL = IMPORT_ARR[:, COL_PCON] / 145.0
PPOR_ALL = IMPORT_ARR[:, COL_PPOR] / 145.0
TEMP_ALL = IMPORT_ARR[:, COL_TEMP]

# define a subset of data, identified by DUR_START and DUR_END
# if the defined duration limits are changed, so will these values
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
INTERP_NUM = int(DUR_SEC_LEN / INTERP_INC) + 1  # NUM. OF INTERPOLATION INCREMENTS
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

PCON_AVG_PSI = np.mean(PCON_INTERP) * 145
PCON_AVG_MPA = np.mean(PCON_INTERP)
PPOR_AVG_PSI = np.mean(PPOR_INTERP) * 145
PPOR_AVG_MPA = np.mean(PPOR_INTERP)
TEMP_AVG_C = np.mean(TEMP_INTERP)

print("Avg. Confining Pressure (MPa): " + str(PCON_AVG_MPA))
print("Avg. Pore Pressure (MPa): " + str(PPOR_AVG_MPA))
print("Avg. Confining Pressure (psi): " + str(PCON_AVG_PSI))
print("Avg. Pore Pressure (psi): " + str(PPOR_AVG_PSI))
print('Avg. Temperature (C): ' + str(TEMP_AVG_C))

# calculated volume strain rate by fitting model to fractional density
FDEN0 = FDEN_INTERP[0]  # INITIAL FRACTIONAL DENSITY
MODEL = daf.fit_fden(FDEN_INTERP, DUR_DAY_INTERP)  # perform the FIT
SLOPE, C, B, G, KEXP, AEXP, AZERO, AINF = MODEL.best_values.values()
PARM_FIT = MODEL.best_values.values()
# print(PARM_FIT)
# print(MODEL.fit_report())
# print(MODEL.ci_out)
# print(MODEL.best_values)

# plt.figure(0)
# MODEL.plot_fit()
# plt.show
FIT_REPORT = MODEL.fit_report()
# FIT_REPORT_CI = MODEL.ci_report()

FIT_CI = MODEL.ci_out
FIT_RESID = MODEL.residual
FIT_RESID_NORM = linalg.norm(FIT_RESID)
print("Error Norm of Fit: " + str(FIT_RESID_NORM))

plt.figure(0)
MODEL.plot_residuals()
# plt.show()

FDEN_FIT_INTERP = MODEL.eval(x=DUR_DAY_INTERP,
                             slope=SLOPE,
                             c=C,
                             b=B,
                             g=G,
                             kexp=KEXP,
                             aexp=AEXP,
                             azer=AZERO,
                             ainf=AINF)

# FDEN_FIT_INTERP = daf.model_fden(DUR_DAY_INTERP, PARM_FIT)
# FDEN_FIT_INTERP = MODEL.best_fit

# CALCULATE VOLUME STRAIN AND VOLUME STRAIN RATE
VSTRN = -np.log(FDEN0 / FDEN)  # POSITIVE IN COMPRESSION
VSTRN_INTERP = -np.log(FDEN0 / FDEN_INTERP)  # POSITIVE IN COMPRESSION
VSTRN_FIT_INTERP = -np.log(FDEN0 / FDEN_FIT_INTERP)  # POSITIVE IN COMPRESSION

DELTA_VSTRN = np.gradient(VSTRN)
DELTA_VSTRN_INTERP = np.gradient(VSTRN_INTERP)
DELTA_VSTRN_FIT_INTERP = np.gradient(VSTRN_FIT_INTERP)

DELTA_SEC = np.gradient(DUR_SEC)
DELTA_SEC_INTERP = np.gradient(DUR_SEC_INTERP)

VSTRN_RATE = DELTA_VSTRN / DELTA_SEC
VSTRN_RATE_INTERP = DELTA_VSTRN_INTERP / DELTA_SEC_INTERP
VSTRN_RATE_FIT_INTERP = DELTA_VSTRN_FIT_INTERP / DELTA_SEC_INTERP
PTER_INTERP = PCON_INTERP - PPOR_INTERP  # Terzahi pressure
PSOL_INTERP = (PCON_INTERP - PPOR_INTERP * (1 - FDEN_INTERP)) / FDEN_INTERP

##################################
# PLOTTING/EXPORTING BELOW
##################################
# if PLOT_RESID == 1:

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
    CS_DUR_DAY = DUR_START + CSMOD_ARR[:,0] / (3600 * 24)  # PLOTTING TIME
    CS_FDEN = CSMOD_ARR[:,1]
    CS_TEMP = CSMOD_ARR[:,2]
    CS_VSTRN_RATE = CSMOD_ARR[:,3] * (-1)
    CS_PCON = CSMOD_ARR[:,3]
    CS_PDEV = CSMOD_ARR[:,4]

##################################
FS = 14  # FONT SIZE FOR PLOTTING
NUM_SUBPLOT = 3
FIG1, AXARR = plt.subplots(NUM_SUBPLOT, figsize=(13, 10), sharex=True)
AXARR[0].set_title("Test: " + FOLDER_DIR,
                   fontsize=18)
##################################
# EXACT VOLUME STRAIN AND FRACTIONAL DENSITY RELATION
##################################
# lbl_strn = ['Volumetric Strain', 'Fractional Density', 'Lateral Strain']
# AXARR[0].plot(DURATION_DAY, VSTRN, 'b-', lw=3)
# # AXARR[0].plot(PLT_TIME, PLT_ASTRN, 'g-', lw=3)
# # AXARR[0].plot(PLT_TIME, PLT_LSTRN, 'r-', lw=3)
# AXARR[0].grid(True)
# AXARR[0].set_ylabel("Strain", fontsize=FS)
# # AXARR[0].set_ylim(ymin=0)
# YMIN, YMAX = AXARR[0].get_ylim()
# YMIN = FDEN0 / np.exp(-YMIN)
# YMAX = FDEN0 / np.exp(-YMAX)
# AX2A = AXARR[0].twinx()
# AX2A.semilogy(DURATION_DAY, FDEN, 'r-', lw=2)
# AX2A.yaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
# AX2A.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
# AX2A.set_ylabel("Fractional Density", fontsize=FS)
# AX2A.tick_params(labelsize=FS)
# AX2A.set_ylim(ymin=YMIN, ymax=YMAX)
# AX2A.lines[0].remove()
# # AXARR[0].legend(lbl_strn, frameon=1, framealpha=1, loc=0, fontsize=FS)
# AXARR[0].tick_params(labelsize=FS)
# AXARR[0].tick_params(labelsize=FS, pad=10)
#################################
# APPROXIMATE VOLUME STRAIN AND FRACTIONAL DENSITY
# #################################

LBL_FDEN = ["Measured", "Fit", "CS Model"]
# AXARR[0].plot(DUR_DAY_INTERP, FDEN_INTERP, linestyle='-',
#               linewidth=1, marker='.', markersize=4, color='g',
#               alpha=1)
AXARR[0].plot(DUR_DAY, FDEN, linestyle='-', linewidth=1,
              marker='.', markersize=14, color='r', alpha=1)
AXARR[0].plot(DUR_DAY_INTERP, FDEN_FIT_INTERP, linestyle='-',
              linewidth=4, marker=None, markersize=1, color='b',
              alpha=1)
if PLOT_CSMOD == 1:
    AXARR[0].plot(CS_DUR_DAY, CS_FDEN, linestyle='-',
                  linewidth=2, marker=None, markersize=1, color='g',
                  alpha=1)
AXARR[0].grid(True)
AXARR[0].set_ylabel("Fractional Density", fontsize=FS)
AXARR[0].set_ylim(ymin=FDEN0)
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
AXARR[0].legend(LBL_FDEN, frameon=1, framealpha=1, loc=4, fontsize=FS)
AXARR[0].tick_params(labelsize=FS)
AXARR[0].tick_params(labelsize=FS, pad=10)
#################################
lbl_strnrate = ["Interpolated", "Measured", "Fit", "CS Model"]
lbl_interval = ["Sampling"]
AXARR[1].semilogy(DUR_DAY_INTERP, VSTRN_RATE_INTERP, linestyle='-',
                  linewidth=1, marker='.', markersize=12,
                  color='y', alpha=1)
AXARR[1].semilogy(DUR_DAY, VSTRN_RATE, linestyle='-',
                  linewidth=1, marker='.', markersize=12,
                  color='r', alpha=1)
AXARR[1].semilogy(DUR_DAY_INTERP, VSTRN_RATE_FIT_INTERP, linestyle='-',
                  linewidth=4, marker='None', markersize=12,
                  color='b', alpha=1)
if PLOT_CSMOD == 1:
    AXARR[1].semilogy(CS_DUR_DAY, CS_VSTRN_RATE, linestyle='-',
                      linewidth=2, marker='None', markersize=12,
                      color='G', alpha=1)

AXARR[1].grid(True)
AXARR[1].set_ylabel(r'Strain Rate (sec$^{-1}$)', fontsize=FS)

AX2B = AXARR[1].twinx()
AX2B.semilogy(DUR_DAY, DELTA_SEC, linestyle='-',
              linewidth=1, marker='.', markersize=4,
              color='k', alpha=1)
AX2B.set_ylabel("Seconds Per Sample", fontsize=FS)
AX2B.tick_params(labelsize=FS)
AXARR[1].legend(lbl_strnrate, frameon=1, framealpha=0.75, loc=1, fontsize=FS)
AX2B.legend(lbl_interval, frameon=1, framealpha=0.85, loc=4, fontsize=FS)

AXARR[1].tick_params(labelsize=FS)
AXARR[1].tick_params(labelsize=FS, pad=10)
#################################
lbl_strs = ["Confining", "Pore", "Terzaghi",
            "Solid"]
lbl_temp = ["Temperature"]
AXARR[2].plot(DUR_DAY_INTERP, PCON_INTERP, 'b-', lw=3)
AXARR[2].plot(DUR_DAY_INTERP, PPOR_INTERP, 'g-', lw=3)
AXARR[2].plot(DUR_DAY_INTERP, PTER_INTERP, 'r-', lw=3)
AXARR[2].plot(DUR_DAY_INTERP, PSOL_INTERP, 'c-', lw=3)
AXARR[2].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x),
                                                                     ',')))
AXARR[2].grid(True)
AXARR[2].set_ylabel('Pressure (MPa)', fontsize=FS)

AX2C = AXARR[2].twinx()
AX2C.plot(DUR_DAY_INTERP, TEMP_INTERP, linestyle='-',
          linewidth=1, marker='.', markersize=4,
          color='k', alpha=1)
AX2C.set_ylabel(r'Temperature ($^o$C)', fontsize=FS)
AX2C.tick_params(labelsize=FS)

AXARR[2].legend(lbl_strs, frameon=1, framealpha=.85, loc=4, fontsize=FS)
AX2C.legend(lbl_temp, frameon=1, framealpha=0.85, loc=3, fontsize=FS)

AXARR[2].tick_params(labelsize=FS)
AXARR[2].tick_params(labelsize=FS, pad=10)
#################################
LOWEST_CHART = NUM_SUBPLOT - 1
AXARR[LOWEST_CHART].set_xlabel("Test Duration [days]", fontsize=FS,
                               labelpad=10)
majorFormatter = FormatStrFormatter('%2.2f')
AXARR[LOWEST_CHART].xaxis.set_major_formatter(majorFormatter)
AXARR[LOWEST_CHART].tick_params(labelsize=FS, pad=10)
# AXARR[LOWEST_CHART].set_xlim(DUR_START, DUR_END)

# FIG1.tight_layout()
FIG1_NAME = ("PLOTS_" + TEST_NAME + "_" + str(DUR_START) + "-" +
             str(DUR_END) + '.pdf')
PATH = REPO_DIR + '/' + FOLDER_DIR + '/'
#################################
if SAVEFIG != 0:
    FIG1.savefig(PATH + FIG1_NAME)
    print("Figure Saved As: " + FIG1_NAME)
if PLOT != 0:
    plt.show()
if SAVECSV != 0:
    # SAVE RESULTS TO .CSV FILE
    OUT_FILENAME = PATH + TEST_NAME + '_OUT.csv'
    OUT_FILENAME_REPORT = PATH + TEST_NAME + '_FITREPORT.csv'

    COMMENTS = """RESULTS FROM, XX, RUN BY, XX, ON, XX
               """
    HEADER = ('INC,TIME_SEC,ASTRNRATE,LSTRNRATE,ZETARATE,ASTRN,LSTRN,ZETA,\
                VSTRN,FDEN,RHO,MDCREEP,SPCREEP,SSCREEP,FTRN,MSTRS,\
                DSTRS,SEQ,SEQF,F2A,F2L,ASTRS,LSTRS,TEMPC,DSZ,WATER')
    # np.savetxt(OUT_FILENAME, OUT, fmt='%.8e', delimiter=',', newline='\n',
    #            header=HEADER, comments=COMMENTS)
    # print("Saved Data As: " + OUT_FILENAME)

    OUT = open(OUT_FILENAME_REPORT, 'w')
    OUT.write(FIT_REPORT)
    # np.savetxt(OUT_FILENAME_REPORT, FIT_REPORT)
    print("Saved Fit Report As: " + OUT_FILENAME_REPORT)
