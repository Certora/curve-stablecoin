methods {
    function total_shares(int256) external returns uint256 envfree;
    function admin() external returns address envfree;
    function BORROWED_TOKEN() external returns address envfree;
    function COLLATERAL_TOKEN() external returns address envfree;
    function BORROWED_PRECISION() external returns uint256 envfree;
    function COLLATERAL_PRECISION() external returns uint256 envfree;
    function active_band() external returns int256 envfree;
    function active_band_with_skip() external returns int256 envfree;
    function min_band() external returns int256 envfree;
    function max_band() external returns int256 envfree;
    function bands_x(int256 n) external returns uint256 envfree;
    function bands_y(int256 n) external returns uint256 envfree;
    function read_user_tick_numbers(address) external returns int256[2] envfree;
    function liquidity_mining_callback() external returns address envfree;
    function has_liquidity(address) external returns bool envfree;
    function admin_fees_x() external returns uint256 envfree;
    function admin_fees_y() external returns uint256 envfree;

    //
    function _.price_w() external => CONSTANT;
    function _.balanceOf(address account) external => require_uint256(tokenBalance[calledContract][account]) expect uint256;
    function _.approve(address spender, uint256 amount) external with (env e) => approveSummary(calledContract, e.msg.sender, spender, amount) expect bool;
    function _.transfer(address to, uint256 amount) external with (env e) => transferFromSummary(calledContract, e.msg.sender, to, amount) expect bool;
    function _.transferFrom(address from, address to, uint256 amount) external => transferFromSummary(calledContract, from, to, amount) expect bool;
}

ghost mapping(address => mapping(address => mathint)) tokenBalance;
ghost mapping(address => mapping(address => mapping(address => mathint))) tokenApprovals {
    init_state axiom (forall address token. forall address spender. tokenApprovals[token][currentContract][spender] == 0);
}

function approveSummary(address token, address from, address spender, uint256 amount) returns bool {
    tokenApprovals[token][from][spender] = amount;
    return true;
}

function transferFromSummary(address token, address from, address to, uint256 amount) returns bool {
    require tokenBalance[token][from] >= to_mathint(amount);
    tokenBalance[token][from] = tokenBalance[token][from] - amount;
    tokenBalance[token][to] = tokenBalance[token][to] + amount;
    return true;
}

definition changes_totalxy(method f) returns bool = (
        f.selector == sig:withdraw(address, uint256).selector ||
        f.selector == sig:deposit_range(address, uint256, int256, int256).selector ||
        f.selector == sig:reset_admin_fees().selector ||
        f.selector == sig:exchange(uint256, uint256, uint256, uint256).selector ||
        f.selector == sig:exchange(uint256, uint256, uint256, uint256, address).selector ||
        f.selector == sig:exchange_dy(uint256, uint256, uint256, uint256).selector ||
        f.selector == sig:exchange_dy(uint256, uint256, uint256, uint256, address).selector
    );

definition changes_balance(method f) returns bool = (
        f.selector == sig:exchange(uint256, uint256, uint256, uint256).selector ||
        f.selector == sig:exchange(uint256, uint256, uint256, uint256, address).selector ||
        f.selector == sig:exchange_dy(uint256, uint256, uint256, uint256).selector ||
        f.selector == sig:exchange_dy(uint256, uint256, uint256, uint256, address).selector
    );

ghost mapping(address => int256) user_ns {
    init_state axiom (forall address user. user_ns[user] == 0);
}
ghost mapping(address => mathint) user_n1 {
    init_state axiom (forall address user. user_n1[user] == 0);
}
ghost mapping(address => mathint) user_n2 {
    init_state axiom (forall address user. user_n2[user] == 0);
}
ghost mapping(address => mapping(mathint => uint256)) user_ticks_unpacked {
    init_state axiom (forall address user. forall mathint n. user_ticks_unpacked[user][n] == 0);
}
ghost mapping(address => mapping(mathint => uint256)) user_ticks_packed {
    init_state axiom (forall address user. forall mathint n. user_ticks_packed[user][n] == 0);
}
ghost mapping(mathint => mathint) total_shares_ghost {
    init_state axiom (forall mathint n. total_shares_ghost[n] == 0);
}
ghost mathint total_x { init_state axiom total_x == 0; }
ghost mathint total_y { init_state axiom total_y == 0; }

hook Sstore admin_fees_x uint256 newValue (uint256 oldValue) {
    total_x = total_x + (newValue - oldValue) * BORROWED_PRECISION();
}

