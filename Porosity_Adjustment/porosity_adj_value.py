import numpy as np
import os
# import sys

# porosity values are pulled from the produced .npy file
# this file must be run for porosity adjustments to take effect

current_dir = os.getcwd()
save_path = os.path.join(current_dir, 'porosity_adj.npy')

print "Porosity Adjustment Value"

adjustment_dict = {}

# values to subtract from measured porosity
adjustment_dict['175_01'] = -0.
adjustment_dict['175_03'] = -0.
adjustment_dict['175_04'] = -0.
adjustment_dict['175_09'] = -0.0343
adjustment_dict['175_10'] = -0.0602
adjustment_dict['175_11'] = -0.0729
adjustment_dict['175_12'] = -0.0640
adjustment_dict['175_13'] = -0.07623
adjustment_dict['175_15'] = -0.0840
adjustment_dict['175_16'] = -0.024
adjustment_dict['90_02'] = -0.
adjustment_dict['90_03'] = -0.
adjustment_dict['90_04'] = -0.0476
adjustment_dict['90_08'] = -0.
adjustment_dict['250_03'] = -0.0243

print adjustment_dict

np.save(save_path, adjustment_dict)
