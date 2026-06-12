import datetime
import json
import logging
import typing


class SimTime:

    class UserClock:

        def __init__(self: typing.Self,
                     clock_name: str,
                     initial_clock: datetime.datetime | datetime.time,
                     logging_level: int = logging.WARNING) -> None:

            self.clock_name: str = clock_name
            self._time_initial: datetime.datetime

            if isinstance(initial_clock, datetime.datetime):
                self._time_initial = initial_clock
            elif isinstance(initial_clock, datetime.time):
                self._time_initial = datetime.datetime.combine(
                    datetime.date.fromisoformat("1970-01-01"),
                    initial_clock
                )
            else:
                raise ValueError("Initial clock must be of type datetime.datetime or datetime.time")

            self._time_current: datetime.datetime = self._time_initial
            self._logger = logging.getLogger(f"sim_time.{clock_name}")
            self._logger.setLevel(logging_level)


        def advance_clock(self: typing.Self, advance_amount) -> None:
            self._time_current += advance_amount
            self._logger.debug(f"Time advanced by {SimTime.timedelta_isoformat(advance_amount)} s, "
                               f"now at {self._time_current.isoformat(sep=" ", timespec="microseconds")}")


        def time_current(self: typing.Self) -> datetime.datetime:
            return self._time_current


        def time_elapsed(self: typing.Self) -> datetime.timedelta:
            return self._time_current - self._time_initial


    # No need to call this constructor on every advance time call, set it and forget it
    _zero_delta: datetime.timedelta = datetime.timedelta()

    # Class level logger
    _logger: logging.Logger = logging.getLogger("sim_time")


    @classmethod
    def timedelta_isoformat(cls, time_delta: datetime.timedelta) -> str:
        total_seconds: int = time_delta.seconds
        microseconds: int = time_delta.microseconds

        return f"{total_seconds}.{microseconds:06d}"


    def __init__(self: typing.Self, logging_level: int = logging.WARNING) -> None:
        self._sim_master_delta: datetime.timedelta = datetime.timedelta()
        self._user_clocks: dict[str, SimTime.UserClock] = {}
        self._logger.setLevel(logging_level)


    def add_user_clock(self: typing.Self, user_clock: UserClock) -> None:
        if user_clock.clock_name in self._user_clocks:
            raise ValueError(f"Tried to add clock named {user_clock.clock_name} that was already added")

        self._user_clocks[user_clock.clock_name] = user_clock
        SimTime._logger.info(f"Added user clock \"{user_clock.clock_name}\" with initial value of "
                             f"{user_clock.time_current().isoformat(sep=" ", timespec="microseconds")}")


    def advance_sim_time(self: typing.Self, time_delta: datetime.timedelta) -> None:
        if time_delta < SimTime._zero_delta:
            raise ValueError("Tried to move time backwards")

        if time_delta == SimTime._zero_delta:
            # No-op
            return

        self._sim_master_delta += time_delta

        # Now add the delta to all individual clocks
        for curr_clock in self._user_clocks.values():
            curr_clock.advance_clock(time_delta)

        SimTime._logger.info(f"Advanced simulation time by {SimTime.timedelta_isoformat(time_delta)} s")


    def user_clock(self: typing.Self, clock_name: str) -> UserClock:
        if clock_name not in self._user_clocks:
            raise ValueError(f"Requested non-existent clock \"{clock_name}\"")

        return self._user_clocks[clock_name]


    def user_clocks(self: typing.Self) -> dict[str, UserClock]:
        return self._user_clocks


if __name__ == "__main__":

    def _print_clocks(clocks_to_print: dict[str, SimTime.UserClock]):
        epoch_date: datetime.date = datetime.date(1970, 1, 1)
        for clock_name, user_clock in sorted(clocks_to_print.items()):
            current_datetime: datetime.datetime = user_clock.time_current()
            if current_datetime.date() != epoch_date:
                print(f"\t{clock_name:26} : "
                      f"{current_datetime.isoformat(sep=" ", timespec="microseconds")}")
            else:
                print(f"\t{clock_name:26} :            "
                      f"{current_datetime.time().isoformat(timespec="microseconds")}")


    logging.basicConfig()

    sim_engine: SimTime = SimTime(
        # logging_level=logging.DEBUG
    )

    sim_engine.add_user_clock(
        SimTime.UserClock("sim_time_relative", datetime.time(),
                          # logging_level=logging.DEBUG
        )
    )

    receiver_time_absolute_gps: datetime.datetime = datetime.datetime.fromisoformat("2026-06-01T00:00:00.000000")
    sim_engine.add_user_clock(
        SimTime.UserClock("receiver_time_absolute_gps", receiver_time_absolute_gps,
                          # logging_level=logging.DEBUG
        )
    )

    sat_time_absolute_gps: datetime.datetime = receiver_time_absolute_gps - datetime.timedelta(seconds=0.071414)
    sim_engine.add_user_clock(
        SimTime.UserClock("sat_time_absolute_gps", sat_time_absolute_gps,
                          # logging_level=logging.DEBUG
        )
    )

    print()
    print("Clocks at starting line:")
    _print_clocks(sim_engine.user_clocks())

    time_to_advance: datetime.timedelta = datetime.timedelta(seconds=5.071414)
    sim_engine.advance_sim_time(time_to_advance)
    print(f"\nAdvanced sim time by {SimTime.timedelta_isoformat(time_to_advance)} s")

    print()
    print("Clocks after time advance:")
    _print_clocks(sim_engine.user_clocks())

    print()
    print("Elapsed time reported by all user clocks:")
    for clock_name, user_clock in sorted(sim_engine.user_clocks().items()):
        print(f"\t{clock_name:26} : "
              f"{SimTime.timedelta_isoformat(user_clock.time_elapsed()):>13} s")
