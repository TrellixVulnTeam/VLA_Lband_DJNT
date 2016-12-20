
from astropy.io import fits
from spectral_cube import SpectralCube
from spectral_cube.lower_dimensional_structures import OneDSpectrum
import astropy.units as u
import numpy as np
import os
from astropy.utils.console import ProgressBar
from itertools import izip, repeat
from turbustat.statistics.stats_utils import fourier_shift


def spectrum_shifter(spectrum, v0, vcent):
    '''
    Shift the central velocity of a spectrum by the difference if v0 and vcent.

    Parameters
    ----------
    spectrum : `~spectral_cube.lower_dimensional_objects.OneDSpectrum`
        1D spectrum to shift.
    v0 : `~astropy.units.Quantity`
        Velocity to shift spectrum to.
    vcent : `~astropy.units.Quantity`
        Initial center velocity of the spectrum.
    '''

    vdiff = np.abs(spectrum.spectral_axis[1] - spectrum.spectral_axis[0])
    vel_unit = vdiff.unit

    pix_shift = (vcent.to(vel_unit) - v0.to(vel_unit)) / vdiff

    shifted = fourier_shift(spectrum, pix_shift)

    if hasattr(spectrum, "beams"):
        beams = spectrum.beams
    else:
        beams = None

    return OneDSpectrum(shifted, unit=spectrum.unit, wcs=spectrum.wcs,
                        meta=spectrum.meta, spectral_unit=vel_unit,
                        beams=beams)


def mulproc_spectrum_shifter(inputs):
    y, x, cube, vcent, v0 = inputs

    return spectrum_shifter(cube[:, y, x], v0, vcent[y, x]), y, x


def cube_shifter(cube, velocity_surface, v0=None, save_shifted=False,
                 save_name=None, xy_posns=None, pool=None,
                 return_spectra=True, chunk_size=20000,
                 verbose=False):
    '''
    Shift spectra in a cube according to a given velocity surface (peak
    velocity, centroid, rotation model, etc.).
    '''

    if not save_shifted and not return_spectra:
        raise Exception("One of 'save_shifted' or 'return_spectra' must be "
                        "enabled.")

    if not np.isfinite(velocity_surface).any():
        raise Exception("velocity_surface contains no finite values.")

    if xy_posns is None:
        # Only compute where a shift can be found
        xy_posns = np.where(np.isfinite(velocity_surface))

    if v0 is None:
        # Set to near the center velocity of the cube if not given.
        v0 = cube.spectral_axis[cube.shape[0] // 2]
    else:
        if not isinstance(v0, u.Quantity):
            raise u.UnitsError("v0 must be a quantity.")
        spec_unit = cube.spectral_axis.unit
        if not v0.unit.is_equivalent(spec_unit):
            raise u.UnitsError("v0 must have units equivalent to the cube's"
                               " spectral unit ().".format(spec_unit))

    # Adjust the header to have velocities centered at v0.
    new_header = cube.header.copy()
    new_header["CRVAL3"] = new_header["CRVAL3"] - v0.to(u.m / u.s).value

    if save_shifted:
        # execfile(os.path.expanduser("~/Dropbox/code_development/ewky_scripts/write_huge_fits.py"))

        if os.path.exists(save_name):
            raise Exception("The file name {} already "
                            "exists".format(save_name))

        create_huge_fits(save_name, new_header)

        output_fits = fits.open(save_name, mode='update')

    if return_spectra:
        all_shifted_spectra = []
        out_posns = []

    # Create chunks of spectra for read-out.
    nchunks = 1 + xy_posns[0].size // chunk_size

    if verbose:
        iterat = ProgressBar(xrange(nchunks))
    else:
        iterat = xrange(nchunks)

    for i in iterat:

        y_posns = xy_posns[0][i * chunk_size:(i + 1) * chunk_size]
        x_posns = xy_posns[1][i * chunk_size:(i + 1) * chunk_size]

        gen = izip(y_posns, x_posns, repeat(cube), repeat(velocity_surface),
                   repeat(v0))

        if pool is not None:
            shifted_spectra = pool.map(mulproc_spectrum_shifter, gen)
        else:
            shifted_spectra = map(mulproc_spectrum_shifter, gen)

        if save_shifted:
            for out in shifted_spectra:
                output_fits[0].data[:, out[1], out[2]] = out[0].value

            output_fits.flush()

        if return_spectra:
            all_shifted_spectra.extend([out[0] for out in shifted_spectra])
            out_posns.extend([out[1:] for out in shifted_spectra])

    if pool is not None:
        pool.close()
        pool.join()

    if save_shifted:
        output_fits.flush()
        output_fits.close()

    if return_spectra:
        return all_shifted_spectra, out_posns


def create_huge_fits(filename, header, shape=None):

    header.tofile(filename)

    if shape is None:
        try:
            shape = tuple(header['NAXIS{0}'.format(ii)] for ii in
                          range(1, header['NAXIS'] + 1))
        except KeyError:
            raise KeyError("header does not contain the NAXIS keywords. Need "
                           "to provide a shape.")
    with open(filename, 'rb+') as fobj:
        fobj.seek(len(header.tostring()) + (np.product(shape) *
                                            np.abs(header['BITPIX'] // 8)) - 1)
        fobj.write(b'\0')


def write_huge_fits(cube, filename, verbose=True, dtype=">f4"):
    '''
    Write a SpectralCube to a massive FITS file. Currently only 3D objects
    will work. A more general approach where the longest axis is iterated over
    is probably a good idea.

    cube : np.ndarray or SpectralCube
        Data to be written.

    filename : str
        Name of the FITS file to write to. If it does not already exist,
        `create_huge_fits` is called first to create an empty FITS file.
    '''

    if not os.path.exists(filename):
        create_huge_fits(filename, cube.header)

    # Open the FITS and write the values out channel-by-channel
    hdu = fits.open(filename, mode='update')

    nchans = cube.shape[0]

    if verbose:
        iterat = ProgressBar(nchans)
    else:
        iterat = xrange(nchans)

    for i in iterat:
        hdu[0].data[i, :, :] = cube[i, :, :].value.astype(dtype)
        hdu.flush()

    # And write the header
    hdu[0].header = cube.header
    hdu.flush()

    hdu.close()
