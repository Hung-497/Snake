"""Display-free checks for the board effects' timing rules."""

from snake.ui.MotionRules import ViewFade, board_effects_enabled, end_flash_alpha, food_pulse_scale


def test_board_effects_stop_at_fast_speed():
    assert not board_effects_enabled(1)
    assert board_effects_enabled(5)
    assert board_effects_enabled(10)


def test_food_pulse_is_gentle_and_changes_with_elapsed_time():
    scales = [food_pulse_scale(seconds) for seconds in (0, 0.3, 0.6, 0.9, 1.2)]

    assert all(0.88 <= scale <= 1.0 for scale in scales)
    assert max(scales) - min(scales) >= 0.08


def test_end_flash_fades_out_by_elapsed_time():
    start = end_flash_alpha(0)
    halfway = end_flash_alpha(0.09)

    assert 0 < halfway < start <= 80
    assert end_flash_alpha(0.18) == 0
    assert end_flash_alpha(1.0) == 0


def test_view_fade_switches_halfway_and_finishes_clear():
    fade = ViewFade()
    fade.start("settings")

    assert fade.advance_by(0.045) is None
    assert 0 < fade.alpha < 255
    assert fade.advance_by(0.045) == "settings"
    assert fade.alpha == 255
    assert fade.advance_by(0.09) is None
    assert fade.alpha == 0
    assert not fade.active


def test_a_new_navigation_replaces_a_pending_view():
    fade = ViewFade()
    fade.start("play")
    fade.advance_by(0.04)
    fade.start("records")

    assert fade.advance_by(0.09) == "records"
    fade.clear()
    assert not fade.active
    assert fade.alpha == 0
