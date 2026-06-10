import random

import numpy
import numpy.linalg
import numpy.typing





satellite_prn_numbers: list[str] = ["02", "07", "13", "19"]



def satellite_ecef_positions() -> numpy.typing.NDArray:
    return _satellite_positions


def satellite_pseudoranges(clock_bias_seconds: float,
                           satellite_positions: numpy.typing.NDArray,
                           fixed_ionospheric_delay_seconds: float | None = None,
                           fixed_tropospheric_delay_seconds: float | None = None) -> numpy.typing.NDArray:

    clock_bias_meters: float = clock_bias_seconds * SPEED_OF_LIGHT_M_PER_S

    if not -0.001 <= clock_bias_seconds <= 0.001:
        raise ValueError(f"Clock bias must be between -0.001 and +0.001 seconds to let least squares find a solution")

    if fixed_ionospheric_delay_seconds is not None:
        # print(f"Using fixed ionospheric delay of {fixed_ionospheric_delay_seconds:.09f} seconds")
        ionospheric_delays_meters: numpy.typing.NDArray = numpy.full(
            4, fixed_ionospheric_delay_seconds * SPEED_OF_LIGHT_M_PER_S)
    else:
        # Random values for each satellite, 1 - 200 ns
        ionospheric_delays_meters: numpy.typing.NDArray = numpy.array(
            [ ((random.random() * 0.000_000_199) + 0.000_000_001) * SPEED_OF_LIGHT_M_PER_S for _ in range(4) ]
        )

    if fixed_tropospheric_delay_seconds is not None:
        # print(f"Using fixed ionospheric delay of {fixed_ionospheric_delay_seconds:.09f} seconds")
        tropospheric_delays_meters: numpy.typing.NDArray = numpy.full(
            4, fixed_tropospheric_delay_seconds * SPEED_OF_LIGHT_M_PER_S)
    else:
        # Random values for each satellite, 1 - 50 ns
        tropospheric_delays_meters: numpy.typing.NDArray = numpy.array(
            [ ((random.random() * 0.000_000_049) + 0.000_000_001) * SPEED_OF_LIGHT_M_PER_S for _ in range(4) ]
        )

    # Compute vector differences (subtract ACTUAL receiver position from each satellite)
    delta_vectors: numpy.typing.NDArray = satellite_positions - _actual_receiver_ecef_pos

    # Compute true geometric range (L2 Euclidean norm along the row axis, calculates length of vector)
    geometric_ranges: numpy.typing.NDArray = numpy.linalg.norm(delta_vectors, axis=1)

    # Add all obfuscation variables (delays & receiver clock bias) in meters to produce
    #   realistically noisy  pseudoranges
    raw_measured_pseudoranges: numpy.typing.NDArray = (geometric_ranges +
                                                       ionospheric_delays_meters +
                                                       tropospheric_delays_meters +
                                                       clock_bias_meters)

    return raw_measured_pseudoranges


def fix_error_position_meters(fix_position: numpy.typing.NDArray) -> float:
    return float(numpy.linalg.norm(_actual_receiver_ecef_pos - fix_position))
