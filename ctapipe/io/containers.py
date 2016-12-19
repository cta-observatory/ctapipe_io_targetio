"""
Container structures for data that should be read or written to disk
"""

from astropy import units as u
from astropy.time import Time

from ..core import Container, Item, Map
from numpy import ndarray

__all__ = ['DataContainer', 'RawDataContainer', 'RawCameraContainer',
           'MCEventContainer', 'MCCameraEventContainer',
           'CalibratedCameraContainer',
           'ReconstructedShowerContainer',
           'ReconstructedEnergyContainer',
           'ParticleClassificationContainer',
           'ReconstructedContainer']

# todo: change some of these Maps to be just 3D NDarrays?


class InstrumentContainer(Container):
    """Storage of header info that does not change with event. This is a
    temporary hack until the Instrument module and database is fully
    implemented.  Eventually static information like this will not be
    part of the data stream, but be loaded and accessed from
    functions.

    """

    pixel_pos = Item(Map(ndarray), "map of tel_id to pixel positions")
    optical_foclen = Item(Map(ndarray), "map of tel_id to focal length")
    mirror_dish_area = Item(Map(float), "map of tel_id to the area of the mirror dish", unit=u.m**2)
    mirror_numtiles = Item(Map(int), "map of tel_id to the number of tiles for the mirror")
    tel_pos = Item(Map(ndarray), "map of tel_id to telescope position")
    num_pixels = Item(Map(int), "map of tel_id to number of pixels in camera")
    num_samples = Item(Map(int), "map of tel_id to number of time samples")
    num_channels = Item(Map(int), "map of tel_id to number of channels")


class CalibratedCameraContainer(Container):
    """Storage of output of camera calibrationm e.g the final calibrated
    image in intensity units and other per-event calculated
    calibration information.
    """
    calibrated_image = Item(0, "array of camera image", unit=u.electron)
    integration_window = Item(Map(), ("map per channel of bool ndarrays of "
                                      "shape (npix, nsamples) "
                                      "indicating the samples used in "
                                      "the obtaining of the charge, dependant "
                                      "on the integration method used"))
    # todo: rename the following to *_image
    pedestal_subtracted_adc = Item(Map(), ("Map of channel to subtracted "
                                           "ADC image"))
    peakpos = Item(Map(), ("position of the peak as determined by the "
                           "peak-finding algorithm for each pixel"
                           " and channel"))


class CameraCalibrationContainer(Container):
    """
    Storage of externally calculated calibration parameters (not per-event)
    """
    dc_to_pe = Item(None, "DC/PE calibration arrays from MC file")
    pedestal = Item(None, "pedestal calibration arrays from MC file")


class CalibratedContainer(Container):
    """ Calibrated Camera Images and associated data"""
    tel = Item(Map(CalibratedCameraContainer),
               "map of tel_id to CalibratedCameraContainer")


class RawCameraContainer(Container):
    """
    Storage of raw data from a single telescope
    """
    adc_sums = Item(Map(), ("map of channel to (masked) arrays of all "
                            "integrated ADC data (n_pixels)"))
    adc_samples = Item(Map(), ("map of channel to arrays of "
                               "(n_pixels, n_samples)"))


class RawDataContainer(Container):
    """
    Storage of a Merged Raw Data Event
    """

    run_id = Item(-1, "run id number")
    event_id = Item(-1, "event id number")
    tels_with_data = Item([], "list of telescopes with data")
    tel = Item(Map(RawCameraContainer), "map of tel_id to RawCameraContainer")


class MCCameraEventContainer(Container):
    """
    Storage of mc data for a single telescope that change per event
    """
    photo_electron_image = Item(Map(), ("reference image in pure photoelectrons,"
                                        " with no noise"))
    # todo: move to instrument (doesn't change per event)
    reference_pulse_shape = Item(Map(), ("map of channel to array "
                                         "defining pulse shape"))
    # todo: move to instrument or a static MC container (don't change per
    # event)
    time_slice = Item(0, "width of time slice", unit=u.ns)
    dc_to_pe = Item(None, "DC/PE calibration arrays from MC file")
    pedestal = Item(None, "pedestal calibration arrays from MC file")
    azimuth_raw = Item(0, "Raw azimuth angle [radians from N->E] "
                          "for the telescope")
    altitude_raw = Item(0, "Raw altitude angle [radians] for the telescope")
    azimuth_cor = Item(0, "the tracking Azimuth corrected for pointing "
                             "errors for the telescope")
    altitude_cor = Item(0, "the tracking Altitude corrected for pointing "
                              "errors for the telescope")


