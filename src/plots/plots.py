import numpy as np
import matplotlib.pyplot as plt
from luxpy import spd_to_xyz, plotSL, utils, xyz_to_Yuv, plot_color_data, plot_spectrum_colors

wavelengths = np.linspace(380, 780, 1000)
intensities = np.sin(wavelengths / 100)

spd = np.vstack((wavelengths, intensities)).T 




plot_spectrum_colors(spd)
plt.show()

# CIE 1931 XYZ koordináták kiszámítása
xyz = spd_to_xyz(spd)

Yuv_REF_2 = xyz_to_Yuv(xyz)

# xyz_TCS8_REF_2, xyz_REF_2 = spd_to_xyz(REF, cieobs = cieobs, \
#                                           rfl = TCS8, relative = True, out = 2)

# Az xy diagram ábrázolása
# Step 1:
# axh = plotSL(cspace = 'Yuv', show = False,\
#                  BBL = True, DL = True, diagram_colors = True)

# Step 2:
# Y, u, v = utils.asplit(Yuv_REF_2) # splits array along last axis

# Step 3:
# plot_color_data(u, v, formatstr = 'go', axh = axh, label = 'Yuv_REF_2')