hook Sstore bands_x[KEY int256 n] uint256 newValue (uint256 oldValue) {
    total_x = total_x - oldValue + newValue;
}

hook Sstore admin_fees_y uint256 newValue (uint256 oldValue) {
    total_y = total_y + (newValue - oldValue) * COLLATERAL_PRECISION();
}

hook Sstore bands_y[KEY int256 n] uint256 newValue (uint256 oldValue) {
    total_y = total_y - oldValue + newValue;
}

hook Sstore user_shares[KEY address user].ns int256 newPacked (int256 oldPacked) {
    user_ns[user] = newPacked;

    mathint n1 = newPacked % 2^128;
    mathint realn1;
    if (n1 >= 2^127) {
        realn1 = n1 - 2^128;
    } else {
        realn1 = n1;
    }
    mathint realn2 = (newPacked - realn1 + 2^256) / 2^128 - 2^128;
    assert realn1 < 2^127 && realn1 >= -2^127;
    assert realn2 * 2^128 + realn1 == to_mathint(newPacked);
    user_n1[user] = realn1;
    user_n2[user] = realn2;
}

hook Sload int256 packed user_shares[KEY address user].ns {
    require user_ns[user] == packed;
}

hook Sstore user_shares[KEY address user].ticks[INDEX uint256 index] uint256 newPacked (uint256 oldPacked) {
    user_ticks_packed[user][index] = newPacked;
    if (newPacked == 0 && index == 0) {
        // clear all ticks for current user
        havoc total_shares_ghost assuming
            forall mathint n. total_shares_ghost@new[n] == total_shares_ghost@old[n] - user_ticks_unpacked[user][n];
        havoc user_ticks_unpacked assuming
            forall address u. forall mathint n. user_ticks_unpacked@new[u][n] == (u == user ? 0 : user_ticks_unpacked@old[u][n]);
    } else {
        mathint basetick = user_n1[user] + 2 * index;
        total_shares_ghost[basetick + 0] = total_shares_ghost[basetick + 0] - user_ticks_unpacked[user][basetick + 0];
        total_shares_ghost[basetick + 1] = total_shares_ghost[basetick + 1] - user_ticks_unpacked[user][basetick + 1];
        user_ticks_unpacked[user][basetick + 0] = require_uint256(newPacked % 2^128);
        user_ticks_unpacked[user][basetick + 1] = require_uint256(newPacked / 2^128);
        assert index == 0 => newPacked != 0;
        total_shares_ghost[basetick + 0] = total_shares_ghost[basetick + 0] + user_ticks_unpacked[user][basetick + 0];
        total_shares_ghost[basetick + 1] = total_shares_ghost[basetick + 1] + user_ticks_unpacked[user][basetick + 1];
    }
}

hook Sload uint256 packed user_shares[KEY address user].ticks[INDEX uint256 index] {
    require user_ticks_packed[user][index] == packed;
}

invariant only_admin_approved(address token, address spender)
    tokenApprovals[token][currentContract][spender] > 0 => spender == 0 || spender == admin();

invariant total_shares_match(int256 n)
    total_shares_ghost[n] == to_mathint(total_shares(n))
{
    preserved {
        requireInvariant unpack_invariant();
        requireInvariant n1_n2_inrange();
    }
    preserved withdraw(address user, uint256 frac) with (env e) {
        requireInvariant n1_n2_inrange();
        require to_mathint(user_ticks_unpacked[user][n]) == packed_to_unpacked(user, n);
    }
}

definition user_ticks_valid(address user) returns bool = user_ticks_packed[user][0] != 0;
definition packed_to_unpacked(address user, mathint index) returns mathint =
    (user_ticks_packed[user][0] == 0 || index < user_n1[user] || index > user_n2[user] ? 0 :
      (index - user_n1[user]) % 2 == 0 ? user_ticks_packed[user][(index - user_n1[user])/2] % 2^128
                                       : user_ticks_packed[user][(index - user_n1[user])/2] / 2^128);

invariant unpack_invariant()
    (forall address user. forall mathint index. to_mathint(user_ticks_unpacked[user][index]) == packed_to_unpacked(user, index))
{
    preserved {
        requireInvariant n1_n2_inrange();
    }
    preserved deposit_range(address user, uint256 amount, int256 n1, int256 n2) with (env e) {
        require e.msg.sender == admin() => n1 <= n2;
    }
}

