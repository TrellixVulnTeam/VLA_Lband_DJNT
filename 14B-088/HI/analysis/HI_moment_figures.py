
'''
Make figures of the zeroth and first moments.
'''

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from astropy.visualization import AsinhStretch
from astropy.visualization.mpl_normalize import ImageNormalize
from radio_beam import Beam
from astropy.wcs.utils import proj_plane_pixel_area

from paths import (fourteenB_HI_file_dict, allfigs_path,
                   fourteenB_wGBT_HI_file_dict)
from constants import hi_freq, hi_coldens_Kkms
from plotting_styles import default_figure, twocolumn_figure

default_figure()

moment0 = fits.open(fourteenB_HI_file_dict["Moment0"])[0]
moment0_wcs = WCS(moment0.header)

moment0_feath = fits.open(fourteenB_wGBT_HI_file_dict["Moment0"])[0]

peaktemps = fits.open(fourteenB_HI_file_dict["PeakTemp"])[0].data
peaktemps_feath = fits.open(fourteenB_wGBT_HI_file_dict["PeakTemp"])[0].data

beam = Beam.from_fits_header(moment0.header)

moment0_Kkm_s = beam.jtok(hi_freq).value * moment0.data / 1000.
moment0_coldens = moment0_Kkm_s * hi_coldens_Kkms.value

moment0_Kkm_s_feath = beam.jtok(hi_freq).value * moment0_feath.data / 1000.
moment0_coldens_feath = moment0_Kkm_s_feath * hi_coldens_Kkms.value

pixscale = np.sqrt(proj_plane_pixel_area(moment0_wcs))

twocolumn_figure(fig_ratio=0.95, font_scale=1.2)

ax = plt.subplot(111, projection=moment0_wcs)
im = ax.imshow(moment0_Kkm_s,
               origin='lower',
               interpolation='nearest',
               norm=ImageNormalize(vmin=-0.001,
                                   vmax=np.nanmax(moment0_Kkm_s),
                                   stretch=AsinhStretch()))
ax.set_ylabel("DEC (J2000)")
ax.set_xlabel("RA (J2000)")
ax.add_patch(beam.ellipse_to_plot(int(0.05 * moment0.shape[0]),
                                  int(0.05 * moment0.shape[1]), pixscale))

cbar = plt.colorbar(im)
cbar.set_label(r"Integrated Intensity (K km s$^{-1}$)")

plt.savefig(allfigs_path("zeroth_moment_map_14B088.pdf"))
plt.savefig(allfigs_path("zeroth_moment_map_14B088.png"))

plt.close()

ax = plt.subplot(111, projection=moment0_wcs)
im = ax.imshow(moment0_Kkm_s_feath,
               origin='lower',
               interpolation='nearest',
               norm=ImageNormalize(vmin=-0.001,
                                   vmax=np.nanmax(moment0_Kkm_s_feath),
                                   stretch=AsinhStretch()))
ax.set_ylabel("DEC (J2000)")
ax.set_xlabel("RA (J2000)")
ax.add_patch(beam.ellipse_to_plot(int(0.05 * moment0.shape[0]),
                                  int(0.05 * moment0.shape[1]), pixscale))

cbar = plt.colorbar(im)
cbar.set_label(r"Integrated Intensity (K km s$^{-1}$)")

plt.savefig(allfigs_path("zeroth_moment_map_14B088_feather.pdf"))
plt.savefig(allfigs_path("zeroth_moment_map_14B088_feather.png"))

plt.close()

# Make another zeroth moment map in HI (thin) column density
ax = plt.subplot(111, projection=moment0_wcs)
im = ax.imshow(moment0_coldens,
               origin='lower',
               interpolation='nearest',
               norm=ImageNormalize(vmin=-0.001 * hi_coldens_Kkms.value,
                                   vmax=np.nanmax(moment0_coldens),
                                   stretch=AsinhStretch()))
ax.set_ylabel("DEC (J2000)")
ax.set_xlabel("RA (J2000)")
ax.add_patch(beam.ellipse_to_plot(int(0.05 * moment0.shape[0]),
                                  int(0.05 * moment0.shape[1]), pixscale))

formatter = tkr.ScalarFormatter(useMathText=True)
formatter.set_scientific(True)
formatter.set_powerlimits((-2, 2))

cbar = plt.colorbar(im, format=formatter)
cbar.set_label(r"HI Column Density (cm$^{-2}$)")

plt.savefig(allfigs_path("coldens_map_14B088.pdf"))
plt.savefig(allfigs_path("coldens_map_14B088.png"))

plt.close()

