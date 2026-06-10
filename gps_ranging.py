import argparse
import json
import logging
import random
import time
import typing

import numpy
import numpy.linalg
import numpy.typing

import gps_gold_codes
import gps_ephemeris
import gps_receiver


_logger = logging.getLogger("gps_ranging")
_logger.setLevel(logging.DEBUG)


SPEED_OF_LIGHT_M_PER_S: float = 299_792_458.0


def compute_pseudorange_from_receiver_to_svn_meters(svn_num: int,
                                                    ionosphere_delay_seconds: float | None,
                                                    tropospheric_delay_seconds: float | None) -> float:

    # Normalization gets _length_ of vector
    actual_transmission_delay_meters: float = float(
        numpy.linalg.norm(
            gps_ephemeris.gps_satellite_positions_by_svn[svn_num] - gps_receiver.actual_receiver_ecef_pos
        )
    )

    computed_pseudorange_meters: float

    # Add in atmospheric delays
    atmospheric_delays: float = 0.0
    if ionosphere_delay_seconds is None:
        ionosphere_delay_seconds = float(random.randint(1, 1601)) * 0.000_000_001
        # _logger.debug(f" Random ionospheric delay : {ionosphere_delay_seconds:.09f} s")

    if tropospheric_delay_seconds is None:
        tropospheric_delay_seconds = float(random.randint(8, 101)) * 0.000_000_001
        # _logger.debug(f"Random tropospheric delay : {tropospheric_delay_seconds:.09f} s")

    computed_pseudorange_meters: float = actual_transmission_delay_meters + (
            (ionosphere_delay_seconds + tropospheric_delay_seconds) * SPEED_OF_LIGHT_M_PER_S
    )

    _logger.debug(f"SVN {svn_num:02d} pseudorange: {computed_pseudorange_meters:,.02f} m = "
                  f"{actual_transmission_delay_meters:,.02f} (actual) + " 
                  f"{ionosphere_delay_seconds * SPEED_OF_LIGHT_M_PER_S:6.02f} (ionospheric) + "
                  f"{tropospheric_delay_seconds * SPEED_OF_LIGHT_M_PER_S:5.02f} (tropospheric)"
    )

    return computed_pseudorange_meters


def _parse_args() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Trilateration demo for GPS")
    parser.add_argument("-b", "--prn-listen-offset-milliseconds", type=int,
                        # Random -1 .. +1 ms
                        default=random.randint(0, 999),
                        help="PRN sniff millisecond offset (0 .. 999 ms) (default: random)")
    parser.add_argument("-i", "--ionosphere-delay-seconds", type=float,
                        help="Fixed ionospheric propagation delay (typical: 0.0000000007 - 0.000001600 s / "
                             "0.7 - 1,600 ns)"
                             "(default: random per satellite)")
    parser.add_argument("-t", "--troposphere-delay-seconds", type=float,
                        help="Fixed tropospheric propagation delay (typical: 0.000000008 - 0.000000100 s / "
                             "8 - 100 ns)"
                             "(default: random per satellite)")
    return parser.parse_args()


def _svn_prn_stream(args: argparse.Namespace, svn_num: int,
                    prn_listen_offset_milliseconds: int,
                    fix_svn_prns: dict[int, numpy.typing.NDArray[numpy.int8]]) -> numpy.typing.NDArray[numpy.int8]:

    # Calculate a noisy pseudorange in meters from our _actual_ receiver position to the satellite
    computed_pseudorange: float = compute_pseudorange_from_receiver_to_svn_meters(svn_num,
                                                                                  args.ionosphere_delay_seconds,
                                                                                  args.troposphere_delay_seconds)



def _main() -> None:
    args: argparse.Namespace = _parse_args()

    print()

    # Populate the gold codes for the satellites we're simulating a lock to
    print("Generating GPS Gold codes for satellites in our position fix")
    gold_codes: gps_gold_codes.GPSGoldCodes = gps_gold_codes.GPSGoldCodes()
    fix_svn_prns: dict[int, numpy.typing.NDArray[numpy.int8]] = {}
    for svn_num in (2, 7, 13, 19):
        fix_svn_prns[svn_num] = gold_codes.gold_code(svn_num)
    print("\tDone!")

    print()
    print("\"Listening\" to PRN stream from our four satellites for two full PRN repetitions (2 ms)")
    sniffed_prn_streams_by_svn: dict[int, numpy.typing.NDArray[numpy.int8]] = {}
    for svn_num in (2, 7, 13, 19):
        sniffed_prn_streams_by_svn[svn_num] = _svn_prn_stream(args, svn_num, args.prn_listen_offset_milliseconds,
                                                              fix_svn_prns)

    print("\tDone!")

    print()


if __name__ == "__main__":
    logging.basicConfig()
    _main()
