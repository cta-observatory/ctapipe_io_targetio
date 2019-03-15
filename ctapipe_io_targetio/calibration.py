from ctapipe.io import CameraR1Calibrator
from traitlets import Unicode
import numpy as np


class TargetIOR1Calibrator(CameraR1Calibrator):

    pedestal_path = Unicode(
        '',
        allow_none=True,
        help='Path to the TargetCalib pedestal file'
    ).tag(config=True)
    tf_path = Unicode(
        '',
        allow_none=True,
        help='Path to the TargetCalib Transfer Function file'
    ).tag(config=True)
    pe_path = Unicode(
        '',
        allow_none=True,
        help='Path to the TargetCalib pe conversion file'
    ).tag(config=True)
    ff_path = Unicode(
        '',
        allow_none=True,
        help='Path to a TargetCalib flat field file'
    ).tag(config=True)

    def __init__(self, config=None, parent=None, **kwargs):
        """
        The R1 calibrator for targetio files (i.e. files containing data
        taken with a TARGET module, such as with CHEC)

        Fills the r1 container.

        Parameters
        ----------
        config : traitlets.loader.Config
            Configuration specified by config file or cmdline arguments.
            Used to set traitlet values.
            Set to None if no configuration to pass.
        tool : ctapipe.core.Tool
            Tool executable that is calling this component.
            Passes the correct logger to the component.
            Set to None if no Tool to pass.
        kwargs
        """
        super().__init__(config=config, parent=parent, **kwargs)
        try:
            import target_calib
        except ImportError:
            msg = ("Cannot find target_calib module, please follow "
                   "installation instructions from https://forge.in2p3.fr/"
                   "projects/gct/wiki/Installing_CHEC_Software")
            self.log.error(msg)
            raise

        self._r1_wf = None
        self.tc = target_calib
        self.calibrator = None
        self.telid = 0

        self._load_calib()

    def calibrate(self, event):
        """
        Placeholder function to satisfy abstract parent, this is overloaded by
        either fake_calibrate or real_calibrate.
        """
        pass

    def _load_calib(self):
        """
        If a pedestal file has been supplied, create a target_calib
        Calibrator object. If it hasn't then point calibrate to
        fake_calibrate, where nothing is done to the waveform.
        """
        if self.pedestal_path:
            self.calibrator = self.tc.Calibrator(self.pedestal_path,
                                                 self.tf_path,
                                                 [self.pe_path, self.ff_path])
            self.calibrate = self.real_calibrate
        else:
            self.log.warning("No pedestal path supplied, "
                             "r1 samples will equal r0 samples.")
            self.calibrate = self.fake_calibrate

    def fake_calibrate(self, event):
        """
        Don't perform any calibration on the waveforms, just fill the
        R1 container.

        Parameters
        ----------
        event : `ctapipe` event-container
        """
        if event.meta['origin'] != 'targetio':
            raise ValueError('Using TargetioR1Calibrator to calibrate a '
                             'non-targetio event.')

        if self.check_r0_exists(event, self.telid):
            samples = event.r0.tel[self.telid].waveform
            event.r1.tel[self.telid].waveform = samples.astype('float32')

    def real_calibrate(self, event):
        """
        Apply the R1 calibration defined in target_calib and fill the
        R1 container.

        Parameters
        ----------
        event : `ctapipe` event-container
        """
        if event.meta['origin'] != 'targetio':
            raise ValueError('Using TargetioR1Calibrator to calibrate a '
                             'non-targetio event.')

        if self.check_r0_exists(event, self.telid):
            samples = event.r0.tel[self.telid].waveform
            if self._r1_wf is None:
                self._r1_wf = np.zeros(samples.shape, dtype=np.float32)
            fci = event.targetio.tel[self.telid].first_cell_ids
            self.calibrator.ApplyEvent(samples[0], fci, self._r1_wf[0])
            event.r1.tel[self.telid].waveform = self._r1_wf