invariant n1_n2_inrange()
    (forall address user. 0 <= 2^127 + user_n1[user] && user_n1[user] <= user_n2[user] && user_n2[user] < 2^127
                          && to_mathint(user_ns[user]) == user_n1[user] + 2^128 * user_n2[user])
{
    preserved deposit_range(address user, uint256 amount, int256 n1, int256 n2) with (env e) {
        require e.msg.sender == admin() => n1 <= n2;
    }
}

invariant low_bands_empty(int256 n)
    n < min_band() => bands_x(n) == 0 && bands_y(n) == 0;
invariant high_bands_empty(int256 n)
    n > max_band() => bands_x(n) == 0 && bands_y(n) == 0;

invariant low_bands_in_x(int256 n)
    n < active_band() => bands_y(n) == 0;

invariant high_bands_in_y(int256 n)
    n > active_band() => bands_x(n) == 0;

rule deposit_adds_to_bands(address user, uint256 amount, int256 n1, int256 n2) {
    env e;
    require e.msg.sender == admin() => n1 <= n2;
    mathint total_x_before = total_x;
    mathint total_y_before = total_y;
    deposit_range(e, user, amount, n1, n2);
    assert e.msg.sender == admin();
    assert total_x == total_x_before;
    assert total_y == total_y_before + amount * COLLATERAL_PRECISION();
    assert user_n1[user] == to_mathint(n1) && user_n2[user] == to_mathint(n2);
}

rule withdraw_removes_from_bands(address user, uint256 frac) {
    env e;
    requireInvariant n1_n2_inrange();
    require BORROWED_PRECISION() != 0;
    // work around for bug in AMM.vy
    require BORROWED_PRECISION() == 1;
    require COLLATERAL_PRECISION() != 0;
    mathint total_x_before = total_x;
    mathint total_y_before = total_y;
    mathint num_bands = user_n2[user] - user_n1[user] + 1;
    uint256[2] amounts;
    amounts = withdraw(e, user, frac);
    assert e.msg.sender == admin();
    uint256 amount_x = amounts[0];
    uint256 amount_y = amounts[1];
    mathint removed_x = total_x_before - total_x;
    mathint removed_y = total_y_before - total_y;
    assert amount_x * BORROWED_PRECISION() <= removed_x && removed_x < (amount_x + 2 * num_bands) * BORROWED_PRECISION();
    assert amount_y * COLLATERAL_PRECISION() <= removed_y && removed_y < (amount_y + 2 * num_bands) * COLLATERAL_PRECISION();
}

rule reset_admin_fees_removes_from_total() {
    env e;
    mathint admin_fees_x_before = admin_fees_x();
    mathint admin_fees_y_before = admin_fees_y();
    mathint total_x_before = total_x;
    mathint total_y_before = total_y;
    reset_admin_fees(e);

    mathint removed_x = total_x_before - total_x;
    mathint removed_y = total_y_before - total_y;
    assert removed_x == admin_fees_x_before * BORROWED_PRECISION();
    assert removed_y == admin_fees_y_before * COLLATERAL_PRECISION();
}

rule withdraw_when_not_in_softliquidation(address user, uint256 frac) {
    env e;
    requireInvariant n1_n2_inrange();
    mathint n1_before = user_n1[user];
    mathint min_band = min_band();
    requireInvariant low_bands_empty(require_int256(n1_before));
    requireInvariant high_bands_in_y(require_int256(n1_before));
    if (n1_before + 1 <= user_n2[user]) {
        requireInvariant high_bands_in_y(require_int256(n1_before + 1));
        requireInvariant low_bands_empty(require_int256(n1_before + 1));
    }
    if (n1_before + 2 <= user_n2[user]) {
        requireInvariant high_bands_in_y(require_int256(n1_before + 2));
        requireInvariant low_bands_empty(require_int256(n1_before + 1));
    }
    if (n1_before + 3 <= user_n2[user]) {
        requireInvariant high_bands_in_y(require_int256(n1_before + 3));
        requireInvariant low_bands_empty(require_int256(n1_before + 1));
    }
    mathint active_band_before = active_band_with_skip();
    uint256[2] amounts;
    amounts = withdraw(e, user, frac);
    assert n1_before > active_band_before => amounts[0] == 0;
}

rule withdraw_all_user_shares(address user) {

    env e;
    uint256[2] amounts;
    bool liquidity_before = has_liquidity(user);
    bool valid_before = user_ticks_valid(user);
    amounts = withdraw(e, user, 10^18);
    bool valid_after = user_ticks_valid(user);
    assert valid_before && !valid_after;
    assert liquidity_before && !has_liquidity(user);
}