class MCEventContainer(Container):
    """
    Monte-Carlo
    """
    energy = Item(0, "Monte-Carlo Energy")
    alt = Item(0, "Monte-carlo altitude", unit=u.deg)
    az = Item(0, "Monte-Carlo azimuth", unit=u.deg)
    core_x = Item(0, "MC core position")
    core_y = Item(0, "MC core position")
    h_first_int = Item(0, "Height of first interaction")
    tel = Item(Map(MCCameraEventContainer),
               "map of tel_id to MCCameraEventContainer")


class MCHeaderContainer(Container):
    """
    Monte-Carlo information that doesn't change per event
    """
    run_array_direction = Item([], "the tracking/pointing direction in "
                                   "[radians]. Depending on 'tracking_mode' "
                                   "this either contains: "
                                   "[0]=Azimuth, [1]=Altitude in mode 0, "
                                   "OR "
                                   "[0]=R.A., [1]=Declination in mode 1.")


class CentralTriggerContainer(Container):

    gps_time = Item(Time, "central average time stamp")
    tels_with_trigger = Item([], "list of telescopes with data")


class ReconstructedShowerContainer(Container):
    """
    Standard output of algorithms reconstructing shower geometry
    """

    alt = Item(0.0, "reconstructed altitude", unit=u.deg)
    alt_uncert = Item(0.0, "reconstructed altitude uncertainty", unit=u.deg)
    az = Item(0.0, "reconstructed azimuth", unit=u.deg)
    az_uncert = Item(0.0, 'reconstructed azimuth uncertainty', unit=u.deg)
    core_x = Item(0.0, 'reconstructed x coordinate of the core position',
                  unit=u.m)
    core_y = Item(0.0, 'reconstructed y coordinate of the core position',
                  unit=u.m)
    core_uncert = Item(0.0, 'uncertainty of the reconstructed core position',
                       unit=u.m)
    h_max = Item(0.0, 'reconstructed height of the shower maximum')
    h_max_uncert = Item(0.0, 'uncertainty of h_max')
    is_valid = (False, ('direction validity flag. True if the shower direction'
                        'was properly reconstructed by the algorithm'))
    tel_ids = Item([], ('list of the telescope ids used in the'
                        ' reconstruction of the shower'))
    average_size = Item(0.0, 'average size of used')
    goodness_of_fit = Item(0.0, 'measure of algorithm success (if fit)')


class ReconstructedEnergyContainer(Container):
    """
    Standard output of algorithms estimating energy
    """
    energy = Item(-1.0, 'reconstructed energy', unit=u.TeV)
    energy_uncert = Item(-1.0, 'reconstructed energy uncertainty', unit=u.TeV)
    is_valid = Item(False, ('energy reconstruction validity flag. True if '
                            'the energy was properly reconstructed by the '
                            'algorithm'))
    tel_ids = Item([], ('array containing the telescope ids used in the'
                        ' reconstruction of the shower'))
    goodness_of_fit = Item(0.0, 'goodness of the algorithm fit')


class ParticleClassificationContainer(Container):
    """
    Standard output of gamma/hadron classification algorithms
    """
    # TODO: Do people agree on this? This is very MAGIC-like.
    # TODO: Perhaps an integer classification to support different classes?
    # TODO: include an error on the prediction?
    prediction = Item(0.0, ('prediction of the classifier, defined between '
                            '[0,1], where values close to 0 are more gamma-like,'
                            ' and values close to 1 more hadron-like'))
    is_valid = Item(False, ('classificator validity flag. True if the predition '
                            'was successful within the algorithm validity range'))

    # TODO: KPK: is this different than the list in the reco
    # container? Why repeat?
    tel_ids = Item([], ('array containing the telescope ids used '
                        'in the reconstruction of the shower'))
    goodness_of_fit = Item(0.0, 'goodness of the algorithm fit')


class ReconstructedContainer(Container):
    """ collect reconstructed shower info from multiple algorithms """

    shower = Item(Map(ReconstructedShowerContainer),
                  "Map of algorithm name to shower info")
    energy = Item(Map(ReconstructedEnergyContainer),
                  "Map of algorithm name to energy info")
    classification = Item(Map(ParticleClassificationContainer),
                          "Map of algorithm name to classification info")


