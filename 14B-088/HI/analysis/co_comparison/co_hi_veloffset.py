import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.visualization import AsinhStretch
from astropy.visualization.mpl_normalize import ImageNormalize
from spectral_cube import Projection
import seaborn as sb
from corner import hist2d
from os.path import join, exists
import os

from paths import (fourteenB_wGBT_HI_file_dict,
                   iram_co21_14B088_data_path,
                   allfigs_path)
from plotting_styles import onecolumn_figure, default_figure, twocolumn_figure
from constants import hi_freq


'''
Is bright CO better correlated w/ the HI velocity?

Compare the peak temp of CO between the CO and HI velocities.

'''

fig_path = join(allfigs_path(""), "co_vs_hi")
if not exists(fig_path):
    os.mkdir(fig_path)

hi_mom1 = fits.open(fourteenB_wGBT_HI_file_dict['Moment1'])[0].data / 1000.
hi_peakvels = fits.open(fourteenB_wGBT_HI_file_dict['PeakVels'])[0].data / 1000.
hi_peaktemp = fits.open(fourteenB_wGBT_HI_file_dict['PeakTemp'])[0].data

co_mom1 = fits.open(iram_co21_14B088_data_path("m33.co21_iram.14B-088_HI.mom1.fits"))[0].data / 1000.
co_peakvels = fits.open(iram_co21_14B088_data_path("m33.co21_iram.14B-088_HI.peakvels.fits"))[0].data / 1000.
co_peaktemp = fits.open(iram_co21_14B088_data_path("m33.co21_iram.14B-088_HI.peaktemps.fits"))[0].data

co_mask = fits.open(iram_co21_14B088_data_path("m33.co21_iram.14B-088_HI_source_mask.fits"))[0]

good_co_pts = co_mask.data.sum(0) >= 2

good_pts = np.logical_and(np.isfinite(hi_mom1), good_co_pts)
# Impose 3 sigma cut on the CO peaks
good_pts = np.logical_and(good_pts, co_peaktemp > 0.06)


onecolumn_figure(font_scale=1.1)

# Mom1 comparisons
hist2d(np.abs((co_mom1 - hi_mom1)[good_pts]), co_peaktemp[good_pts],
       bins=16, data_kwargs={"alpha": 0.6},
       range=[(0.0, 25.0),
              (0.0, 1.05 * np.max(co_peaktemp[good_pts]))])
plt.axhline(0.06, color='r', linestyle='--')
plt.ylabel(r"T$_\mathrm{peak, CO}$ (K)")
plt.xlabel(r"$|V_{\rm cent, CO} - V_{\rm cent, HI}|$ (km/s)")
plt.grid()
plt.tight_layout()

plt.savefig(allfigs_path(join(fig_path, "co21_Tpeak_centroid_velocity_offset.pdf")))
plt.savefig(allfigs_path(join(fig_path, "co21_Tpeak_centroid_velocity_offset.png")))
plt.close()

hist2d(np.abs((co_mom1 - hi_mom1)[good_pts]), hi_peaktemp[good_pts],
       bins=16, data_kwargs={"alpha": 0.6},
       range=[(0.0, 25.0),
              (0.0, 1.05 * np.max(hi_peaktemp[good_pts]))])
plt.ylabel(r"T$_\mathrm{peak, HI}$ (K)")
plt.xlabel(r"$|V_{\rm cent, CO} - V_{\rm cent, HI}|$ (km/s)")
plt.grid()
plt.tight_layout()

plt.savefig(allfigs_path(join(fig_path, "hi_Tpeak_centroid_velocity_offset.pdf")))
plt.savefig(allfigs_path(join(fig_path, "hi_Tpeak_centroid_velocity_offset.png")))
plt.close()

# Peak Velocity Comparisons
hist2d(np.abs((co_peakvels - hi_peakvels)[good_pts]), co_peaktemp[good_pts],
       bins=16, data_kwargs={"alpha": 0.6},
       range=[(0.0, 25.),
              (0.0, 1.05 * np.max(co_peaktemp[good_pts]))])
plt.axhline(0.06, color='r', linestyle='--')
plt.ylabel(r"T$_\mathrm{peak, CO}$ (K)")
plt.xlabel(r"$|V_{\rm peak, CO} - V_{\rm peak, HI}|$ (km/s)")
plt.grid()
plt.tight_layout()

plt.savefig(allfigs_path(join(fig_path, "co21_Tpeak_peakvel_velocity_offset.pdf")))
plt.savefig(allfigs_path(join(fig_path, "co21_Tpeak_peakvel_velocity_offset.png")))
plt.close()

