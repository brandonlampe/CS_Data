import sys
import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
import matplotlib.axis as ax
from matplotlib import cm
import Table

# relative path to module
sys.path.append(sys.path[0])
import DataAnalysisFunc as daf
REPO_DIR = os.path.dirname(sys.path[0])  # PATH TO REPOSITORY DIRECTORY

SAVE_DIR = 'WP_HY_175'
FOLDER_DIR_LIST = ['UNM_WP_HY_175_09/STAGE01',
                   'UNM_WP_HY_175_10/STAGE01',
                   'UNM_WP_HY_175_11/STAGE01',
                   'UNM_WP_HY_175_12/STAGE01']
# 'UNM_WP_HY_175_04',

# BUILD_SUMMARY = 1  # 0=> SUMMARY IS READ FROM FILE, 1=> SUMMARY IS BUILT
SHOW_PLOT = 1
SAVE_PLOT = 1

OUT_DIR = os.path.join(REPO_DIR, 'SUMMARY', SAVE_DIR)
# CREEP_PARM_LIST = []  # LIST OF dictS of - CREEP parameters
TEST_LIST = []
DATA_DICT = {}  # stores data from LOAD_OUT.csv

STEP_SIZE_SEC = np.array(([10, 100]))  # STEP SIZES (SECONS)

# if BUILD_SUMMARY == 1:
for folder_dir in FOLDER_DIR_LIST:
    test_name = folder_dir[10:]  # + '_comp'
    dir_name = REPO_DIR + '/' + folder_dir

    # print(dir_name)

    for root, fit_name, files in os.walk(dir_name, topdown=True):
        # print(fit_name)
        if fit_name != []:
            FIT_IDX = fit_name.index('LOADING_FIT')
            # print("FIT IDX: " + str(FIT_IDX))
            # print(fit_name)
            fit_dir = os.path.join(root, fit_name[FIT_IDX])
            # print(fit_dir)
            for filename in os.listdir(fit_dir):
                print(test_name)
                if test_name == '175_04':  # choose alternate file
                    if filename[-11:] == 'OUT_MOD.csv':
                        file_dir = os.path.join(fit_dir, filename)
                        print(file_dir)
                        arr = np.loadtxt(fname=file_dir, dtype=float,
                                         delimiter=',', skiprows=3)
                        # print(arr[:5,:])
                        arr_name = test_name[:6]
                        TEST_LIST.append(arr_name)
                        DATA_DICT[arr_name] = arr
                        size = len(DATA_DICT[arr_name])
                        print(test_name)
                elif filename[-7:] == 'OUT.csv':
                    file_dir = os.path.join(fit_dir, filename)
                    print(file_dir)
                    arr = np.loadtxt(fname=file_dir, dtype=float,
                                     delimiter=',', skiprows=3)
                    # print(arr[:5,:])
                    arr_name = test_name[:6]
                    TEST_LIST.append(arr_name)
                    DATA_DICT[arr_name] = arr
                    size = len(DATA_DICT[arr_name])
                    # print(size)

COL_TIME = 0  # SEC
COL_FDEN = 4  # FRACTIONAL DENSITY (MEASURED)
COL_PCON = 8  # CONFINING PRESSURE (MPA)
COL_PPOR = 9  # PORE PRESSURE (MPA)
COL_TEMP = 12  # CONFINING FLUID TEMP (C)

##################################
# PLOTTING
################################################
FS = 14  # FONT SIZE FOR PLOTTING
##################################
LBND = 0.0  # lower bound on color map
UBND = 1.0  # upper bound on color map

LINE_NUM = len(DATA_DICT)
COLORMAP_SUB = np.linspace(LBND, UBND, LINE_NUM)
COLORMAP = [cm.Set1(x) for x in COLORMAP_SUB]

FIG1 = plt.figure(figsize=(13, 10))

AX1 = FIG1.add_subplot(421)
AX2 = FIG1.add_subplot(425)
AX3 = FIG1.add_subplot(427, sharex=AX2)

AX4 = FIG1.add_subplot(422)
AX4A = AX4.twinx()
AX5 = FIG1.add_subplot(424, sharex=AX4)
AX5A = AX5.twinx()
AX6 = FIG1.add_subplot(426, sharex=AX4)
AX6A = AX6.twinx()
AX7 = FIG1.add_subplot(428, sharex=AX4)
AX7A = AX7.twinx()

# CREATE LABELS FOR PLOTTING
FOLDER_DIR_LIST_PLT = []
for i in FOLDER_DIR_LIST:
    FOLDER_DIR_LIST_PLT.append(i[10:])
