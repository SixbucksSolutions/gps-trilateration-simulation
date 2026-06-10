import numpy
import numpy.typing


# 3D ECEF positions of 4 GPS satellites all visible from Fairfax County, Virginia, USA
# at 2026-06-01 00:00:00Z (units: meters)
#
# These represent known coordinates extracted from the satellite ephemeris data
gps_satellite_positions_by_svn: dict[int, numpy.typing.NDArray[numpy.float64]] = {
     2: numpy.array([12_450_000.000, -18_340_000.000,  16_120_000.000]),
     7: numpy.array([-8_420_000.000, -22_110_000.000,  11_430_000.000]),
    13: numpy.array([ 5_120_000.000, -24_150_000.000,  -8_210_000.000]),
    19: numpy.array([15_430_000.000, -11_240_000.000, -17_210_000.000]),
}
