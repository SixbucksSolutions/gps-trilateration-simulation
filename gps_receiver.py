import numpy
import numpy.typing


# This is only used to compute initial pseudorange, need to calculate actual signal propagation delay
#   for pseudoranges -- never exposed outside of this file
actual_receiver_ecef_pos: numpy.typing.NDArray[numpy.float64] = numpy.array(
    [
         1_088_598.0,
        -4_853_018.0,
         3_979_796.0,
    ]
)