# print(FOLDER_DIR_LIST_PLT)

STRNRATE_LINES = []
STRN_LINES = []
FDEN_TIME_LINES = []
PPOR_TIME_LINES = []
PCON_TIME_LINES = []
PRES_TIME_LINES = []

PCON_LINES = []
PPOR_LINES = []
PDIF_LINES = []
TEMP_LINES = []

plot_single = 0
for idx, color in enumerate(COLORMAP):
    FDEN0 = DATA_DICT[TEST_LIST[idx]][0, COL_FDEN]
    print("Initial Fractional Density: " + str(FDEN0))
    FDEN = DATA_DICT[TEST_LIST[idx]][:, COL_FDEN]
    PCON = DATA_DICT[TEST_LIST[idx]][:, COL_PCON]
    PPOR = DATA_DICT[TEST_LIST[idx]][:, COL_PPOR]
    PDIF = PCON - PPOR
    TIME0 = DATA_DICT[TEST_LIST[idx]][0, COL_TIME]
    TIME = DATA_DICT[TEST_LIST[idx]][:, COL_TIME] - TIME0
    TEMP = DATA_DICT[TEST_LIST[idx]][:, COL_TEMP]
    STRN = -np.log(FDEN0 / FDEN)
    STRN_DELTA = np.gradient(STRN)
    TIME_DELTA = np.gradient(TIME)
    STRN_RATE = STRN_DELTA / TIME_DELTA
    PRES_ARR = np.array((PCON, PPOR))
    # print(PRES_ARR.shape)

    LBL_FDEN = "Test: " + TEST_LIST[idx]
    LBL_STRN = '_nolegend_'
    LBL_PDIF = '_nolegend_'
    LBL_PCON = '_nolegend_'
    LBL_PRES = [r'$P_c$', r'$P_p$']

    current_fden_time = AX1.plot(TIME, FDEN, color=color, label=LBL_FDEN,
                                 linestyle='-',
                                 linewidth=3, marker='None', markersize=6,
                                 markerfacecolor=color, fillstyle='none',
                                 alpha=1)
    current_pcon = AX2.plot(PDIF, STRN, color=color,
                            label=LBL_PCON,
                            linestyle='-',
                            linewidth=3, marker='None', markersize=4,
                            markerfacecolor=color, fillstyle='bottom',
                            alpha=1)
    current_pdif = AX3.plot(PDIF, FDEN, color=color,
                            label=LBL_PDIF,
                            linestyle='-',
                            linewidth=3, marker='None', markersize=4,
                            markerfacecolor=color, fillstyle='bottom',
                            alpha=1)
    if plot_single == 0:
        AX4.plot(TIME, FDEN, color=color,
                 label=LBL_PCON,
                 linestyle='-',
                 linewidth=3, marker='None', markersize=4,
                 markerfacecolor=color, fillstyle='bottom',
                 alpha=1)
        AX4A.plot(TIME, PRES_ARR.T,
                  label=LBL_PRES,
                  linestyle='--',
                  linewidth=3, marker='None', markersize=4,
                  markerfacecolor=color, fillstyle='bottom',
                  alpha=1)
        AX4A.legend(LBL_PRES, frameon=1, framealpha=.85, loc=0, fontsize=FS,
                    numpoints=3)
    elif plot_single == 1:
        AX5.plot(TIME, FDEN, color=color,
                 label=LBL_PCON,
                 linestyle='-',
                 linewidth=3, marker='None', markersize=4,
                 markerfacecolor=color, fillstyle='bottom',
                 alpha=1)
        AX5A.plot(TIME, PRES_ARR.T,
                  label=LBL_PRES,
                  linestyle='--',
                  linewidth=3, marker='None', markersize=4,
                  markerfacecolor=color, fillstyle='bottom',
                  alpha=1)
        AX5A.legend(LBL_PRES, frameon=1, framealpha=.85, loc=0, fontsize=FS,
                    numpoints=3)
    elif plot_single == 2:
        AX6.plot(TIME, FDEN, color=color,
                 label=LBL_PCON,
                 linestyle='-',
                 linewidth=3, marker='None', markersize=4,
                 markerfacecolor=color, fillstyle='bottom',
                 alpha=1)
        AX6A.plot(TIME, PRES_ARR.T,
                  label=LBL_PRES,
                  linestyle='--',
                  linewidth=3, marker='None', markersize=4,
                  markerfacecolor=color, fillstyle='bottom',
                  alpha=1)
        AX6A.legend(LBL_PRES, frameon=1, framealpha=.85, loc=0, fontsize=FS,
                    numpoints=3)
    elif plot_single == 3:
        AX7.plot(TIME, FDEN, color=color,
                 label=LBL_PCON,
                 linestyle='-',
                 linewidth=3, marker='None', markersize=4,
                 markerfacecolor=color, fillstyle='bottom',
                 alpha=1)
        AX7A.plot(TIME, PRES_ARR.T,
                  label=LBL_PRES,
                  linestyle='--',
                  linewidth=3, marker='None', markersize=4,
                  markerfacecolor=color, fillstyle='bottom',
                  alpha=1)
        AX7A.legend(LBL_PRES, frameon=1, framealpha=.85, loc=0, fontsize=FS,
                    numpoints=3)
    plot_single = plot_single + 1

    FDEN_TIME_LINES.append(current_fden_time)
    # PRES_TIME_LINES.append(current_pres_time)
    # PPOR_TIME_LINES.append(current_ppor_time)
    # PCON_TIME_LINES.append(current_pcon_time)
    PCON_LINES.append(current_pcon)
    PDIF_LINES.append(current_pcon)

