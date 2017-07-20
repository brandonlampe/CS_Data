import sys
import numpy as np
import os
import pickle
# import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
# import matplotlib.axis as ax
# from mpl_toolkits.mplot3d import Axes3D
import scipy.interpolate as interp
import scipy.ndimage.filters as filters
from matplotlib import cm
# import Table

# relative path to module
sys.path.append(sys.path[0])
# import DataAnalysisFunc as daf
REPO_DIR = os.path.dirname(sys.path[0])  # PATH TO REPOSITORY DIRECTORY

SAVE_DIR = 'CREEP_PRES_DEN'
FOLDER_DIR_LIST = [
    # 'UNM_WP_HY_175_09/STAGE02',
    'UNM_WP_HY_175_09/STAGE03',
    'UNM_WP_HY_175_09/STAGE04',
    'UNM_WP_HY_175_09/STAGE05',
    'UNM_WP_HY_175_09/STAGE06',
    # 'UNM_WP_HY_175_09/STAGE07',
    # 'UNM_WP_HY_175_09/STAGE08',
    # 'UNM_WP_HY_175_09/STAGE09',
    # 'UNM_WP_HY_175_09/STAGE10',
    # 'UNM_WP_HY_175_09/STAGE12',
    # 'UNM_WP_HY_175_09/STAGE12',
    # 'UNM_WP_HY_175_09/STAGE13',
    # 'UNM_WP_HY_175_09/STAGE15',
    # 'UNM_WP_HY_175_09/STAGE14',
    # 'UNM_WP_HY_175_09/STAGE16',
    # 'UNM_WP_HY_175_09/STAGE17',
    # 'UNM_WP_HY_175_09/STAGE18',
    # 'UNM_WP_HY_175_09/STAGE19',
    # 'UNM_WP_HY_175_09/STAGE20',
    # 'UNM_WP_HY_175_09/STAGE21',
    # 'UNM_WP_HY_175_09/STAGE22',
    # 'UNM_WP_HY_175_11/STAGE02',  # NEGATIVE CREEP RATE
    # 'UNM_WP_HY_175_11/STAGE04',  # NEGATIVE CREEP RATE
    # 'UNM_WP_HY_175_11/STAGE05',  # NEGATIVE CREEP RATE
    'UNM_WP_HY_175_12/STAGE02',
    'UNM_WP_HY_175_12/STAGE03',
    'UNM_WP_HY_175_12/STAGE04',
    'UNM_WP_HY_175_12/STAGE05',
    # 'UNM_WP_HY_175_13/STAGE02',  # FIRST 24 HRS OF TRANS CREEP
    'UNM_WP_HY_175_13/STAGE03',
    'UNM_WP_HY_175_13/STAGE04',
    'UNM_WP_HY_175_13/STAGE05',
    'UNM_WP_HY_175_13/STAGE06',
    'UNM_WP_HY_175_13/STAGE07',
    'UNM_WP_HY_175_13/STAGE08',
    'UNM_WP_HY_175_13/STAGE09',
    'UNM_WP_HY_175_13/STAGE10',
    'UNM_WP_HY_175_13/STAGE11',
    'UNM_WP_HY_175_13/STAGE12',
    'UNM_WP_HY_175_13/STAGE13'
]

SHOW_PLOT = 1
SAVE_PLOT = 1
ENABLE_LOG = True
FIG1_NAME = 'SS_CREEP_ANALYSIS_Select.pdf'
CONT_COUNT = 5 # number of contours on plot

OUT_DIR = os.path.join(REPO_DIR, 'SUMMARY', SAVE_DIR)
CREEP_PARM_LIST = []  # LIST OF dictS of - CREEP parameters
TEST_SPEC_LIST = []  # RECORDS TEST TEMPERATURE, PRESSURE, ETC.
TEST_LIST = []  # STORES THE TEST NAMES FOR PLOTTING LAEELS
VSTRN_RATE_LIST = []
DAY_MED_LIST = []
# DATA_DICT = {}  # DICTIONARY, LOADS .CSV FILE FROM ANALYSIS_CREEP