hist2d(np.abs((co_peakvels - hi_peakvels)[good_pts]), hi_peaktemp[good_pts],
       bins=16, data_kwargs={"alpha": 0.6},
       range=[(0.0, 25.),
              (0.0, 1.05 * np.max(hi_peaktemp[good_pts]))])
plt.ylabel(r"T$_\mathrm{peak, HI}$ (K)")
plt.xlabel(r"$|V_{\rm peak, CO} - V_{\rm peak, HI}|$ (km/s)")
plt.grid()
plt.tight_layout()

plt.savefig(allfigs_path(join(fig_path, "hi_Tpeak_peakvel_velocity_offset.pdf")))
plt.savefig(allfigs_path(join(fig_path, "hi_Tpeak_peakvel_velocity_offset.png")))
plt.close()


# Where do the outliers occur
moment0 = Projection.from_hdu(fits.open(fourteenB_wGBT_HI_file_dict["Moment0"])[0])

moment0_Kkm_s = moment0.value * moment0.beam.jtok(hi_freq).value / 1000.

twocolumn_figure(fig_ratio=0.95, font_scale=1.2)
sb.set_palette("colorblind")

ax = plt.subplot(111, projection=moment0.wcs.celestial)
im = ax.imshow(moment0_Kkm_s,
               origin='lower',
               interpolation='nearest',
               norm=ImageNormalize(vmin=-0.001,
                                   vmax=np.nanmax(moment0_Kkm_s),
                                   stretch=AsinhStretch()))
ax.set_ylabel("DEC (J2000)")
ax.set_xlabel("RA (J2000)")
# ax.set_ylim([260, 900])
# ax.set_xlim([130, 620])

# Where are the velocity outliers spatially?
# Assign colours to points based on their percentile in the distribution
vel_diff = np.abs(co_mom1 - hi_mom1)
percs = np.nanpercentile(vel_diff[good_pts],
                         [85, 95, 99, 99.5])
labels = ["85\%", "95\%", "99\%", "99.5\%"]
labels = [r"$>$ {0} km/s ({1})".format(round(perc, 1), label)
          for perc, label in zip(percs, labels)]

cols = ["D", "s", "o", "^"]

nonan_vel_diff = vel_diff.copy()
nonan_vel_diff[np.isnan(nonan_vel_diff)] = 0.0

for perc, col, label in zip(percs, cols, labels):
    ypos, xpos = np.where(np.logical_and(nonan_vel_diff > perc, good_pts))
    plt.plot(xpos, ypos, col, label=label)

plt.legend(loc='lower left', frameon=True)

cbar = plt.colorbar(im)
cbar.set_label(r"Integrated Intensity (K km s$^{-1}$)")

plt.savefig(allfigs_path(join(fig_path, "co21_HI_centroid_offset_outliers.pdf")))
plt.savefig(allfigs_path(join(fig_path, "co21_HI_centroid_offset_outliers.png")))
plt.close()

# Peak velocity outliers
ax = plt.subplot(111, projection=moment0.wcs.celestial)
im = ax.imshow(moment0_Kkm_s,
               origin='lower',
               interpolation='nearest',
               norm=ImageNormalize(vmin=-0.001,
                                   vmax=np.nanmax(moment0_Kkm_s),
                                   stretch=AsinhStretch()))
ax.set_ylabel("DEC (J2000)")
ax.set_xlabel("RA (J2000)")
# ax.set_ylim([260, 900])
# ax.set_xlim([130, 620])

# Where are the velocity outliers spatially?
# Assign colours to points based on their percentile in the distribution
vel_diff = np.abs(co_peakvels - hi_peakvels)
percs = np.nanpercentile(vel_diff[good_pts],
                         [85, 95, 99, 99.5])
labels = ["85\%", "95\%", "99\%", "99.5\%"]
labels = [r"$>$ {0} km/s ({1})".format(round(perc, 1), label)
          for perc, label in zip(percs, labels)]

cols = ["D", "s", "o", "^", '1']

nonan_vel_diff = vel_diff.copy()
nonan_vel_diff[np.isnan(nonan_vel_diff)] = 0.0

for perc, col, label in zip(percs, cols, labels):
    ypos, xpos = np.where(np.logical_and(nonan_vel_diff > perc, good_pts))
    plt.plot(xpos, ypos, col, label=label)

plt.legend(loc='lower left', frameon=True)

cbar = plt.colorbar(im)
cbar.set_label(r"Integrated Intensity (K km s$^{-1}$)")

plt.savefig(allfigs_path(join(fig_path, "co21_HI_peakvels_offset_outliers.pdf")))
plt.savefig(allfigs_path(join(fig_path, "co21_HI_peakvels_offset_outliers.png")))
plt.close()

default_figure()