rule withdraw_some_user_shares(address user) {

    env e;
    uint256 frac;
    uint256[2] amounts;
    bool liquidity_before = has_liquidity(user);
    bool valid_before = user_ticks_valid(user);
    require frac != 10^18;
    amounts = withdraw(e, user, frac);
    bool valid_after = user_ticks_valid(user);
    assert valid_before && valid_after;
    assert liquidity_before && has_liquidity(user);
}

rule deposit_some_user_shares(address user, uint256 amount, int256 n1, int256 n2) {
    env e;
    require e.msg.sender == admin() => n1 <= n2;
    bool valid_before = user_ticks_valid(user);
    deposit_range(e, user, amount, n1, n2);
    bool valid_after = user_ticks_valid(user);
    assert !valid_before && valid_after;
}

rule integrity_of_read_user_tick_numbers(address user) {
    requireInvariant n1_n2_inrange();
    env e;
    int256[2] n1n2;
    n1n2 = read_user_tick_numbers(user);
    assert n1n2[0] <= n1n2[1];
    assert to_mathint(n1n2[0]) == user_n1[user] && to_mathint(n1n2[1]) == user_n2[user];
}

rule deposit_only_in_non_active_bands(address user, uint256 amount, int256 n1, int256 n2) {
    env e;
    require e.msg.sender == admin() => n1 <= n2;
    deposit_range(e, user, amount, n1, n2);
    assert n1 > active_band();
}

rule deposit_range_requires_sorted_arguments(address user, uint256 amount, int256 n1, int256 n2) {
    env e;
    deposit_range(e, user, amount, n1, n2);

    assert n1 <= n2;



    /* The deposit_range does not check whether n1 <= n2. This function is called in the following cases:
    _create_loan(mvalue: uint256, collateral: uint256, debt: uint256, N: uint256, transfer_coins: bool)
        assert N > MIN_TICKS-1, "Need more ticks" // MIN_TICKS == 4
        n1: ...
        n2: int256 = n1 + convert(N - 1, int256)

    // PASS

    _add_collateral_borrow(d_collateral: uint256, d_debt: uint256, _for: address, remove_collateral: bool):
        ns: int256[2] = self.AMM.read_user_tick_numbers(_for)
        n1: ...
        n2: int256 = n1 + unsafe_sub(ns[1], ns[0])

    repay(_d_debt: uint256, _for: address = msg.sender, max_active_band: int256 = 2**255-1, use_eth: bool = True)
        ns: int256[2] = self.AMM.read_user_tick_numbers(_for)
        if ns[0] > active_band:
            n1: ...
            n2: int256 = n1 + unsafe_sub(ns[1], ns[0])


    repay_extended(callbacker: address, callback_args: DynArray[uint256,5])
        ns: int256[2] = self.AMM.read_user_tick_numbers(msg.sender)
        if total_stablecoins < debt
            n1: int256 = self._calculate_debt_n1(cb.collateral, debt, size)
            n2: int256 = n1 + unsafe_sub(ns[1], ns[0])

    */
}


definition DEAD_SHARES() returns mathint = 1000;

rule totalSharesToBandsYShouldBeConstantOnWithdraw(address user) {
    env e;
    int256 n;
    requireInvariant n1_n2_inrange();
    // to avoid timeouts, we require user using only a single band.
    require user_n1[user] + 0 >= user_n2[user];

    uint256 frac;

    require e.msg.sender == admin();

    mathint oldVirtShares = total_shares(n) + DEAD_SHARES();
    mathint oldVirtAssets = bands_y(n) + 1;

    withdraw(e, user, frac);

    mathint newVirtShares = total_shares(n) + DEAD_SHARES();
    mathint newVirtAssets = bands_y(n) + 1;

    // either all shares and assets were withdrawn, or shares increased in value
    assert (newVirtShares == DEAD_SHARES() && newVirtAssets == 1) ||
           newVirtShares * oldVirtAssets <= oldVirtShares * newVirtAssets, "shares must not lose value";
    assert newVirtShares * oldVirtAssets >= oldVirtShares * (newVirtAssets - 1), "shares gain too much value";
    satisfy newVirtShares != oldVirtShares;
}



