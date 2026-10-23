"""Compare two bots game by game, with a 95% range for the difference.

Both bots played the same seeds, so each seed gives one score difference and
the luck of the food placement cancels out. The 95% range is the t-interval
around the average difference: average ± t × standard deviation / √games. If
the range lies wholly above or below zero, the difference is reliable.
"""

from dataclasses import dataclass
import math
import statistics


# Published t values for a 95% range with very few games, where the formula
# in t_value is not accurate enough.
SMALL_T_VALUES = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776}
NORMAL_97_5 = statistics.NormalDist().inv_cdf(0.975)


@dataclass(frozen=True)
class PairedComparison:
    game_count: int
    mean_difference: float
    # None when there are too few games for a range.
    low: float | None
    high: float | None

    @property
    def verdict(self):
        if self.low is None:
            return "too few games"
        if self.low > 0:
            return "first is better"
        if self.high < 0:
            return "second is better"
        return "no reliable difference"


def t_value(degrees_of_freedom):
    """The t value for a two-sided 95% range.

    Beyond the small table this uses the Cornish-Fisher expansion, which
    adds corrections to the normal value of 1.96 that shrink as the number
    of games grows.
    """
    if degrees_of_freedom in SMALL_T_VALUES:
        return SMALL_T_VALUES[degrees_of_freedom]
    z = NORMAL_97_5
    v = degrees_of_freedom
    return (
        z
        + (z**3 + z) / (4 * v)
        + (5 * z**5 + 16 * z**3 + 3 * z) / (96 * v**2)
        + (3 * z**7 + 19 * z**5 + 17 * z**3 - 15 * z) / (384 * v**3)
        + (79 * z**9 + 776 * z**7 + 1482 * z**5 - 1920 * z**3 - 945 * z) / (92160 * v**4)
    )


def compare_paired(first_scores, second_scores):
    """Compare two equal-length score lists, where position i is the same seed."""
    if len(first_scores) != len(second_scores) or not first_scores:
        raise ValueError("Scores must be paired game by game")
    differences = [first - second for first, second in zip(first_scores, second_scores)]
    game_count = len(differences)
    mean_difference = statistics.mean(differences)
    if game_count < 2:
        return PairedComparison(game_count, mean_difference, None, None)
    margin = (
        t_value(game_count - 1) * statistics.stdev(differences) / math.sqrt(game_count)
    )
    return PairedComparison(
        game_count, mean_difference, mean_difference - margin, mean_difference + margin,
    )
