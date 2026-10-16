"""Bot Experiment games and reports can be built outside the RunExperiment command."""

import json
import random

from snake.bots.RuleBasedBot import RuleBasedBot
from snake.engine.GameConfig import GameConfig
from snake.sessions.ExperimentReport import (
    REPORT_SCHEMA_VERSION, build_report, game_outcome, make_engine,
    play_evaluation_game, save_report, summarize_games,
)


CONFIG = GameConfig(8, 8, 20)


def test_one_evaluation_game_records_its_seed_score_moves_and_outcome():
    engine = make_engine(CONFIG, 7)
    bot = RuleBasedBot(engine, random_source=random.Random(8))

    game, elapsed_seconds = play_evaluation_game(engine, bot, seed=7, max_moves=500)

    assert game == {
        "seed": 7, "score": engine.score, "moves": game["moves"],
        "outcome": game_outcome(engine),
    }
    assert 0 < game["moves"] <= 500
    assert elapsed_seconds >= 0


def test_a_game_cut_off_by_the_move_limit_is_a_move_limit_outcome():
    engine = make_engine(CONFIG, 7)
    bot = RuleBasedBot(engine, random_source=random.Random(8))

    game, _ = play_evaluation_game(engine, bot, seed=7, max_moves=1)

    assert game["moves"] == 1
    assert game["outcome"] == "move_limit"


def test_a_report_describes_the_board_seeds_and_each_bots_games():
    games = [{"seed": 3, "score": 4, "moves": 20, "outcome": "collision"}]
    results = {"rule": {"games": games, "summary": summarize_games(games, 0.5)}}

    report = build_report(
        CONFIG, base_seed=3, game_count=1, max_moves=500, bot_modes=("rule",), results=results,
    )

    assert report["schema_version"] == REPORT_SCHEMA_VERSION == 3
    assert report["board"] == {"width": 8, "height": 8, "tile_size": 20}
    assert report["seeds"] == [3]
    assert report["bot_seed_offset"] == 1
    assert report["max_moves"] == 500
    assert report["selected_bot_modes"] == ["rule"]
    assert report["bots"] == results


def test_a_saved_report_is_a_new_json_file_in_the_folder(tmp_path):
    path = save_report({"schema_version": 3}, directory=tmp_path / "experiments")

    assert path.parent == tmp_path / "experiments"
    assert json.loads(path.read_text()) == {"schema_version": 3}