rule totalSharesToBandsXShouldBeConstantOnWithdraw(address user) {
    env e;
    int256 n;
    requireInvariant n1_n2_inrange();
    // to avoid timeouts, we require user using only a single band.
    require user_n1[user] + 0 >= user_n2[user];

    uint256 frac;

    mathint oldVirtShares = total_shares(n) + DEAD_SHARES();
    mathint oldVirtAssets = bands_x(n) + 1;

    withdraw(e, user, frac);

    mathint newVirtShares = total_shares(n) + DEAD_SHARES();
    mathint newVirtAssets = bands_x(n) + 1;

    // either all shares and assets were withdrawn, or shares increased in value
    assert (newVirtShares == DEAD_SHARES() && newVirtAssets == 1) ||
           newVirtShares * oldVirtAssets <= oldVirtShares * newVirtAssets, "shares must not lose value";
    assert newVirtShares * oldVirtAssets >= oldVirtShares * (newVirtAssets - 1), "shares gain too much value";
    satisfy true;
}

rule totalSharesToBandsYShouldBeConstantOnDepositRange(address user, uint256 amount, int256 n1, int256 n2) {
    env e;

    int256 n;

    //require e.msg.sender == admin() && n1 == n2 && n == n1;
    //require bands_y(n) > 0;

    mathint oldVirtShares = total_shares(n) + DEAD_SHARES();
    mathint oldVirtAssets = bands_y(n) + 1;
//    require oldRatio == 10^21;

    deposit_range(e, user, amount, n1, n2);

    mathint newVirtShares = total_shares(n) + DEAD_SHARES();
    mathint newVirtAssets = bands_y(n) + 1;

    assert newVirtShares * oldVirtAssets <= oldVirtShares * newVirtAssets, "shares must not lose value";
    assert (newVirtShares + 1) * oldVirtAssets >= oldVirtShares * newVirtAssets, "shares gain too much value";

    satisfy n1 == n2 && n == n1;
}




// Exchange...
// i = 0, j = 1, stablecoin is going to AMM (in coin), collateral out of AMM (out coin)
// i = 1, j = 0, collateral is going to AMM, stablecoin out of AMM

// e.msg.sender sends coins, _for gets coins
rule integrityOfExchange_balance(uint256 i, uint256 j, uint256 in_amount, uint256 min_amount, address _for) {
    env e;
    address stablecoin = BORROWED_TOKEN();
    address collateraltoken = COLLATERAL_TOKEN();

    require (i == 0 && j == 1) || (i == 1 && j == 0);
    // the rule only holds if the liquidity mining callback doesn't mess up balances; we assume here that there is none.
    require liquidity_mining_callback() == 0;

    // avoid timeouts
    require BORROWED_PRECISION() == 1 || BORROWED_PRECISION() == 1000;
    require COLLATERAL_PRECISION() == 1 || COLLATERAL_PRECISION() == 1000;

    require _for != currentContract;
    require e.msg.sender != currentContract;

    mathint userInCoinBalanceBefore;
    mathint userOutCoinBalanceBefore;
    mathint contractInCoinBalanceBefore;
    mathint contractOutCoinBalanceBefore;

    mathint userInCoinBalanceAfter;
    mathint userOutCoinBalanceAfter;
    mathint contractInCoinBalanceAfter;
    mathint contractOutCoinBalanceAfter;
    // mathint totalXBefore = total_x * BORROWED_PRECISION();

    if (i == 0) {
        userInCoinBalanceBefore = tokenBalance[stablecoin][e.msg.sender];
        contractInCoinBalanceBefore = tokenBalance[stablecoin][currentContract];
        userOutCoinBalanceBefore = tokenBalance[collateraltoken][_for];
        contractOutCoinBalanceBefore = tokenBalance[collateraltoken][currentContract];
    } else {
        userInCoinBalanceBefore = tokenBalance[collateraltoken][e.msg.sender];
        contractInCoinBalanceBefore = tokenBalance[collateraltoken][currentContract];
        userOutCoinBalanceBefore = tokenBalance[stablecoin][_for];
        contractOutCoinBalanceBefore = tokenBalance[stablecoin][currentContract];
    }

    uint256[2] traded;
    traded = exchange(e, i, j, in_amount, min_amount, _for);

    if (i == 0) {
        userInCoinBalanceAfter = tokenBalance[stablecoin][e.msg.sender];
        contractInCoinBalanceAfter = tokenBalance[stablecoin][currentContract];
        userOutCoinBalanceAfter = tokenBalance[collateraltoken][_for];
        contractOutCoinBalanceAfter = tokenBalance[collateraltoken][currentContract];
    } else {
        userInCoinBalanceAfter = tokenBalance[collateraltoken][e.msg.sender];
        contractInCoinBalanceAfter = tokenBalance[collateraltoken][currentContract];
        userOutCoinBalanceAfter = tokenBalance[stablecoin][_for];
        contractOutCoinBalanceAfter = tokenBalance[stablecoin][currentContract];
    }

    // satisfy userOutCoinBalanceAfter > userOutCoinBalanceBefore;
    mathint userInCoin = userInCoinBalanceBefore - userInCoinBalanceAfter;
    mathint userOutCoin = userOutCoinBalanceAfter - userOutCoinBalanceBefore;
    mathint contractInCoin = contractInCoinBalanceAfter - contractInCoinBalanceBefore;
    mathint contractOutCoin = contractOutCoinBalanceBefore - contractOutCoinBalanceAfter;

    assert userInCoin >= 0, "user in coin change";
    assert userOutCoin >= 0, "user out coin change";
    assert userInCoin == contractInCoin, "in coin";
    assert userOutCoin == contractOutCoin, "out coin";

    if (userInCoin == 0) {
        assert userOutCoin == 0, "wrong out";
    } else {
        assert userInCoin <= to_mathint(in_amount), "wrong in amount";
        assert userOutCoin >= to_mathint(min_amount), "wrong out amount";
    }
    assert userInCoin == to_mathint(traded[0]), "return value doesn't match in";
    assert userOutCoin == to_mathint(traded[1]), "return value doesn't match out";
}

