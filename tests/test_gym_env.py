"""Tests for the gym environment"""

from agents.agent_random import Player
from gym_env.env import HoldemTable, Action, Stage, PlayerCycle


def _create_env(n_players):
    """Create an environment"""
    env = HoldemTable(n_players)
    for _ in range(n_players):
        player = Player()
        env.add_player(player)
    env.reset()
    return env


def test_scenario1():
    """Test basic actions with 6 players."""
    env = _create_env(6)
    assert len(env.players[0].cards) == 2
    assert env.current_player.seat == 3  # start with utg

    env.step(Action.CALL)
    env.step(Action.FOLD)
    env.step(Action.FOLD)
    env.step(Action.FOLD)
    env.step(Action.CALL)
    assert env.current_player.seat == 2  # bb
    assert env.players[3].stack == 98
    assert env.players[4].stack == 100
    assert env.players[5].stack == 100
    assert env.players[0].stack == 100
    assert env.players[1].stack == 98
    assert env.players[2].stack == 98
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_POT)  # bb raises
    assert env.player_cycle.second_round
    env.step(Action.FOLD)  # utg
    env.step(Action.CALL)  # 4 only remaining player calls
    assert env.stage == Stage.FLOP
    env.step(Action.CHECK)


def test_heads_up_after_flop():
    """All in at preflop leads to heads up after flop."""
    env = _create_env(6)
    env.step(Action.ALL_IN)  # utg
    env.step(Action.ALL_IN)
    env.step(Action.ALL_IN)
    env.step(Action.ALL_IN)  # 0
    env.step(Action.CALL)  # sb = all in
    assert Action.ALL_IN in env.action_space  # bb has the option to raise
    env.step(Action.FOLD)  # bb folds
    assert sum(env.player_cycle.alive) == 2
    # two players left - heads up
    assert env.stage == Stage.PREFLOP  # start new hand
    assert sum(env.player_cycle.alive) == 2
    env.step(Action.CALL)  # sb calls at preflop, first mover
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_POT)  # bb raises pot
    assert env.stage == Stage.PREFLOP
    assert len(env.action_space) == 2
    env.step(Action.CALL)  # sb can now call and then turn
    assert env.stage == Stage.FLOP
    env.step(Action.CHECK)
    env.step(Action.CHECK)
    assert env.stage == Stage.TURN

def test_scenario3():
    """Test basic actions with 6 players."""
    env = _create_env(6)
    env.step(Action.CALL)  # utg
    env.step(Action.CALL)  # 4
    env.step(Action.CALL)  # 5
    env.step(Action.CALL)  # 0 dealer
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_HAlF_POT)  # sb
    assert len(env.action_space) > 2
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_HAlF_POT)  # bb
    assert env.stage == Stage.PREFLOP
    assert len(env.action_space) == 2
    env.step(Action.CALL)  # utg in second round
    env.step(Action.CALL)  # 4
    env.step(Action.CALL)  # 5
    env.step(Action.CALL)  # dealer
    assert env.stage == Stage.PREFLOP
    env.step(Action.CALL)  # sb
    assert env.stage == Stage.FLOP
    assert env.current_player.seat == 1
    env.step(Action.RAISE_HAlF_POT)


def test_cycle_mechanism1():
    """Test cycle"""
    lst = ['dealer', 'sb', 'bb', 'utg', 'utg1', 'utg2']
    cycle = PlayerCycle(lst)
    current = cycle.next_player()
    assert current == 'sb'
    current = cycle.next_player(step=2)
    assert current == 'utg'
    cycle.deactivate_current()
    current = cycle.next_player(step=6)
    assert current == 'utg1'
    current = cycle.next_player(step=1)
    assert current == 'utg2'
    current = cycle.next_player()
    assert current == 'dealer'
    cycle.deactivate_player(0)
    cycle.deactivate_player(1)
    cycle.deactivate_player(2)
    current = cycle.next_player(step=2)
    assert current == 'utg1'


def test_cycle_mechanism2():
    """Test cycle"""
    lst = ['dealer', 'sb', 'bb', 'utg']
    cycle = PlayerCycle(lst, start_idx=2, max_steps_total=5)
    current = cycle.next_player()
    assert current == 'utg'
    cycle.next_player()
    cycle.next_player()
    current = cycle.next_player(step=2)
    assert not current