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
FOLDER_DIR_LIST = ['UNM_WP_HY_175_01', 'UNM_WP_HY_175_04']

# BUILD_SUMMARY = 1  # 0=> SUMMARY IS READ FROM FILE, 1=> SUMMARY IS BUILT
SHOW_PLOT = 1
SAVE_PLOT = 1

OUT_DIR = os.path.join(REPO_DIR, 'SUMMARY', SAVE_DIR)
CREEP_PARM_LIST = []  # LIST OF dictS of - CREEP parameters
TEST_SPEC_LIST = []

STEP_SIZE_SEC = np.array(([10, 100]))  # STEP SIZES (SECONS)

# if BUILD_SUMMARY == 1:
for folder_dir in FOLDER_DIR_LIST:
    test_name = folder_dir[10:]  # + '_comp'
    dir_name = REPO_DIR + '/' + folder_dir

    # print(dir_name)

    for root, fit_name, files in os.walk(dir_name, topdown=True):
        # print(fit_name)
        if fit_name != []:
            FIT_IDX = 0  # 0=>CREEP, 1=>FINAL, 2=>LOADING
            if fit_name[FIT_IDX] == 'LOADING_FIT':
                # print(fit_name)
                fit_dir = os.path.join(root, fit_name[FIT_IDX])
                for filename in os.listdir(fit_dir):
                    if filename[-8:] == 'PARM.bin':
                        file_dir = os.path.join(fit_dir, filename)
                        # print(file_dir)
                        with open(file_dir, 'rb') as handle:
                            CREEP_PARM = pickle.loads(handle.read())
                        CREEP_PARM_LIST.append(CREEP_PARM)
                    elif filename[-8:] == 'SPEC.bin':
                        #  ONLY CREEP ANALYSIS HAVE A "SPEC.bin" file
                        if filename[:6] == '175_09':
                            file_dir = os.path.join(fit_dir,
                                                    '175_09_STAGE01' +
                                                    filename[14:])
                        else:
                            file_dir = os.path.join(fit_dir, filename)

                        print(file_dir)
                        with open(file_dir, 'rb') as handle:
                            TEST_SPEC = pickle.loads(handle.read())
                        TEST_SPEC_LIST.append(TEST_SPEC)

TEST_CNT = len(TEST_SPEC_LIST)
PCON = np.zeros(TEST_CNT)
PPOR = np.zeros(TEST_CNT)
PDIF = np.zeros(TEST_CNT)

# for i in xrange(TEST_CNT):
#     PCON[i] = TEST_SPEC_LIST[i]['average confining pressure']
#     PPOR[i] = TEST_SPEC_LIST[i]['average pore pressure']
#     PDIF[i] = PCON[i] - PPOR[i]