XMIN, XMAX = AX2.get_xlim()  # get bounds on volumetric strain axis
XMIN = XMIN
XMAX = XMAX
AX3.set_xlim(xmin=XMIN, xmax=XMAX)

#  CUSTOM TICK MARKS
# TICK = np.arange(1, 1 + TEST_CNT, 1)
# plt.sca(AX3)  # SELECT THE CURRENT AXIS = AX3
# plt.xticks(TICK, FOLDER_DIR_LIST_PLT, rotation=0)
# AX3.set_xlim(xmin=0.5, xmax=TICK[-1] + 0.5)
# AX3.set_xticklabels(FOLDER_DIR_LIST)
# AX3.xtick_params(which='major', rotation='vertical')

# # LOC = AX3.get_major_locator()
# # ax.XTick(axes=AX3, loc=LOC, label=FOLDER_DIR_LIST)

AX1.set_title("Loading Analysis: " + SAVE_DIR, fontsize=18)
# TITLE = FIG1.suptitle("Creep Test Analysis: " + SAVE_DIR, fontsize=18)
# TITLE.set_y(1.0)

AX1.set_ylabel("Fractional Density", fontsize=FS)
AX1.set_xlabel("Loading Time (sec)", fontsize=FS)
AX2.set_ylabel(r'Volumetric Strain', fontsize=FS)
# AX2.set_xlabel("Differential Pressure (MPa)", fontsize=FS)
AX3.set_ylabel('Fractional Density', fontsize=FS)
AX3.set_xlabel('Differential Pressure (MPa)', fontsize=FS)
AX4A.set_ylabel('Pressure (MPa)', fontsize=FS)
AX5A.set_ylabel('Pressure (MPa)', fontsize=FS)
AX6A.set_ylabel('Pressure (MPa)', fontsize=FS)
AX7A.set_ylabel('Pressure (MPa)', fontsize=FS)
AX7.set_xlabel('Loading Time (sec)', fontsize=FS)
AX1.grid()
AX2.grid()
AX3.grid()
AX4.grid()
AX5.grid()
AX6.grid()
AX7.grid()
AX1.tick_params(labelsize=FS, pad=10)
AX2.tick_params(labelsize=FS, pad=10)
AX3.tick_params(labelsize=FS, pad=10)

HANDLES_1, LABELS_1 = AX1.get_legend_handles_labels()
#  bbox_to_anchor(xmin, ymin, xmax, ymax) ro bounding box of legend
LGD1 = AX1.legend(HANDLES_1, LABELS_1, bbox_to_anchor=(0.0, -1.0, 1.0, 0.5),
                  loc='upper left', borderaxespad=1, ncol=3,
                  fontsize=12)
# HANDLES_3, LABELS_3 = AX3.get_legend_handles_labels()
# LGD3 = AX3.legend(HANDLES_3, LABELS_3,
#                   bbox_to_anchor=(1, 0, 1.2, 1),
#                   loc='upper left', borderaxespad=1, ncol=1,
#                   fontsize=12, numpoints=1, labelspacing=1, markerscale=0.75)

FIG1.tight_layout()


if SAVE_PLOT == 1:
    FIG1_NAME = 'LoadingTestSummary_175.pdf'
    FIG1_PATH = os.path.join(OUT_DIR, FIG1_NAME)
    FIG1.savefig(FIG1_PATH, bbox_extra_artists=(LGD1,), bbox_inches='tight')

if SHOW_PLOT == 1:
    plt.show()
