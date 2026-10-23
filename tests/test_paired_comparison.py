"""The game-by-game comparison is checked against numbers worked out by hand."""

import pytest

from snake.analysis.PairedComparison import compare_paired, t_value


def test_differences_with_a_range_above_zero_are_reliable():
    # Differences 2, 3, 4: average 3, sample standard deviation 1. With 3
    # games the t value for 95% and 2 degrees of freedom is 4.303, so the
    # range is 3 ± 4.303 × 1 / √3 = 3 ± 2.484.
    comparison = compare_paired([3, 5, 7], [1, 2, 3])

    assert comparison.game_count == 3
    assert comparison.mean_difference == 3
    assert comparison.low == pytest.approx(0.516, abs=0.001)
    assert comparison.high == pytest.approx(5.484, abs=0.001)
    assert comparison.verdict == "first is better"


def test_a_range_that_crosses_zero_is_no_reliable_difference():
    comparison = compare_paired([5, 3, 6, 2], [4, 4, 4, 4])

    assert comparison.mean_difference == 0
    assert comparison.low < 0 < comparison.high
    assert comparison.verdict == "no reliable difference"


def test_a_range_below_zero_means_the_second_is_better():
    comparison = compare_paired([1, 2, 3], [3, 5, 7])

    assert comparison.high == pytest.approx(-0.516, abs=0.001)
    assert comparison.verdict == "second is better"


def test_identical_scores_have_no_difference_and_no_spread():
    comparison = compare_paired([4, 9, 2], [4, 9, 2])

    assert (comparison.mean_difference, comparison.low, comparison.high) == (0, 0, 0)
    assert comparison.verdict == "no reliable difference"


def test_one_game_is_not_enough_for_a_range():
    comparison = compare_paired([10], [4])

    assert comparison.mean_difference == 6
    assert comparison.low is None and comparison.high is None
    assert comparison.verdict == "too few games"


def test_scores_must_be_paired_game_by_game():
    with pytest.raises(ValueError):
        compare_paired([1, 2, 3], [1, 2])


@pytest.mark.parametrize("degrees, expected", [
    (1, 12.706), (2, 4.303), (5, 2.571), (10, 2.228), (30, 2.042), (199, 1.972),
])
def test_t_values_match_the_published_table(degrees, expected):
    assert t_value(degrees) == pytest.approx(expected, abs=0.002)