# CREEP (FUNCTION OF TIME)
NROW = 1204
PLT_TIME_DAY = np.zeros((1204, len(FOLDER_DIR_LIST)))
PLT_VSTRN_RATE = np.zeros((1204, len(FOLDER_DIR_LIST)))
PLT_FDEN = np.zeros((1204, len(FOLDER_DIR_LIST)))
for i in xrange(len(FOLDER_DIR_LIST)):
    CREEP_START = CREEP_PARM_LIST[i]['start']
    if FOLDER_DIR_LIST[i] == 'UNM_WP_HY_175_04':
        CREEP_END = 6  # 16.132
    else:
        CREEP_END = CREEP_PARM_LIST[i]['end']

    # print(CREEP_PARM_LIST[i])

    CREEP_DUR_DAY = CREEP_END - CREEP_START
    CREEP_DUR_SEC = CREEP_DUR_DAY * 24 * 3600
    CREEP_TIME_END_01 = 3600  # SECONDS
    CREEP_TIME_END_02 = 48000  # SECONDS
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
    # print(len(CREEP_TIME_DAY))
    CREEP_FDEN = daf.schnute(x=CREEP_TIME_DAY + CREEP_START,
                             start=CREEP_PARM_LIST[i]['start'],
                             end=CREEP_PARM_LIST[i]['end'],
                             a=CREEP_PARM_LIST[i]['a'],
                             b=CREEP_PARM_LIST[i]['b'],
                             c=CREEP_PARM_LIST[i]['c'],
                             d=CREEP_PARM_LIST[i]['d'])

    # CREEP_FDEN_RATE = daf.deriv_schnute(x=CREEP_TIME_DAY + CREEP_START,
    #                                     start=CREEP_PARM_LIST[i]['start'],
    #                                     end=CREEP_PARM_LIST[i]['end'],
    #                                     a=CREEP_PARM_LIST[i]['a'],
    #                                     b=CREEP_PARM_LIST[i]['b'],
    #                                     c=CREEP_PARM_LIST[i]['c'],
    #                                     d=CREEP_PARM_LIST[i]['d'])
    # CREEP_FDEN_RATE_SEC = CREEP_FDEN_RATE / (24 * 3600)
    FDEN_ZERO = CREEP_FDEN[0]
    CREEP_VSTRN = np.log(CREEP_FDEN / FDEN_ZERO)

    CREEP_DELTA_VSTRN = np.gradient(CREEP_VSTRN)
    CREEP_DELTA_SEC = np.gradient(CREEP_TIME_SEC)
    CREEP_VSTRN_RATE = CREEP_DELTA_VSTRN / CREEP_DELTA_SEC

    PLT_FDEN[:, i] = CREEP_FDEN
    PLT_VSTRN_RATE[:, i] = CREEP_VSTRN_RATE
    PLT_TIME_DAY[:, i] = CREEP_TIME_DAY

# print(CREEP_VSTRN_RATE)
##################################
# PLOTTING
################################################
FS = 14  # FONT SIZE FOR PLOTTING
##################################
LBND = 0.0  # lower bound on color map
UBND = 1.0  # upper bound on color map

LINE_NUM = PLT_FDEN.shape[1]
COLORMAP_SUB = np.linspace(LBND, UBND, LINE_NUM)
COLORMAP = [cm.Set1(x) for x in COLORMAP_SUB]

FIG1 = plt.figure(figsize=(13, 10))
AX1 = FIG1.add_subplot(311)
AX2 = FIG1.add_subplot(312)
AX3 = FIG1.add_subplot(313)

# CREATE LABELS FOR PLOTTING
FOLDER_DIR_LIST_PLT = []
for i in FOLDER_DIR_LIST:
    FOLDER_DIR_LIST_PLT.append(i[10:])
# print(FOLDER_DIR_LIST_PLT)

STRNRATE_LINES = []
FDEN_LINES = []
PCON_LINES = []
PPOR_LINES = []
PDIF_LINES = []
for idx, color in enumerate(COLORMAP):
    FDEN = PLT_FDEN[:, idx]
    STRNRATE = PLT_VSTRN_RATE[:, idx]
    TIME = PLT_TIME_DAY[:, idx]
    LBL_FDEN = "Test: " + FOLDER_DIR_LIST_PLT[idx]
    LBL_STRNRATE = '_nolegend_'
    if idx == 0:
        LBL_PCON = 'Confining Pressure'
        LBL_PPOR = 'Pore Pressure'
        LBL_PDIF = 'Pressure Difference'
    else:
        LBL_PCON = '_nolegend_'
        LBL_PPOR = '_nolegend_'
        LBL_PDIF = '_nolegend_'

    current_fden = AX1.plot(TIME, FDEN, color=color, label=LBL_FDEN,
                            linestyle='-',
                            linewidth=3, marker='None', markersize=6,
                            markerfacecolor=color, fillstyle='none',
                            alpha=1)
    current_strnrate = AX2.semilogy(FDEN, STRNRATE, color=color,
                                    label=LBL_STRNRATE,
                                    linestyle='-',
                                    linewidth=3, marker='None', markersize=4,
                                    markerfacecolor=color, fillstyle='bottom',
                                    alpha=1)
    current_pcon = AX3.plot(idx + 1, PCON[idx], color=color,
                            label=LBL_PCON,
                            linestyle='None',
                            linewidth=2, marker='s', markersize=16,
                            markerfacecolor=color, fillstyle='full',
                            alpha=1)
    current_ppor = AX3.plot(idx + 1, PPOR[idx], color=color,
                            label=LBL_PPOR,
                            linestyle='None',
                            linewidth=2, marker='o', markersize=16,
                            markerfacecolor=color, fillstyle='full',
                            alpha=1)
    current_pdif = AX3.plot(idx + 1, PDIF[idx], color=color,
                            label=LBL_PDIF,
                            linestyle='None',
                            linewidth=2, marker='D', markersize=16,
                            markerfacecolor=color, fillstyle='full',
                            alpha=1)

    FDEN_LINES.append(current_fden)
    STRNRATE_LINES.append(current_strnrate)
    PCON_LINES.append(current_pcon)
    PPOR_LINES.append(current_pcon)
    PDIF_LINES.append(current_pcon)

