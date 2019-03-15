from ctapipe.utils.datasets import get_dataset_path
from numpy.testing import assert_array_equal, assert_array_almost_equal


def test_targetio_calibrator():
    from ctapipe_io_targetio import TargetIOEventSource
    from ctapipe.calib import CameraR1Calibrator

    url_r0 = get_dataset_path("targetmodule_r0.tio")
    url_r1 = get_dataset_path("targetmodule_r1.tio")
    pedpath = get_dataset_path("targetmodule_ped.tcal")

    source_r0 = TargetIOEventSource(input_url=url_r0)
    source_r1 = TargetIOEventSource(input_url=url_r1)

    r1c = CameraR1Calibrator.from_eventsource(eventsource=source_r0)

    event_r0 = source_r0._get_event_by_index(0)
    event_r1 = source_r1._get_event_by_index(0)

    r1c.calibrate(event_r0)
    assert_array_equal(event_r0.r0.tel[0].waveform,
                       event_r0.r1.tel[0].waveform)

    r1c = CameraR1Calibrator.from_eventsource(
        eventsource=source_r0,
        pedestal_path=pedpath
    )
    r1c.calibrate(event_r0)
    assert_array_almost_equal(
        event_r0.r1.tel[0].waveform,
        event_r1.r1.tel[0].waveform,
        1,
    )