rule integrityOfExchangeDY_balance(uint256 i, uint256 j, uint256 out_amount, uint256 max_amount, address _for) {
    env e;
    address stablecoin = BORROWED_TOKEN();
    address collateraltoken = COLLATERAL_TOKEN();

    require (i == 0 && j == 1) || (i == 1 && j == 0);
    // the rule only holds if the liquidity mining callback doesn't mess up balances; we assume here that there is none.
    require liquidity_mining_callback() == 0;

    // avoid timeouts
    require BORROWED_PRECISION() == 1 || BORROWED_PRECISION() == 1000;
    require COLLATERAL_PRECISION() == 1 || COLLATERAL_PRECISION() == 1000;


    require _for != currentContract;
    require e.msg.sender != currentContract;

    mathint userInCoinBalanceBefore;
    mathint userOutCoinBalanceBefore;
    mathint contractInCoinBalanceBefore;
    mathint contractOutCoinBalanceBefore;

    mathint userInCoinBalanceAfter;
    mathint userOutCoinBalanceAfter;
    mathint contractInCoinBalanceAfter;
    mathint contractOutCoinBalanceAfter;

    if (i == 0) {
        userInCoinBalanceBefore = tokenBalance[stablecoin][e.msg.sender];
        contractInCoinBalanceBefore = tokenBalance[stablecoin][currentContract];
        userOutCoinBalanceBefore = tokenBalance[collateraltoken][_for];
        contractOutCoinBalanceBefore = tokenBalance[collateraltoken][currentContract];
    } else {
        userInCoinBalanceBefore = tokenBalance[collateraltoken][e.msg.sender];
        contractInCoinBalanceBefore = tokenBalance[collateraltoken][currentContract];
        userOutCoinBalanceBefore = tokenBalance[stablecoin][_for];
        contractOutCoinBalanceBefore = tokenBalance[stablecoin][currentContract];
    }

    uint256[2] traded;
    traded = exchange_dy(e, i, j, out_amount, max_amount, _for);

    if (i == 0) {
        userInCoinBalanceAfter = tokenBalance[stablecoin][e.msg.sender];
        contractInCoinBalanceAfter = tokenBalance[stablecoin][currentContract];
        userOutCoinBalanceAfter = tokenBalance[collateraltoken][_for];
        contractOutCoinBalanceAfter = tokenBalance[collateraltoken][currentContract];
    } else {
        userInCoinBalanceAfter = tokenBalance[collateraltoken][e.msg.sender];
        contractInCoinBalanceAfter = tokenBalance[collateraltoken][currentContract];
        userOutCoinBalanceAfter = tokenBalance[stablecoin][_for];
        contractOutCoinBalanceAfter = tokenBalance[stablecoin][currentContract];
    }

    // satisfy userOutCoinBalanceAfter > userOutCoinBalanceBefore;
    mathint userInCoin = userInCoinBalanceBefore - userInCoinBalanceAfter;
    mathint userOutCoin = userOutCoinBalanceAfter - userOutCoinBalanceBefore;
    mathint contractInCoin = contractInCoinBalanceAfter - contractInCoinBalanceBefore;
    mathint contractOutCoin = contractOutCoinBalanceBefore - contractOutCoinBalanceAfter;

    assert userInCoin >= 0, "user in coin change";
    assert userOutCoin >= 0, "user out coin change";
    assert userInCoin == contractInCoin, "in coin";
    assert userOutCoin == contractOutCoin, "out coin";
    if (userInCoin == 0) {
        assert userOutCoin == 0, "wrong out";
    } else {
        assert userInCoin <= to_mathint(max_amount), "wrong in amount";
        assert userOutCoin >= to_mathint(out_amount), "wrong out amount";
    }
    assert userInCoin == to_mathint(traded[0]), "return value doesn't match in";
    assert userOutCoin == to_mathint(traded[1]), "return value doesn't match out";
}