for folder_dir in FOLDER_DIR_LIST:
    test_name = folder_dir[10:]
    TEST_LIST.append(test_name)
    dir_name = REPO_DIR + '/' + folder_dir
    # print(dir_name)
    for root, fit_name, files in os.walk(dir_name, topdown=True):
        # print(fit_name)
        if fit_name != []:
            FIT_IDX = 0  # 0=>CREEP, 1=>FINAL, 2=>LOADING
            if fit_name[FIT_IDX] == 'CREEP_FIT':
                # print(fit_name)
                fit_dir = os.path.join(root, fit_name[FIT_IDX])
                for filename in os.listdir(fit_dir):
                    if filename[-8:] == 'PARM.bin':
                        file_dir = os.path.join(fit_dir, filename)
                        # print(file_dir)
                        with open(file_dir, 'rb') as handle:
                            CREEP_PARM = pickle.loads(handle.read())
                        CREEP_PARM_LIST.append(CREEP_PARM)
                        # print(CREEP_PARM_LIST)
                    elif filename[-8:] == 'SPEC.bin':
                        file_dir = os.path.join(fit_dir, filename)
                        # print(file_dir)
                        with open(file_dir, 'rb') as handle:
                            TEST_SPEC = pickle.loads(handle.read())
                        TEST_SPEC_LIST.append(TEST_SPEC)
                        # print(TEST_SPEC_LIST)
                    elif filename[-7:] == 'OUT.csv':
                        file_dir = os.path.join(fit_dir, filename)
                        arr = np.loadtxt(fname=file_dir, dtype=float,
                                         delimiter=',', skiprows=3)
                        COL_DAY = 1  # COLUMN NUMBER FOR DURATION IN DAYS
                        COL_VSTRN_RATE = 7  # COLUMN NUMBER FOR VSTRN_RATE

                        DAY_MIN = arr[0, COL_DAY]
                        DAY_MAX = arr[-1, COL_DAY]
                        DAY_MED_LIST.append((DAY_MIN + DAY_MAX) / 2)
                        # print("Start Test:" + str(DAY_MIN))
                        # print("End Test:" + str(DAY_MAX))
                        VSTRN_RATE_LIST.append(arr[0, COL_VSTRN_RATE])

TEST_CNT = len(TEST_SPEC_LIST)
PCON = np.zeros(TEST_CNT)
PPOR = np.zeros(TEST_CNT)
PDIF = np.zeros(TEST_CNT)
VSTRN_RATE = np.zeros(TEST_CNT)
FDEN_MED = np.zeros(TEST_CNT)

for i in xrange(TEST_CNT):
    PCON[i] = TEST_SPEC_LIST[i]['average confining pressure']
    PPOR[i] = TEST_SPEC_LIST[i]['average pore pressure']
    PDIF[i] = PCON[i] - PPOR[i]
    VSTRN_RATE[i] = VSTRN_RATE_LIST[i]
    FDEN_MED[i] = CREEP_PARM_LIST[i]['intercept'] +\
        (CREEP_PARM_LIST[i]['slope'] * DAY_MED_LIST[i])

# print(VSTRN_RATE)
# print(FDEN_MED)

##################################
# PLOTTING
################################################
FS = 14  # FONT SIZE FOR PLOTTING
##################################
LBND = 0.0  # lower bound on color map
UBND = 1.0  # upper bound on color map

LINE_NUM = TEST_CNT
COLORMAP_SUB = np.linspace(LBND, UBND, LINE_NUM)
COLORMAP = [cm.Set1(x) for x in COLORMAP_SUB]

FIG1 = plt.figure(figsize=(13, 10))
FIG1.set_tight_layout(True)
GS = gridspec.GridSpec(nrows=3, ncols=2)
AX1 = FIG1.add_subplot(GS[1, 1])
AX2 = FIG1.add_subplot(GS[1, 0])
AX3 = FIG1.add_subplot(GS[2, 0:2])
AX4 = FIG1.add_subplot(GS[0, 0])
# NAME PLOT LINES
FDEN_STRNRATE_LINES = []
PDIF_STRNRATE_LINES = []
FDEN_PDIF_LINES = []

