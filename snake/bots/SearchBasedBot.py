from collections import deque
from dataclasses import replace

from snake.bots.BotMode import BotMode


class SearchBasedBot(BotMode):
    """Seek food through future states while keeping a way to continue."""

    # Fixed work limits keep seeded play repeatable and the app responsive.
    MAX_EXPLORED_STATES = 800
    MAX_MOVES_PER_UPDATE = 1

    def __init__(self, engine, random_source=None):
        super().__init__(engine, random_source=random_source)

    def choose_action(self, state):
        if state.game_over:
            return None

        remaining_states = self.MAX_EXPLORED_STATES
        food_action, rejected_food_direction, remaining_states = self._find_food_action(
            state, remaining_states
        )
        if food_action is not None:
            return food_action

        return self._survival_action(
            state, rejected_food_direction, remaining_states
        )

    def _legal_moves(self, state):
        for direction in self.DIRECTIONS:
            if not self.can_turn(state, direction):
                continue
            transition = self.engine.preview_from(state, direction)
            if transition.moved:
                yield direction, transition

    def _find_food_action(self, state, search_limit):
        if state.food_position is None:
            return None, None, search_limit

        positions_to_check = deque([(state, ())])
        visited_states = {state}
        remaining_states = search_limit
        rejected_food_direction = None

        while positions_to_check and remaining_states > 0:
            current_state, path = positions_to_check.popleft()
            remaining_states -= 1

            for direction, transition in self._legal_moves(current_state):
                next_path = path + (direction,)
                if transition.ate_food:
                    if transition.game_won:
                        return next_path[0], None, remaining_states

                    after_eating = self._state_after(current_state, transition)
                    can_continue, remaining_states = self._can_reach_tail(
                        after_eating, remaining_states
                    )
                    if can_continue:
                        return next_path[0], None, remaining_states
                    if not path:
                        rejected_food_direction = direction
                    continue

                # The body and heading change at every search step.
                next_state = self._state_after(current_state, transition)
                if next_state in visited_states:
                    continue
                visited_states.add(next_state)
                positions_to_check.append((next_state, next_path))

        return None, rejected_food_direction, remaining_states

    @staticmethod
    def _state_after(state, transition):
        return replace(
            state,
            snake_position=transition.position,
            snake_body=transition.body,
            direction=transition.direction,
            food_position=None if transition.ate_food else state.food_position,
            score=transition.score,
            game_over=transition.game_over,
            game_won=transition.game_won,
        )

    def _can_reach_tail(self, state, remaining_states):
        tail_position = state.snake_body[-1]
        positions_to_check = deque([state])
        visited_states = {state}

        while positions_to_check and remaining_states > 0:
            current_state = positions_to_check.popleft()
            remaining_states -= 1

            for _, transition in self._legal_moves(current_state):
                if transition.position == tail_position:
                    return True, remaining_states

                next_state = self._state_after(current_state, transition)
                if next_state not in visited_states:
                    visited_states.add(next_state)
                    positions_to_check.append(next_state)

        return False, remaining_states

    def _survival_action(self, state, rejected_food_direction, remaining_states):
        best_action = None
        best_rank = None

        for direction, transition in self._legal_moves(state):
            if direction == rejected_food_direction:
                continue
            next_state = self._state_after(state, transition)
            space, remaining_states = self._count_future_positions(
                next_state, remaining_states
            )
            if state.food_position is None:
                food_distance = 0
            else:
                food_distance = (
                    abs(transition.position.x - state.food_position.x)
                    + abs(transition.position.y - state.food_position.y)
                )

            # Prefer enough room for the whole snake, then make progress
            # toward food instead of chasing tiny search-limit differences.
            snake_length = len(next_state.snake_body) + 1
            useful_space = min(space, snake_length)
            rank = (-useful_space, food_distance, -space)
            if best_rank is None or rank < best_rank:
                best_action = direction
                best_rank = rank

        # The food move is still legal when it is the only available action.
        return best_action if best_action is not None else rejected_food_direction

    def _count_future_positions(self, state, remaining_states):
        positions_to_check = deque([state])
        visited_states = {state}
        reachable_positions = {state.snake_position}

        while positions_to_check and remaining_states > 0:
            current_state = positions_to_check.popleft()
            remaining_states -= 1

            for _, transition in self._legal_moves(current_state):
                next_state = self._state_after(current_state, transition)
                reachable_positions.add(next_state.snake_position)
                if next_state not in visited_states:
                    visited_states.add(next_state)
                    positions_to_check.append(next_state)

        return len(reachable_positions), remaining_states
