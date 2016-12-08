
from astropy.io import fits
from spectral_cube import SpectralCube
import astropy.units as u
import numpy as np
import os
from astropy.utils.console import ProgressBar
from astropy.table import Table

from turbustat.statistics.stats_utils import fourier_shift

from analysis.paths import fourteenB_HI_data_path

from analysis.constants import (rotsub_cube_name, cube_name, mask_name,
                                rotsub_mask_name)

'''
Subtract a rotation model from a cube.
'''

# Load in my huge FITS creator
execfile(os.path.expanduser("~/Dropbox/code_development/ewky_scripts/write_huge_fits.py"))

cube = SpectralCube.read(fourteenB_HI_data_path(cube_name))
mask = fits.open(fourteenB_HI_data_path(mask_name))[0]

model = fits.open(fourteenB_HI_data_path("diskfit_noasymm_noradial_nowarp_output/rad.fitmod.fits"))

# Load in the fit results for the galaxy parameters to get vsys
table_name = fourteenB_HI_data_path("diskfit_noasymm_noradial_nowarp_output/rad.out.params.csv")
tab = Table.read(table_name)

vsys = (float(tab["Vsys"]) * u.km / u.s).to(u.m / u.s)

# Now calculate the spectral shifts needed for each pixel
# Assuming that the array shapes for the same (which they are here)
shifts = np.zeros(model[0].data.shape)

posns = list(np.where(np.isfinite(model[0].data)))
posns[0] = posns[0][::-1]
posns[1] = posns[1][::-1]
# Adjust the header
new_header = cube.header.copy()
# There's a 1 pixel offset
# new_header["CRPIX3"] = center_pixel + 1
new_header["CRVAL3"] = new_header["CRVAL3"] - vsys.value

# Create the FITS file so we can write 1 spectrum in at a time
print("Making the empty FITS file")
new_fitsname = fourteenB_HI_data_path(rotsub_cube_name, no_check=True)

create_huge_fits(new_fitsname, new_header)

new_fits = fits.open(new_fitsname, mode='update')

write_every = 10000

vel_res = cube._pix_size_slice(0) * u.m / u.s

print("And here we go!")
for num, (i, j) in enumerate(ProgressBar(zip(*posns))):
    # Don't bother rolling if there's nothing there
    if not np.isfinite(cube.filled_data[:, i, j]).any():
        continue

    shift = ((model[0].data[i, j] * u.m / u.s - vsys) / vel_res).value

    new_fits[0].data[:, i, j] = \
        fourier_shift(cube.filled_data[:, i, j], shift)

    # Now shift the source mask by the same amount
    # Gibbs ringing occurs at the edges, but the amplitudes will not
    # exceed 0.5. The rounding may cause a difference os +/- on pixel
    # one the edge of the valid regions.
    mask.data[:, i, j] = \
        (fourier_shift(mask.data[:, i, j], shift) > 0.5).astype(np.int)

    if num % write_every == 0:
        new_fits.flush()

# Save the rotation subtracted mask
new_mask_hdu = fits.PrimaryHDU(mask.data, header=mask.header)
new_mask_hdu.writeto(fourteenB_HI_data_path(rotsub_mask_name, no_check=True),
                     clobber=True)

# Append the beam table
hdu = fits.open(fourteenB_HI_data_path(cube_name))
new_fits.append(hdu[1])

new_fits.flush()
new_fits.close()

hdu.close()