for idx, color in enumerate(COLORMAP):
    LBL_FDEN = "Test: " + TEST_LIST[idx]
    current_fden_strnrate = AX1.semilogy(FDEN_MED[idx], VSTRN_RATE[idx],
                                         color=color,
                                         label=LBL_FDEN,
                                         linestyle='None',
                                         linewidth=3, marker='o',
                                         markersize=8,
                                         markerfacecolor=color,
                                         fillstyle='none',
                                         alpha=1)
    current_pdif_strnrate = AX2.semilogy(PDIF[idx], VSTRN_RATE[idx],
                                         color=color,
                                         label=LBL_FDEN,
                                         linestyle='None',
                                         linewidth=3, marker='o',
                                         markersize=8,
                                         markerfacecolor=color,
                                         fillstyle='none',
                                         alpha=1)
    current_fden_pdif = AX4.plot(FDEN_MED[idx], PDIF[idx],
                                 color=color,
                                 label=LBL_FDEN,
                                 linestyle='None',
                                 linewidth=3, marker='o',
                                 markersize=8,
                                 markerfacecolor=color,
                                 fillstyle='none',
                                 alpha=1)

    FDEN_STRNRATE_LINES.append(current_fden_strnrate)
    PDIF_STRNRATE_LINES.append(current_pdif_strnrate)
    FDEN_PDIF_LINES.append(current_fden_pdif)

#############################################
# CREATE GRID FOR FDEN CONTOURS
#############################################
PDIF_GRID = np.linspace(5, 40, 100)
VSTRN_RATE_GRID = np.logspace(-7, -10, 100)
# VSTRN_RATE_GRID = np.linspace(2e-8, 1.5e-9, 100)

FDEN_MED_GRID = interp.griddata((PDIF, VSTRN_RATE), FDEN_MED,
                                (PDIF_GRID[None, :], VSTRN_RATE_GRID[:, None]),
                                method='linear')
SIGMA = 0.7
FILTERED_DATA = filters.gaussian_filter(FDEN_MED_GRID, SIGMA)

CONTOUR_LINE = AX3.contour(PDIF_GRID, VSTRN_RATE_GRID, FDEN_MED_GRID,
                           CONT_COUNT, linewidth=0.5, colors='k')
CONTOUR_FILL = AX3.contourf(PDIF_GRID, VSTRN_RATE_GRID, FDEN_MED_GRID,
                            CONT_COUNT, cmap=cm.jet)
COLOR_BAR = plt.colorbar(CONTOUR_FILL, ax=AX3, use_gridspec=True)
# CONTOUR_LABELS = plt.clabel(CONTOUR_SET, inline=1, fontsize=10)
AX3.scatter(PDIF, VSTRN_RATE, s=70, c=COLORMAP)

if ENABLE_LOG:
    # AX3.set_yscale('symlog')
    AX3.set_yscale('log')
    # AX3.set_ylim(ymin=-1e-9, ymax=1e-7)
    AX3.xaxis.grid(True, which='minor')

#  CUSTOM TICK MARKS
# TICK = np.arange(1, 1 + TEST_CNT, 1)
# plt.sca(AX3)  # SELECT THE CURRENT AXIS = AX3
# plt.xticks(TICK, FOLDER_DIR_LIST_PLT, rotation=0)
# AX3.set_xlim(xmin=0.5, xmax=TICK[-1] + 0.5)
# AX3.set_xticklabels(FOLDER_DIR_LIST)
# AX3.xtick_params(which='major', rotation='vertical')

AX3.set_ylabel('Strain Rate', fontsize=FS)
AX3.set_xlabel('Differential Pressure (MPa)', fontsize=FS)
COLOR_BAR.set_label('Fractional Density')
#############################################
AX1.set_ylabel("Strain Rate", fontsize=FS)
AX1.set_xlabel("Fractional Density", fontsize=FS)

AX2.set_ylabel('Strain Rate', fontsize=FS)
AX2.set_xlabel('Differential Pressure (MPa)', fontsize=FS)

AX4.set_ylabel('Differential Pressure (MPa)', fontsize=FS)
AX4.set_xlabel('Fractional Density', fontsize=FS)

AX1.grid()
AX2.grid()
AX3.grid()
AX4.grid()

AX1.tick_params(labelsize=FS, pad=10)
AX2.tick_params(labelsize=FS, pad=10)
AX3.tick_params(labelsize=FS, pad=10)

HANDLES_1, LABELS_1 = AX4.get_legend_handles_labels()
#  bbox_to_anchor(xmin, ymin, xmax, ymax) ro bounding box of legend
LGD = AX4.legend(HANDLES_1, LABELS_1, bbox_to_anchor=(1.2, -.2, 2.0, 1.0),
                 loc='lower left', borderaxespad=1, ncol=2,
                 fontsize=12, numpoints=1)

if SAVE_PLOT == 1:
    FIG1_PATH = os.path.join(OUT_DIR, FIG1_NAME)
    FIG1.savefig(FIG1_PATH, bbox_extra_artists=(LGD,), bbox_inches='tight')

if SHOW_PLOT == 1:
    plt.show()
