using Stablecoin as stablecoin;
using CollateralToken as collateraltoken;
using AMM as amm;
using FactoryMock as factory;
using WETH as weth;

methods {
    // view:
    function factory() external returns (address) envfree;
    function amm() external returns (address) envfree;
    function collateral_token() external returns (address) envfree;
    function debt(address) external returns (uint256) envfree;
    function loan_exists(address) external returns (bool) envfree;
    function total_debt() external returns (uint256) envfree;
    function max_borrowable(uint256, uint256, uint256) external returns (uint256) envfree;
    function calculate_debt_n1(uint256, uint256, uint256) external returns (int256) => NONDET;
    function create_loan(uint256, uint256, uint256) external; // payable nonreentrant
    function create_loan_extended(uint256, uint256, uint256, address, uint256[]) external; // payable nonreentrant
    function add_collateral(uint256, address) external; // payable nonreentrant
    function remove_collateral(uint256, bool) external; // nonreentrant
    function borrow_more(uint256, uint256) external; // payable nonreentrant
    function repay(uint256, address, int256, bool) external; // nonreentrant
    function repay_extended(address, uint256[]) external;
    function health_calculator(address, int256, int256, bool, uint256) external returns (int256) envfree; // view
    function liquidate(address, uint256, bool) external;
    function liquidate_extended(address, uint256, uint256, bool, address, uint256[]) external;
    function tokens_to_liquidate(address, uint256) external returns (uint256);
    function health(address, bool) external returns (int256) envfree;
    function amm_price() external returns (uint256) envfree;
    function user_prices(address) external returns (uint256[2]) envfree;
    function user_state(address) external returns (uint256[4]) envfree;
    function set_amm_fee(uint256) external => NONDET;
    function set_amm_admin_fee(uint256) external => NONDET;
    function set_monetary_policy(address) external => NONDET;
    function set_borrowing_discounts(uint256, uint256) external => NONDET;
    function set_callback(address) external => NONDET;
    function admin_fees() external returns (uint256) envfree;
    function collect_fees() external returns (uint256) envfree;

    // Controller Getters:
    function minted() external returns (uint256) envfree;
    function redeemed() external returns (uint256) envfree;
    function AMM() external returns (address) envfree;

    // ControllerHarness:
    function get_initial_debt(address) external returns (uint256) envfree;
    function get_total_initial_debt() external returns (uint256) envfree;
    function increaseDiscount(address, uint256) external envfree;
    function get_liquidation_discounts(address) external returns (uint256) envfree;
    function get_user_rate_mul(address) external returns (uint256) envfree;

    // AMM:
    function _.withdraw(address user, uint256 frac) external => AMM_withdraw(user, frac) expect (uint256[2]);
    function _.deposit_range(address addr, uint256 amount, int256 n1, int256 n2) external =>
       AMM_deposit_range(addr, amount, n1, n2) expect void;
    function AMM.read_user_tick_numbers(address user) external returns (int256[2]) => AMM_read_user_tick_numbers(user);
    function _.log2(uint256) external => NONDET;
    function _.active_band() external => AMM_active_band expect (int256);
    function _.active_band_with_skip() external => AMM_active_band_with_skip expect (int256);
    function _.admin_fees_x() external => AMM_admin_fees_x expect (uint256);
    function _.admin_fees_y() external => AMM_admin_fees_y expect (uint256);
    function _.reset_admin_fees() external => AMM_reset_admin_fees() expect void;
    function _.fee_receiver() external => FACTORY_fee_receiver expect address;

    // MonetaryPolicy:
    function _.rate_write() external => CONSTANT;

    // havocing AMM:
    function _.get_rate_mul() external => CONSTANT;

    // Controller heavy math:
    function _._calculate_debt_n1(uint256, uint256, uint256) external => NONDET;

    // AMM - LMGauge:
    function _.callback_collateral_shares(int256, uint256[]) external => NONDET;
    function _.callback_user_shares(address, int256, uint256[]) external => NONDET;

    function _.transfer(address to, uint256 amount) external with (env e) => transferFromSummary(calledContract, e.msg.sender, to, amount) expect bool;
    function _.transferFrom(address from, address to, uint256 amount) external => transferFromSummary(calledContract, from, to, amount) expect bool;
}

ghost mapping(address => int256) user_n1s;
ghost mapping(address => int256) user_n2s;
ghost int256 AMM_active_band;
ghost int256 AMM_active_band_with_skip;
ghost uint256 AMM_admin_fees_x;
ghost uint256 AMM_admin_fees_y;
ghost address FACTORY_fee_receiver;

function AMM_read_user_tick_numbers(address user) returns int256[2] {
    int256[2] ns;

    require ns[0] <= ns[1]; // proved in AMM.vy invariant.
    require ns[0] == user_n1s[user];
    require ns[1] == user_n2s[user];

    return ns;
}

function AMM_reset_admin_fees() {
    withdrawn_stable = withdrawn_stable + AMM_admin_fees_x;
    withdrawn_collateral = withdrawn_collateral + AMM_admin_fees_y;
    AMM_admin_fees_x = 0;
    AMM_admin_fees_y = 0;
}

ghost mathint withdrawn_collateral;
ghost mathint withdrawn_stable;
ghost mathint deposited_collateral;
ghost mapping(address => mapping(address => mathint)) tokenBalance;

function AMM_withdraw(address user, uint256 frac) returns uint256[2] {
    uint256[2] result;
    require user_n1s[user] > AMM_active_band_with_skip => result[0] == 0;
    withdrawn_stable = withdrawn_stable + result[0];
    withdrawn_collateral = withdrawn_collateral + result[1];
    havoc AMM_admin_fees_x;
    havoc AMM_admin_fees_y;
    return result;
}

function AMM_deposit_range(address user, uint256 amount, int256 n1, int256 n2) {
    deposited_collateral = deposited_collateral + amount;
}

function transferFromSummary(address token, address from, address to, uint256 amount) returns bool {
    require tokenBalance[token][from] >= to_mathint(amount);
    tokenBalance[token][from] = tokenBalance[token][from] - amount;
    tokenBalance[token][to] = tokenBalance[token][to] + amount;
    return true;
}

rule balanceAMM(method f, env e, calldataarg args) {
    mathint ammStableBefore = tokenBalance[stablecoin][amm];
    mathint ammCollateralBefore = tokenBalance[collateraltoken][amm];
    withdrawn_collateral = 0;
    withdrawn_stable = 0;
    deposited_collateral = 0;

    require e.msg.sender != amm;
    require e.msg.sender != stablecoin;
    require e.msg.sender != collateraltoken;
    require stablecoin != collateraltoken;
    require amm != FACTORY_fee_receiver;

    // the AMM never has a loan
    require !loan_exists(amm);

    f(e, args);

    mathint ammStableAfter = tokenBalance[stablecoin][amm];
    mathint ammCollateralAfter = tokenBalance[collateraltoken][amm];

    assert ammStableAfter == ammStableBefore - withdrawn_stable;
    assert ammCollateralAfter == ammCollateralBefore + deposited_collateral - withdrawn_collateral;
}