ax = plt.subplot(111, projection=moment0_wcs)
im = ax.imshow(moment0_coldens_feath,
               origin='lower',
               interpolation='nearest',
               norm=ImageNormalize(vmin=-0.001 * hi_coldens_Kkms.value,
                                   vmax=np.nanmax(moment0_coldens_feath),
                                   stretch=AsinhStretch()))
ax.set_ylabel("DEC (J2000)")
ax.set_xlabel("RA (J2000)")
ax.add_patch(beam.ellipse_to_plot(int(0.05 * moment0.shape[0]),
                                  int(0.05 * moment0.shape[1]), pixscale))

formatter = tkr.ScalarFormatter(useMathText=True)
formatter.set_scientific(True)
formatter.set_powerlimits((-2, 2))

cbar = plt.colorbar(im, format=formatter)
cbar.set_label(r"HI Column Density (cm$^{-2}$)")

plt.savefig(allfigs_path("coldens_map_14B088_feather.pdf"))
plt.savefig(allfigs_path("coldens_map_14B088_feather.png"))

plt.close()

# Peak HI temperature.
ax = plt.subplot(111, projection=moment0_wcs)
im = ax.imshow(peaktemps,
               origin='lower',
               interpolation='nearest',
               norm=ImageNormalize(vmin=0,
                                   vmax=np.nanmax(peaktemps),
                                   stretch=AsinhStretch()))
ax.set_ylabel("DEC (J2000)")
ax.set_xlabel("RA (J2000)")
ax.add_patch(beam.ellipse_to_plot(int(0.05 * moment0.shape[0]),
                                  int(0.05 * moment0.shape[1]), pixscale))

cbar = plt.colorbar(im)
cbar.set_label(r"HI Peak Temperature (K)")

plt.savefig(allfigs_path("peaktemps_map_14B088.pdf"))
plt.savefig(allfigs_path("peaktemps_map_14B088.png"))

plt.close()

ax = plt.subplot(111, projection=moment0_wcs)
im = ax.imshow(peaktemps_feath,
               origin='lower',
               interpolation='nearest',
               norm=ImageNormalize(vmin=0,
                                   vmax=np.nanmax(peaktemps_feath),
                                   stretch=AsinhStretch()))
ax.set_ylabel("DEC (J2000)")
ax.set_xlabel("RA (J2000)")
ax.add_patch(beam.ellipse_to_plot(int(0.05 * moment0.shape[0]),
                                  int(0.05 * moment0.shape[1]), pixscale))

cbar = plt.colorbar(im)
cbar.set_label(r"HI Peak Temperature (K)")

plt.savefig(allfigs_path("peaktemps_map_14B088_feather.pdf"))
plt.savefig(allfigs_path("peaktemps_map_14B088_feather.png"))

plt.close()

moment1 = fits.open(fourteenB_HI_file_dict["Moment1"])[0]

ax = plt.subplot(111, projection=WCS(moment1.header))
im = ax.imshow(moment1.data / 1000.,
               origin='lower', vmin=-300, vmax=-70,
               interpolation='nearest', cmap='viridis')

ax.set_ylabel("DEC (J2000)")
ax.set_xlabel("RA (J2000)")

cbar = plt.colorbar(im)
cbar.set_label(r"Centroid Velocity (km s$^{-1}$)")

plt.savefig(allfigs_path("centroid_map_14B088.pdf"))
plt.savefig(allfigs_path("centroid_map_14B088.png"))

plt.close()

moment1_feath = fits.open(fourteenB_wGBT_HI_file_dict["Moment1"])[0]

ax = plt.subplot(111, projection=WCS(moment1.header))
im = ax.imshow(moment1_feath.data / 1000.,
               origin='lower', vmin=-300, vmax=-70,
               interpolation='nearest', cmap='viridis')

ax.set_ylabel("DEC (J2000)")
ax.set_xlabel("RA (J2000)")

cbar = plt.colorbar(im)
cbar.set_label(r"Centroid Velocity (km s$^{-1}$)")

plt.savefig(allfigs_path("centroid_map_14B088_feather.pdf"))
plt.savefig(allfigs_path("centroid_map_14B088_feather.png"))

plt.close()

ax = plt.subplot(111, projection=WCS(moment1.header))
im = ax.imshow((moment1_feath.data - moment1.data) / 1000.,
               origin='lower', vmin=-20, vmax=20,
               interpolation='nearest', cmap='seismic')

ax.set_ylabel("DEC (J2000)")
ax.set_xlabel("RA (J2000)")

cbar = plt.colorbar(im)
cbar.set_label(r"Difference in Centroid Velocity (km s$^{-1}$)")

plt.savefig(allfigs_path("centroid_map_14B088_feather_diff.pdf"))
plt.savefig(allfigs_path("centroid_map_14B088_feather_diff.png"))

plt.close()

default_figure()