class DataContainer(Container):
    """ Top-level container for all event information """

    dl0 = Item(RawDataContainer(), "Raw Data")
    dl1 = Item(CalibratedContainer())
    dl2 = Item(ReconstructedContainer(), "Reconstructed Shower Information")
    mc = Item(MCEventContainer(), "Monte-Carlo data")
    mcheader = Item(MCHeaderContainer, "Monte-Carlo run header data")
    trig = Item(CentralTriggerContainer(), "central trigger information")
    count = Item(0, "number of events processed")
    inst = Item(InstrumentContainer(), "instrumental information (deprecated")


class MuonRingParameter(Container):
    """
    Storage of muon ring fit output

    Parameters
    ----------

    run_id : int
        run number
    event_id : int
        event number
    tel_id : int
        telescope ID
    ring_center_x, ring_center_y, ring_radius:
        center position and radius of the fitted ring
    ring_chi2_fit:
        chi squared of the ring fit
    ring_cov_matrix:
        covariance matrix of ring parameters
    """

    #def __init__(self, name="MuonRingParameter"):
        #super().__init__(name)
    run_id = Item(0, "run identification number")
    event_id = Item(0,"event identification number")
    tel_id = Item(0, 'telescope identification number')
    ring_center_x = Item(0.0, 'centre (x) of the fitted muon ring')
    ring_center_y = Item(0.0, 'centre (y) of the fitted muon ring')
    ring_radius = Item(0.0, 'radius of the fitted muon ring')
    ring_chi2_fit = Item(0.0, 'chisquare of the muon ring fit')
    ring_cov_matrix = Item(0.0, 'covariance matrix of the muon ring fit')
    ring_fit_method = Item("", 'fitting method used for the muon ring')
    inputfile = Item("", 'input file')


class MuonIntensityParameter(Container):
    """
    Storage of muon intensity fit output

    Parameters
    ----------

    run_id : int
        run number
    event_id : int
        event number
    tel_id : int
        telescope ID
    impact_parameter: float
        reconstructed impact parameter
    impact_parameter_chi2:
        chi squared impact parameter
    intensity_cov_matrix:
        Covariance matrix of impact parameters or alternatively:
        full 5x5 covariance matrix for the complete fit (ring + impact)
    impact_parameter_pos_x, impact_parameter_pos_y:
        position on the mirror of the muon impact
    COG_x, COG_y:
        center of gravity
    optical_efficiency_muon:
        optical muon efficiency from intensity fit
    ring_completeness:
        completeness of the ring
    ring_num_pixel: int
        Number of pixels composing the ring
    ring_size:
        ring size
    off_ring_size:
        size outside of the ring
    ring_width:
        ring width
    ring_time_width:
        standard deviation of the photons time arrival

    prediction: dict
        ndarray of the predicted charge in all pixels
    mask:
        ndarray of the mask used on the image for fitting

    """

    #def __init__(self, name="MuonIntensityParameter"):
        #super().__init__(name)
    run_id = Item(0, 'run identification number')
    event_id = Item(0, 'event identification number')
    tel_id = Item(0, 'telescope identification number')
    ring_completeness = Item(0., 'fraction of ring present')
    ring_num_pixel = Item(0, 'number of pixels in the ring image')
    ring_size = Item(0.,'size of the ring in pe')
    off_ring_size = Item(0., 'image size outside of ring in pe')
    ring_width = Item(0., 'width of the muon ring in degrees')
    ring_time_width = Item(0., 'duration of the ring image sequence')
    impact_parameter = Item(0., 'distance of muon impact position from centre of mirror')
    impact_parameter_chi2 = Item(0., 'impact parameter chi squared')
    intensity_cov_matrix = Item(0., 'covariance matrix of intensity')
    impact_parameter_pos_x = Item(0., 'impact parameter x position')
    impact_parameter_pos_y = Item(0., 'impact parameter y position')
    COG_x = Item(0.0, 'Centre of Gravity x')
    COG_y = Item(0.0, 'Centre of Gravity y')
    prediction = Item([],'image prediction')
    mask = Item([],'image pixel mask')
    optical_efficiency_muon = Item(0.,'optical efficiency muon')
    intensity_fit_method = Item("",'intensity fit method')
    inputfile = Item("",'input file')