rule exchangeDoesNotChangeUserShares(uint256 i, uint256 j, uint256 in_amount, uint256 min_amount) {
    env e;
    require (i == 0 && j == 1) || (i == 1 && j == 0);

    address anyUser;

    mathint sharesBefore_n1 = user_n1[anyUser];
    mathint sharesBefore_n2 = user_n2[anyUser];

    exchange(e, i, j, in_amount, min_amount);

    mathint sharesAfter_n1 = user_n1[anyUser];
    mathint sharesAfter_n2 = user_n2[anyUser];

    assert sharesBefore_n1 == sharesAfter_n1;
    assert sharesBefore_n2 == sharesAfter_n2;

    // satisfy true;
}

rule integrityOfExchange_bands(uint256 i, uint256 j, uint256 in_amount, uint256 min_amount, address _for) {
    env e;
    address stablecoin = BORROWED_TOKEN();
    address collateraltoken = COLLATERAL_TOKEN();

    require (i == 0 && j == 1) || (i == 1 && j == 0);
    // the rule only holds if the liquidity mining callback doesn't mess up balances; we assume here that there is none.
    require liquidity_mining_callback() == 0;

    // avoid timeouts
    require BORROWED_PRECISION() == 1 || BORROWED_PRECISION() == 1000;
    require COLLATERAL_PRECISION() == 1 || COLLATERAL_PRECISION() == 1000;

    require _for != currentContract;
    require e.msg.sender != currentContract;

    mathint totalXBefore = total_x; // should correspond to stablecoin
    mathint totalYBefore = total_y; // should correspond to collateral token

    mathint stablecoinBalanceBefore = tokenBalance[stablecoin][currentContract];
    mathint collateralBalanceBefore = tokenBalance[collateraltoken][currentContract];

    uint256[2] traded;
    traded = exchange(e, i, j, in_amount, min_amount, _for);

    mathint totalXAfter = total_x; // should correspond to stablecoin
    mathint totalYAfter = total_y; // should correspond to collateral token

    mathint stablecoinDiff = tokenBalance[stablecoin][currentContract] - stablecoinBalanceBefore;
    mathint collateralDiff = tokenBalance[collateraltoken][currentContract] - collateralBalanceBefore;

    // Check that the actual amount of stablecoin gained is at least what we accounted for in total_x.
    // Similarly for collateral.  It may be greater because of rounding errors.
    assert stablecoinDiff * BORROWED_PRECISION() >= totalXAfter - totalXBefore;
    assert collateralDiff * COLLATERAL_PRECISION() >= totalYAfter - totalYBefore;
    assert to_mathint(traded[0]) == (i == 0 ? stablecoinDiff : collateralDiff);
    assert to_mathint(traded[1]) == (j == 0 ? - stablecoinDiff : - collateralDiff);
}

