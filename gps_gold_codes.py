import logging
import typing

import numpy
import numpy.typing


_logger = logging.getLogger("gps_gold_codes")
_logger.setLevel(logging.INFO)


class GPSGoldCodes:

    # Official G2 tap selections for PRN 1 through 32
    # (1-indexed to match PRN numbers)
    _PRN_TAPS: dict[int, tuple[int]] = {
         1: (2,  6),  2: (3,  7),  3: (4, 8),  4: (5,  9),
         5: (1,  9),  6: (2, 10),  7: (1, 8),  8: (2,  9),
         9: (3, 10), 10: (2,  3), 11: (3, 4), 12: (5,  6),
        13: (6,  7), 14: (7,  8), 15: (8, 9), 16: (9, 10),
        17: (1,  4), 18: (2,  5), 19: (3, 6), 20: (4,  7),
        21: (5,  8), 22: (6,  9), 23: (1, 3), 24: (4,  6),
        25: (5,  7), 26: (6,  8), 27: (7, 9), 28: (8, 10),
        29: (1,  6), 30: (2,  7), 31: (3, 8), 32: (4,  9),
    }


    def __init__(self: typing.Self):
        self._gps_gold_codes_cache: dict[int, numpy.typing.NDArray] = {}


    def gold_code(self: typing.Self, prn_num: int) -> numpy.typing.NDArray:
        if prn_num not in GPSGoldCodes._PRN_TAPS:
            raise ValueError(f"PRN must be an integer between 1 and 32.")

        if prn_num not in self._gps_gold_codes_cache:
            _logger.debug(f"Cache miss for PRN {prn_num}, generating and adding to cache")
            self._gps_gold_codes_cache[prn_num] = GPSGoldCodes._generate_ca_code(prn_num)

        return self._gps_gold_codes_cache[prn_num]


    @classmethod
    def _generate_ca_code(cls, prn: int) -> numpy.typing.NDArray:
        """
        Generates the 1023-bit C/A code for a given GPS PRN (1 to 32).
        Returns a NumPy array of 1s and 0s.
        """
        if prn not in cls._PRN_TAPS:
            raise ValueError(f"PRN {prn} must be an integer between 1 and 32.")

        taps = cls._PRN_TAPS[prn]

        # Initialize shift registers G1 and G2 with all ones
        g1 = numpy.ones(10, dtype=numpy.int8)
        g2 = numpy.ones(10, dtype=numpy.int8)

        ca_code = numpy.zeros(1023, dtype=numpy.int8)

        for i in range(1023):
            # 1. Output bit of G1 is the last element (index 9)
            g1_out = g1[9]

            # 2. Output bit of G2 is the XOR of the specified taps
            # Convert 1-based tap index to 0-based Python array index
            g2_out = g2[taps[0] - 1] ^ g2[taps[1] - 1]

            # 3. The final C/A code bit is the XOR of G1 and G2 outputs
            ca_code[i] = g1_out ^ g2_out

            # 4. Calculate feedback for G1 feedback loop: polynomial 1 + x^3 + x^10
            g1_feedback = g1[2] ^ g1[9]

            # 5. Calculate feedback for G2 feedback loop: polynomial 1 + x^2 + x^3 + x^6 + x^8 + x^9 + x^10
            g2_feedback = g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]

            # 6. Shift the registers to the right and insert the feedback bit at the front
            g1 = numpy.roll(g1, 1)
            g1[0] = g1_feedback

            g2 = numpy.roll(g2, 1)
            g2[0] = g2_feedback

        return ca_code


# --- Example Execution ---
if __name__ == "__main__":
    logging.basicConfig()
    gold_codes = GPSGoldCodes()

    code = gold_codes.gold_code(1)
    print(code)