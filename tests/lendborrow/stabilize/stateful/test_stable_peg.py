import pytest
import boa
from boa.vyper.contract import BoaError
from hypothesis import settings
from hypothesis.stateful import run_state_machine_as_test, invariant
from hypothesis._settings import HealthCheck

from . import base

pytestmark = pytest.mark.usefixtures(
    "add_initial_liquidity",
    "provide_token_to_peg_keepers",
    "mint_alice"
)


class StateMachine(base.StateMachine):
    """
    Stateful test that performs a series of deposits, swaps and withdrawals
    and confirms that profit is calculated right.
    """

    def __init__(self):
        super().__init__()

    @invariant()
    def invariant_profit_increases(self):
        """
        Verify that Peg Keeper profit only increases.
        """
        for i, peg_keeper in enumerate(self.peg_keepers):
            profit = peg_keeper.calc_profit()
            assert profit >= self.profit[i]
            self.profit[i] = profit

    @invariant()
    def invariant_profit(self):
        """
        Check Profit value.
        """
        for peg_keeper, swap in zip(self.peg_keepers, self.swaps):
            try:
                with boa.env.prank(self.alice):
                    peg_keeper.update()
            except BoaError as e:
                if 'peg unprofitable' in str(e):
                    continue

            profit = peg_keeper.calc_profit()
            virtual_price = swap.get_virtual_price()
            aim_profit = (
                swap.balanceOf(peg_keeper) - peg_keeper.debt() * 10**18 // virtual_price
            )
            assert aim_profit >= profit  # Never take more than real profit
            assert aim_profit - profit < 2e18  # Error less than 2 LP Tokens

    @invariant()
    def invariant_check_diff(self):
        """
        Verify that Peg Keeper decreased diff of balances by 1/5.
        """
        for idx, (peg_keeper, swap, dmul) in enumerate(zip(self.peg_keepers, self.swaps, self.dmul)):
            balances_before = [swap.balances(i) for i in range(2)]
            profit = 0

            try:
                with boa.env.prank(self.alice):
                    profit = peg_keeper.update()
            except BoaError as e:
                if 'peg unprofitable' in str(e):
                    continue

            balances = [swap.balances(i) for i in range(2)]

            diff = balances[1] * 10**18 // dmul[1] - balances[0] * 10**18 // dmul[0]
            last_diff = balances_before[1] * 10**18 // dmul[1] - balances_before[0] * 10**18 // dmul[0]

            if diff == last_diff:
                assert profit == 0
            else:
                assert (abs(diff - (last_diff - last_diff // 5)) <= 5) or (peg_keeper.debt() == 0)


def test_stable_peg(
    add_initial_liquidity,
    swaps,
    peg_keepers,
    redeemable_tokens,
    stablecoin,
    alice,
    receiver,
    admin,
):
    with boa.env.prank(admin):
        for swap in swaps:
            swap.commit_new_fee(4 * 10**7)
        boa.env.time_travel(4 * 86400)
        for swap in swaps:
            swap.apply_new_fee()

    StateMachine.TestCase.settings = settings(max_examples=20, stateful_step_count=40, suppress_health_check=HealthCheck.all())
    for k, v in locals().items():
        setattr(StateMachine, k, v)
    run_state_machine_as_test(StateMachine)


def test_fail_remove(
    add_initial_liquidity,
    swaps,
    peg_keepers,
    redeemable_tokens,
    stablecoin,
    alice,
    receiver,
    admin,
):
    with boa.env.prank(admin):
        for swap in swaps:
            swap.commit_new_fee(4 * 10**7)
        boa.env.time_travel(4 * 86400)
        for swap in swaps:
            swap.apply_new_fee()
    for k, v in locals().items():
        setattr(StateMachine, k, v)
    state = StateMachine()
    state.advance_time()
    state.invariant_check_diff()
    state.invariant_profit()
    state.invariant_profit_increases()
    state.remove(pct=0.75, pool_idx=0)
    state.teardown()


def test_fail_wrong_diff(
    add_initial_liquidity,
    swaps,
    peg_keepers,
    redeemable_tokens,
    stablecoin,
    alice,
    receiver,
    admin,
):
    with boa.env.prank(admin):
        for swap in swaps:
            swap.commit_new_fee(4 * 10**7)
        boa.env.time_travel(4 * 86400)
        for swap in swaps:
            swap.apply_new_fee()
    for k, v in locals().items():
        setattr(StateMachine, k, v)
    state = StateMachine()
    state.advance_time()
    state.invariant_check_diff()
    state.invariant_profit()
    state.invariant_profit_increases()
    state.exchange(idx=0, pct=0.75, pool_idx=0)
    state.advance_time()
    state.invariant_check_diff()
    state.teardown()


def test_fail_wrong_diff_2(
    add_initial_liquidity,
    swaps,
    peg_keepers,
    redeemable_tokens,
    stablecoin,
    alice,
    receiver,
    admin,
):
    with boa.env.prank(admin):
        for swap in swaps:
            swap.commit_new_fee(4 * 10**7)
        boa.env.time_travel(4 * 86400)
        for swap in swaps:
            swap.apply_new_fee()
    for k, v in locals().items():
        setattr(StateMachine, k, v)
    state = StateMachine()
    state.advance_time()
    state.invariant_check_diff()
    state.invariant_profit()
    state.invariant_profit_increases()
    state.remove(pct=0.5, pool_idx=1)
    state.advance_time()
    state.invariant_check_diff()
    state.invariant_profit()
    state.invariant_profit_increases()
    state.add_one_coin(idx=1, pct=0.5, pool_idx=0)
    state.advance_time()
    state.invariant_check_diff()
    state.invariant_profit()
    state.invariant_profit_increases()
    state.remove_one_coin(idx=0, pct=0.75, pool_idx=0)
    state.advance_time()
    state.invariant_check_diff()
    state.invariant_profit()
    state.invariant_profit_increases()
    state.remove(pct=0.5, pool_idx=0)
    state.advance_time()
    state.invariant_check_diff()
    state.teardown()
