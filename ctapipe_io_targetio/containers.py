"""
Container structures for data that should be read or written to disk
"""
from ctapipe.core import Container, Field, Map
from ctapipe.io.containers import DataContainer

__all__ = [
    'TargetIODataContainer',
]


class TargetIOCameraContainer(Container):
    """
    Container for Fields that are specific to cameras that use TARGET
    """
    first_cell_ids = Field(None, ("numpy array of the first_cell_id of each"
                                  "waveform in the camera image (n_pixels)"))


class TargetIOContainer(Container):
    """
    Storage for the TargetIOCameraContainer for each telescope
    """

    tel = Field(Map(TargetIOCameraContainer),
                "map of tel_id to TargetIOCameraContainer")


class TargetIODataContainer(DataContainer):
    """
    Data container including targeto information
    """
    targetio = Field(TargetIOContainer(), "TARGET-specific Data")
