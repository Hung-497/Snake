"""Zoom and pan in the Network focus layout, as plain arithmetic with no display."""

import pytest

from snake.ui.NetworkLayout import (
    LIVE_TRAINING_HUD_HEIGHT, MAX_ZOOM, MIN_ZOOM, Area, ZoomPan, focus_area, pan_by,
    to_screen, zoom_at,
)


AREA = Area(left=0, bottom=0, width=1000, height=800)
CENTRE = (500, 400)


def test_the_focus_layout_gives_the_graph_the_whole_window_under_the_hud():
    area = focus_area(1152, 960, LIVE_TRAINING_HUD_HEIGHT)

    assert area == Area(0, 0, 1152, 960 - LIVE_TRAINING_HUD_HEIGHT)


def test_without_zoom_points_stay_where_they_are():
    assert to_screen(ZoomPan(), (120, 300), AREA) == (120, 300)


def test_zooming_in_at_the_centre_spreads_points_out_from_it():
    view = zoom_at(ZoomPan(), 2.0, CENTRE, AREA)

    assert view.zoom == 2.0
    assert to_screen(view, CENTRE, AREA) == pytest.approx(CENTRE)
    assert to_screen(view, (600, 450), AREA) == pytest.approx((700, 500))


def test_the_point_under_the_mouse_stays_under_the_mouse():
    view = zoom_at(ZoomPan(), 2.0, (500, 400), AREA)
    mouse = (300, 200)
    # The graph point currently drawn under the mouse.
    under_mouse = (
        (mouse[0] - CENTRE[0] - view.offset_x) / view.zoom + CENTRE[0],
        (mouse[1] - CENTRE[1] - view.offset_y) / view.zoom + CENTRE[1],
    )

    zoomed = zoom_at(view, 1.5, mouse, AREA)

    assert to_screen(zoomed, under_mouse, AREA) == pytest.approx(mouse)


def test_zoom_stays_within_its_limits():
    view = ZoomPan()
    for _ in range(20):
        view = zoom_at(view, 2.0, CENTRE, AREA)
    assert view.zoom == MAX_ZOOM

    for _ in range(40):
        view = zoom_at(view, 0.5, CENTRE, AREA)
    assert view.zoom == MIN_ZOOM == 1.0


def test_the_whole_graph_already_fits_so_it_cannot_be_dragged_away():
    view = pan_by(ZoomPan(), 300, -200, AREA)

    assert (view.offset_x, view.offset_y) == (0, 0)


def test_a_zoomed_graph_pans_only_until_its_edge_reaches_the_window_edge():
    zoomed = zoom_at(ZoomPan(), 2.0, CENTRE, AREA)

    small_drag = pan_by(zoomed, 100, 50, AREA)
    huge_drag = pan_by(zoomed, 5000, -5000, AREA)

    assert (small_drag.offset_x, small_drag.offset_y) == (100, 50)
    # At zoom 2 the graph is twice as big, so it can move half the area each way.
    assert (huge_drag.offset_x, huge_drag.offset_y) == (500, -400)


def test_zooming_back_out_brings_the_graph_back_into_view():
    view = pan_by(zoom_at(ZoomPan(), 4.0, CENTRE, AREA), 1200, 900, AREA)

    zoomed_out = zoom_at(view, 0.25, CENTRE, AREA)

    assert zoomed_out.zoom == 1.0
    assert (zoomed_out.offset_x, zoomed_out.offset_y) == (0, 0)


def test_reset_shows_the_whole_graph_again():
    assert ZoomPan() == ZoomPan(zoom=1.0, offset_x=0, offset_y=0)