TICK = np.arange(1, 1 + TEST_CNT, 1)
plt.sca(AX3)  # SELECT THE CURRENT AXIS = AX3
plt.xticks(TICK, FOLDER_DIR_LIST_PLT, rotation=0)
AX3.set_xlim(xmin=0.5, xmax=TICK[-1] + 0.5)
# AX3.set_xticklabels(FOLDER_DIR_LIST)
# AX3.xtick_params(which='major', rotation='vertical')

# LOC = AX3.get_major_locator()
# ax.XTick(axes=AX3, loc=LOC, label=FOLDER_DIR_LIST)

AX1.set_title("Creep Test Analysis: " + SAVE_DIR, fontsize=18)
# TITLE = FIG1.suptitle("Creep Test Analysis: " + SAVE_DIR, fontsize=18)
# TITLE.set_y(1.0)

AX1.set_ylabel("Fractional Density", fontsize=FS)
AX1.set_xlabel("Creep Time (days)", fontsize=FS)
AX2.set_ylabel(r'Strain Rate $\left(\frac{1}{sec}\right)$', fontsize=FS)
AX2.set_xlabel("Fractional Density", fontsize=FS)
AX3.set_ylabel('Creep Pressures (MPa)', fontsize=FS)
AX3.set_xlabel('Test Name', fontsize=FS)
AX1.grid()
AX2.grid()
AX3.grid()
AX1.tick_params(labelsize=FS, pad=10)
AX2.tick_params(labelsize=FS, pad=10)
AX3.tick_params(labelsize=FS, pad=10)

HANDLES_1, LABELS_1 = AX1.get_legend_handles_labels()
#  bbox_to_anchor(xmin, ymin, xmax, ymax) ro bounding box of legend
LGD1 = AX1.legend(HANDLES_1, LABELS_1, bbox_to_anchor=(1, 0, 1.2, 1),
                  loc='upper left', borderaxespad=1, ncol=1,
                  fontsize=12)
HANDLES_3, LABELS_3 = AX3.get_legend_handles_labels()
LGD3 = AX3.legend(HANDLES_3, LABELS_3,
                  bbox_to_anchor=(1, 0, 1.2, 1),
                  loc='upper left', borderaxespad=1, ncol=1,
                  fontsize=12, numpoints=1, labelspacing=1, markerscale=0.75)

FIG1.tight_layout()


if SAVE_PLOT == 1:
    FIG1_NAME = 'CreepTestSummary_175.pdf'
    FIG1_PATH = os.path.join(OUT_DIR, FIG1_NAME)
    FIG1.savefig(FIG1_PATH, bbox_extra_artists=(LGD1,), bbox_inches='tight')

if SHOW_PLOT == 1:
    plt.show()