rule integrityOfExchangeDY_bands(uint256 i, uint256 j, uint256 out_amount, uint256 max_amount, address _for) {
    env e;
    address stablecoin = BORROWED_TOKEN();
    address collateraltoken = COLLATERAL_TOKEN();

    require (i == 0 && j == 1) || (i == 1 && j == 0);
    // the rule only holds if the liquidity mining callback doesn't mess up balances; we assume here that there is none.
    require liquidity_mining_callback() == 0;

    // avoid timeouts
    require BORROWED_PRECISION() == 1 || BORROWED_PRECISION() == 1000;
    require COLLATERAL_PRECISION() == 1 || COLLATERAL_PRECISION() == 1000;

    require _for != currentContract;
    require e.msg.sender != currentContract;

    mathint totalXBefore = total_x; // should correspond to stablecoin
    mathint totalYBefore = total_y; // should correspond to collateral token

    mathint stablecoinBalanceBefore = tokenBalance[stablecoin][currentContract];
    mathint collateralBalanceBefore = tokenBalance[collateraltoken][currentContract];

    uint256[2] traded;
    traded = exchange_dy(e, i, j, out_amount, max_amount, _for);

    mathint totalXAfter = total_x; // should correspond to stablecoin
    mathint totalYAfter = total_y; // should correspond to collateral token

    mathint stablecoinDiff = tokenBalance[stablecoin][currentContract] - stablecoinBalanceBefore;
    mathint collateralDiff = tokenBalance[collateraltoken][currentContract] - collateralBalanceBefore;

    // Check that the actual amount of stablecoin gained is at least what we accounted for in total_x.
    // Similarly for collateral.  It may be greater because of rounding errors.
    assert stablecoinDiff * BORROWED_PRECISION() >= totalXAfter - totalXBefore, "total_x change matches balance change";
    assert collateralDiff * COLLATERAL_PRECISION() >= totalYAfter - totalYBefore, "total_y change matches balance change";
    assert to_mathint(traded[0]) == (i == 0 ? stablecoinDiff : collateralDiff), "in amount match return value";
    assert to_mathint(traded[1]) == (j == 0 ? - stablecoinDiff : - collateralDiff), "out amount match return value";
}

rule integrityOfExchange_invariant(uint256 i, uint256 j, uint256 in_amount, uint256 min_amount, address _for) {
    env e;

    require (i == 0 && j == 1) || (i == 1 && j == 0);

    require _for != currentContract;
    require e.msg.sender != currentContract;

    mathint ef = A(e);

    assert true;
}

/* This rule shows that exchange_dx allows trades where the trader is not fully paid */
rule exchange_dy_bad_trade {
    env e;
    uint256[2] traded;

    require liquidity_mining_callback() == 0;
    require BORROWED_PRECISION() == 1;
    require COLLATERAL_PRECISION() == 1;

    require e.msg.sender != currentContract;

    require active_band() == max_band();

    // request to buy 50 collateral for at most 3 stable
    traded = exchange_dy(e, 0, 1, 50, 3, e.msg.sender);

    // trader gets only 2 collateral and loses all 3 stable.
    satisfy traded[0] == 3 && traded[1] == 2;
}

rule get_rate_equals_set_rate {
    env e1;
    env e2;
    env e3;
    uint256 somerate;

    require e1.block.timestamp == e2.block.timestamp;
    require e2.block.timestamp == e3.block.timestamp;

    uint256 current_rate_mul = get_rate_mul(e1);
    uint256 set_rate_result = set_rate(e2, somerate);
    uint256 after_rate_mul = get_rate_mul(e1);

    assert current_rate_mul == set_rate_result;
    assert current_rate_mul == after_rate_mul;
}

rule admin_cannot_change_once_set(method f, env e, calldataarg arg) {
    address adminBefore = admin();
    require adminBefore != 0;

    f(e, arg);

    assert admin() == adminBefore;
}

rule cannot_change_totalxy(method f, env e, calldataarg arg) filtered {
    f -> !changes_totalxy(f)
} {
    mathint total_x_before = total_x;
    mathint total_y_before = total_y;

    f(e, arg);

    assert total_x == total_x_before;
    assert total_y == total_y_before;
}

rule cannot_change_balance(method f, env e, calldataarg arg) filtered {
    f -> !changes_balance(f)
} {
    address token;
    mathint balanceBefore = tokenBalance[token][currentContract];

    f(e, arg);

    assert balanceBefore == tokenBalance[token][currentContract];
}

/*
def exchange(i: uint256, j: uint256, in_amount: uint256, min_amount: uint256, _for: address = msg.sender) -> uint256[2]:
    """
    @notice Exchanges two coins, callable by anyone
    @param i Input coin index
    @param j Output coin index
    @param in_amount Amount of input coin to swap
    @param min_amount Minimal amount to get as output
    @param _for Address to send coins to
    @return Amount of coins given in/out
    """
    return self._exchange(i, j, in_amount, min_amount, _for, True)


@external
@nonreentrant('lock')
def exchange_dy(i: uint256, j: uint256, out_amount: uint256, max_amount: uint256, _for: address = msg.sender) -> uint256[2]:
 @notice Exchanges two coins, callable by anyone
    @param i Input coin index
    @param j Output coin index
    @param out_amount Desired amount of output coin to receive
    @param max_amount Maximum amount to spend (revert if more)
    @param _for Address to send coins to
    @return Amount of coins given in/out
    """


Borrowed token changes the same amount as total_x * precision (StableCoin)
Collateral token changes the same amount as total_y * precision

Rounding needs to be taken into account
*/
