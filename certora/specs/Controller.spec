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

    // ControllerHarness:
    function get_initial_debt(address) external returns (uint256) envfree;
    function get_total_initial_debt() external returns (uint256) envfree;
    function increaseDiscount(address, uint256) external envfree;
    function get_liquidation_discounts(address) external returns (uint256) envfree;
    function get_user_rate_mul(address) external returns (uint256) envfree;

    // AMM:
    function AMM.A() external returns (uint256);
    function AMM.get_p() external returns (uint256);
    function AMM.get_base_price() external returns (uint256);
    // function AMM.active_band() external returns (int256);
    function AMM.active_band_with_skip() external returns (int256);
    // function AMM.p_oracle_up(int256) external returns (uint256);
    function AMM.p_oracle_down(int256) external returns (uint256);
    function AMM.deposit_range(address, uint256, int256, int256) external;
    function AMM.read_user_tick_numbers(address) external returns (int256[2]);
    function AMM.get_sum_xy(address) external returns (uint256[2]);
    function AMM.withdraw(address, uint256) external returns (uint256[2]) => NONDET; // nonpayable
    // function AMM.get_x_down(address) external returns (uint256);
    // function AMM.get_rate_mul() external returns (uint256);
    function AMM.set_rate(uint256) external returns (uint256); // nonpayable
    function AMM.set_fee(uint256) external; // nonpayable
    function AMM.set_admin_fee(uint256) external; // nonpayable
    function AMM.price_oracle() external returns (uint256) => CONSTANT;
    function AMM.can_skip_bands(int256) external returns (bool);
    // function set_price_oracle(PriceOracle) external; // nonpayable
    function AMM.admin_fees_x() external returns (uint256);
    function AMM.admin_fees_y() external returns (uint256);
    function AMM.reset_admin_fees() external; // nonpayable
    function AMM.has_liquidity(address) external returns (bool) envfree;
    function AMM.bands_x(int256) external returns (uint256);
    function AMM.bands_y(int256) external returns (uint256);
    function AMM.set_callback(address) external => NONDET; // nonpayable
    

    // AMM Havocing:
    function AMM.active_band() external returns (int256) => NONDET;
    function AMM.set_admin(address) external => NONDET;
    function AMM.exchange_dy(uint256,uint256,uint256,uint256) external returns (uint256[2]) => NONDET;
    function AMM.exchange(uint256,uint256,uint256,uint256,address) external returns (uint256[2]) => NONDET;
    function AMM.get_dxdy(uint256,uint256,uint256) external returns (uint256, uint256) => NONDET;
    function AMM.get_x_down(address) external returns (uint256) => NONDET;
    function AMM.get_dydx(uint256,uint256,uint256) external returns (uint256, uint256) => NONDET;
    function AMM.get_dy(uint256,uint256,uint256) external returns (uint256) => NONDET;
    function AMM.get_y_up(address) external returns (uint256) => NONDET;
    function AMM.exchange_dy(uint256,uint256,uint256,uint256,address) external returns (uint256[2]) => NONDET;
    function AMM.get_amount_for_price(uint256) external returns (uint256, bool) => NONDET;
    function AMM.exchange(uint256,uint256,uint256,uint256) external returns (uint256[2]) => NONDET;
    function AMM.p_oracle_up(int256) external returns (uint256) => NONDET;


    // STABLECOIN:
    function Stablecoin.balanceOf(address) external returns (uint256) envfree;
    function Stablecoin.totalSupply() external returns (uint256) envfree;

    // CollateralToken:
    function CollateralToken.balanceOf(address) external returns (uint256);
    function CollateralToken.totalSupply() external returns (uint256);

    // Factory:
    function FactoryMock.stablecoin() external returns address envfree => getStablecoin();
    function FactoryMock.admin() external returns address envfree => NONDET;
    function FactoryMock.fee_receiver() external returns address envfree => getFeeReceiver();
    function FactoryMock.WETH() external returns address envfree => getWeth();

    // MonetaryPolicy:
    function _.rate_write() external => CONSTANT;
    
    // havocing AMM:
    function _.get_rate_mul() external => CONSTANT;

    // Controller heavy math:
    function _._calculate_debt_n1(uint256, uint256, uint256) external => NONDET;
    function FactoryMock.log2(uint256 _x) external returns int256 => logTwo(_x);

    // AMM - LMGauge:
    function _.callback_collateral_shares(int256, uint256[]) external => NONDET;
    function _.callback_user_shares(address, int256, uint256[]) external => NONDET;
}

ghost address factoryAdmin;
ghost address feeReceiver;
ghost mathint sumAllDebt;
ghost mathint nLoans;

ghost mapping(address => uint256) loansInitialDebt {
    init_state axiom forall address user . loansInitialDebt[user] == 0;
}

ghost mapping(address => uint256) loansRateMul {
    init_state axiom forall address user . loansRateMul[user] == 0;
}

ghost mapping(uint256 => address) loansMirror {
    init_state axiom forall uint256 indx . loansMirror[indx] == 0;
}

ghost mapping(address => uint256) loansIxMirror {
    init_state axiom forall address user . loansIxMirror[user] == 0;
}

ghost mapping(uint256 => int256) log2Sum {
    axiom ((forall uint256 index1 . forall uint256 index2 . log2Sum[index1] <= log2Sum[index2]) && log2Sum[1] == 0 && log2Sum[2] == 1);
}

hook Sstore loans[INDEX uint256 indx] address newUser (address oldUser) STORAGE {
    // nLoans = nLoans + 1;
    loansMirror[indx] = newUser;
}

hook Sload address user loans[INDEX uint256 indx] STORAGE {
    require  loansMirror[indx] == user;
}

hook Sstore loan_ix[KEY address user] uint256 newIndex (uint256 oldIndex) STORAGE {
    loansIxMirror[user] = newIndex;
}

hook Sload uint256 loanIndex loan_ix[KEY address user] STORAGE {
    require  loansIxMirror[user] == loanIndex;
}

hook Sstore loan[KEY address user].initial_debt uint256 newInitialDebt (uint256 oldInitialDebt) STORAGE {
    sumAllDebt = sumAllDebt - oldInitialDebt + newInitialDebt;
    loansInitialDebt[user] = newInitialDebt;
}

hook Sload uint256 initialDebt loan[KEY address user].initial_debt STORAGE {
    require  loansInitialDebt[user] == initialDebt;
}

hook Sstore loan[KEY address user].rate_mul uint256 newRateMul (uint256 oldRateMul) STORAGE {
    loansRateMul[user] = newRateMul;
}

hook Sload uint256 newRateMul loan[KEY address user].rate_mul STORAGE {
    require  loansRateMul[user] == newRateMul;
}

function getFactoryAdmin() returns address {
    return factoryAdmin;
}

function getFeeReceiver() returns address {
    return feeReceiver;
}

function getStablecoin() returns address {
    return stablecoin;
}

function getWeth() returns address {
    return weth;
}

function logTwo(uint256 x) returns int256 { 
    return log2Sum[x];
}

invariant totalDebtEqSumAllDebts()
    to_mathint(get_total_initial_debt()) == sumAllDebt
    { 
        preserved with (env e) { 
            require e.msg.sender != currentContract; 
        } 
    }

invariant loansAndLoansIxInverse(address user)
    loansMirror[loansIxMirror[user]] == user;

invariant mintedPlusRedeemedEqTotalSupply() 
    to_mathint(total_debt()) == minted() - redeemed(); // maybe stablecoin.balaceOf(currentContratc / AMM) == minted() + redeemed();?

invariant loansAndShares(address user)
    loan_exists(user) <=> amm.has_liquidity(user)
    { 
        preserved with (env e) { 
            require e.msg.sender != currentContract; 
        } 
    }

rule integrityOfCreateLoan(uint256 collateralAmaount, uint256 debt, uint256 N) {
    env e;
    require e.msg.sender != currentContract;
    bool loanExsitBefore = loan_exists(e.msg.sender);
    mathint mintedBefore = minted();
    mathint stablecoinBalanceBefore = stablecoin.balanceOf(e.msg.sender);
    require stablecoinBalanceBefore + debt < max_uint256;

    create_loan(e, collateralAmaount, debt, N);

    bool loanExsitAfter = loan_exists(e.msg.sender);
    uint256 initialDebt = get_initial_debt(e.msg.sender);
    mathint mintedAfter = minted();
    mathint stablecoinBalanceAfter = stablecoin.balanceOf(e.msg.sender);

    assert !loanExsitBefore;
    assert debt > 0 => loanExsitAfter && loansMirror[loansIxMirror[e.msg.sender]] == e.msg.sender; // need to have debt > 0 because we summarized _calculate_debt_n1 which checks if debt > 0.
    assert debt == initialDebt;
    assert mintedAfter == mintedBefore + debt;
    assert stablecoinBalanceAfter == stablecoinBalanceBefore + debt;
}

rule integrityOfAddCollateral(uint256 collateral, address _for) {
    env e;

    mathint debtBefore = get_initial_debt(_for);
    mathint senderCollateralBalanceBefore = collateraltoken.balanceOf(e, e.msg.sender);
    mathint ammCollateralBalanceBefore = collateraltoken.balanceOf(e, amm);
    mathint totalDebtBefore = total_debt();

    add_collateral(e, collateral, _for);

    mathint debtAfter = get_initial_debt(_for);
    mathint senderCollateralBalanceAfter = collateraltoken.balanceOf(e, e.msg.sender);
    mathint ammCollateralBalanceAfter = collateraltoken.balanceOf(e, amm);
    mathint totalDebtAfter = total_debt();

    assert debtBefore == debtAfter && totalDebtBefore == totalDebtAfter;
    assert senderCollateralBalanceBefore == senderCollateralBalanceAfter + collateral;
    assert ammCollateralBalanceBefore == ammCollateralBalanceAfter - collateral;
}

rule integrityOfRemoveCollateral(uint256 collateral, bool use_eth) {
    env e;

    mathint debtBefore = get_initial_debt(e.msg.sender);
    mathint senderCollateralBalanceBefore = collateraltoken.balanceOf(e, e.msg.sender);
    mathint ammCollateralBalanceBefore = collateraltoken.balanceOf(e, amm);
    mathint totalDebtBefore = total_debt();

    remove_collateral(e, collateral, use_eth);

    mathint debtAfter = get_initial_debt(e.msg.sender);
    mathint senderCollateralBalanceAfter = collateraltoken.balanceOf(e, e.msg.sender);
    mathint ammCollateralBalanceAfter = collateraltoken.balanceOf(e, amm);
    mathint totalDebtAfter = total_debt();

    assert debtBefore == debtAfter && totalDebtBefore == totalDebtAfter;
    assert senderCollateralBalanceAfter == senderCollateralBalanceBefore + collateral;
    assert ammCollateralBalanceAfter == ammCollateralBalanceBefore - collateral;
}

rule integrityOfBorrowMore(uint256 collateral, uint256 debt) {
    env e;
    require e.msg.sender != 0;
    mathint mintedBefore = minted();
    mathint debtBefore = get_initial_debt(e.msg.sender);
    mathint senderCollateralBalanceBefore = collateraltoken.balanceOf(e, e.msg.sender);
    mathint stablecoinBalanceBefore = stablecoin.balanceOf(e.msg.sender);
    mathint totalDebtBefore = total_debt();

    borrow_more(e, collateral, debt);

    mathint mintedAfter = minted();
    mathint debtAfter = get_initial_debt(e.msg.sender);
    mathint senderCollateralBalanceAfter = collateraltoken.balanceOf(e, e.msg.sender);
    mathint stablecoinBalanceAfter = stablecoin.balanceOf(e.msg.sender);
    mathint totalDebtAfter = total_debt();

    assert mintedAfter == mintedBefore + debt;
    assert debt > 0 => senderCollateralBalanceAfter == senderCollateralBalanceBefore - collateral;
    assert debtBefore <= debtAfter && totalDebtBefore <= totalDebtAfter;
    assert stablecoinBalanceAfter == stablecoinBalanceBefore + debt;
}

rule borrowMoreCumulative(uint256 collateral1, uint256 debt1, uint256 collateral2, uint256 debt2) {
    env e;
    require collateral1 + collateral2 < max_uint256;
    require debt1 + debt2 < max_uint256;
    uint256 combinedCollateral = assert_uint256(collateral1 + collateral2);
    uint256 combinedDebt = assert_uint256(debt1 + debt2);

    storage initialStorage = lastStorage;

    borrow_more(e, collateral1, debt1);
    borrow_more(e, collateral2, debt2);

    mathint mintedSeperate = minted();
    mathint debtSeperate = get_initial_debt(e.msg.sender);
    mathint senderCollateralBalanceSeperate = collateraltoken.balanceOf(e, e.msg.sender);
    mathint totalDebtSeperate = total_debt();

    borrow_more(e, combinedCollateral, combinedDebt) at initialStorage;

    mathint mintedCombined = minted();
    mathint debtCombined = get_initial_debt(e.msg.sender);
    mathint senderCollateralBalanceCombined = collateraltoken.balanceOf(e, e.msg.sender);
    mathint totalDebtCombined = total_debt();

    assert mintedSeperate == mintedCombined;
    assert debtSeperate == debtCombined;
    assert totalDebtSeperate == totalDebtCombined;
    assert senderCollateralBalanceSeperate == senderCollateralBalanceCombined;
}

// debt, health and stablecoin balance are updated correctly
rule integrityOfLiquidate(address user, uint256 min_x, bool use_eth) {
    env e;

    mathint liquidatorStableCoinBalanceBefore = stablecoin.balanceOf(e.msg.sender);
    mathint debtBefore = get_initial_debt(user);
    int256 userHealthFactorBefore = health(user, true);

    liquidate(e, user, min_x, use_eth);

    mathint liquidatorStableCoinBalanceAfter = stablecoin.balanceOf(e.msg.sender);
    mathint debtAfter = get_initial_debt(user);
    int256 userHealthFactorAfter = health(user, true);

    assert userHealthFactorBefore < userHealthFactorAfter;
    assert liquidatorStableCoinBalanceAfter <= liquidatorStableCoinBalanceBefore;
}

rule onlyLiquidateCanDecreaseShares(method f, address user) 
    filtered { f -> f.contract == currentContract } {
    env e;
    calldataarg args;
    require e.msg.sender != user;

    bool hasLiquidityBefore = amm.has_liquidity(user);

    f(e, args);

    bool hasLiquidityAfter = amm.has_liquidity(user);

    assert hasLiquidityBefore && !hasLiquidityAfter => 
        (f.selector == sig:liquidate(address, uint256, bool).selector || f.selector == sig:liquidate_extended(address, uint256, uint256, bool, address, uint256[]).selector);
}

// changing liquidation_discount doesnt affect existing loans
rule liquidationDiscountDoesntAffectExistingLoans(address user, address liquidate_discount, uint256 increaseByAmount) {
    env e; 

    uint256 initialDebtBefore = get_initial_debt(user);
    uint256 rateMulBefore = get_user_rate_mul(user);

    increaseDiscount(user, increaseByAmount);

    uint256 initialDebtAfter = get_initial_debt(user);
    uint256 rateMulAfter = get_user_rate_mul(user);

    assert initialDebtBefore == initialDebtAfter;
    assert rateMulBefore == rateMulAfter;
}

// discount should only be changed by the user itself
rule onlyUserCanChangeHisOwnLiquidationDiscount(method f, address user) 
    filtered { f -> f.contract == currentContract } {
    env e;
    calldataarg args;

    require e.msg.sender != user;

    uint256 userLiquidationDiscountBefore = get_liquidation_discounts(user);

    f(e, args);

    uint256 userLiquidationDiscountAfter = get_liquidation_discounts(user);

    assert userLiquidationDiscountBefore == userLiquidationDiscountAfter;
}

rule anyPositionCanBeClosed(method f, address user) 
    filtered { f -> f.selector == sig:repay(uint256, address, int256, bool).selector ||
                    f.selector == sig:repay_extended(address, uint256[]).selector || 
                    f.selector == sig:liquidate(address, uint256, bool).selector ||
                    f.selector == sig:liquidate_extended(address, uint256, uint256, bool, address, uint256[]).selector } {
    env e;
    calldataarg args;

    mathint debtBefore = get_initial_debt(user);
    require debtBefore > 0;

    f(e, args);

    mathint debtAfter = get_initial_debt(user);

    satisfy debtAfter == 0;
}

/***********************************/
/*       NOT PASSING RULES         */
/***********************************/

rule integrityOfRepay(uint256 debtToRepay, address _for, int256 max_active_band, bool use_eth) {
    env e;
    require e.msg.sender != currentContract && e.msg.sender != amm;
    require use_eth == false;
    mathint debtBefore = get_initial_debt(_for);
    mathint stablecoinBalanceBefore = stablecoin.balanceOf(e.msg.sender);
    mathint ammStablecoinBalanceBefore = stablecoin.balanceOf(amm);
    mathint redeemedBefore = redeemed();

    repay(e, debtToRepay, _for, max_active_band, use_eth);

    mathint debtAfter = get_initial_debt(_for);
    mathint stablecoinBalanceAfter = stablecoin.balanceOf(e.msg.sender);
    mathint ammStablecoinBalanceafter = stablecoin.balanceOf(amm);
    mathint redeemedAfter = redeemed();

    if (debtBefore > to_mathint(debtToRepay)) {
        assert debtAfter <= debtBefore;
        assert stablecoinBalanceAfter <= stablecoinBalanceBefore - debtToRepay;
        assert redeemedAfter == redeemedBefore + debtToRepay;
    } else {
        assert debtAfter == 0;
        assert stablecoinBalanceAfter == stablecoinBalanceBefore - debtBefore + (ammStablecoinBalanceBefore - ammStablecoinBalanceafter);
        assert redeemedAfter == redeemedBefore + debtBefore;
    }
}

rule repayCumulative(uint256 debtToRepay1, uint256 debtToRepay2, address _for, int256 max_active_band, bool use_eth) {
    env e;
    require debtToRepay1 + debtToRepay2 < max_uint256;
    uint256 combinedDebtToRepay = assert_uint256(debtToRepay1 + debtToRepay2);

    storage initialStorage = lastStorage;

    repay(e, debtToRepay1, _for, max_active_band, use_eth);
    repay(e, debtToRepay2, _for, max_active_band, use_eth);

    mathint debtSeperate = get_initial_debt(_for);
    mathint stablecoinBalanceSeperate = stablecoin.balanceOf(e.msg.sender);
    mathint redeemedSeperate = redeemed();

    repay(e, combinedDebtToRepay, _for, max_active_band, use_eth) at initialStorage;

    mathint debtCombined = get_initial_debt(_for);
    mathint stablecoinBalanceCombined = stablecoin.balanceOf(e.msg.sender);
    mathint redeemedCombined = redeemed();

    assert debtSeperate == debtCombined;
    assert stablecoinBalanceSeperate == stablecoinBalanceCombined;
    assert redeemedSeperate == redeemedCombined;
}

// should work only with liquidate_extended (when partially liquidating)
rule liquidateCumulative(address user, uint256 min_x1, uint256 min_x2, bool use_eth) {
    env e;
    require min_x1 + min_x2 < max_uint256;
    uint256 combinedMinX = assert_uint256(min_x1 + min_x2);

    storage initialStorage = lastStorage;

    liquidate(e, user, min_x1, use_eth);
    liquidate(e, user, min_x2, use_eth);

    mathint liquidatorStableCoinBalanceSeperate = stablecoin.balanceOf(e.msg.sender);
    mathint debtSeperate = get_initial_debt(user);

    liquidate(e, user, combinedMinX, use_eth) at initialStorage;

    mathint liquidatorStableCoinBalanceCombined = stablecoin.balanceOf(e.msg.sender);
    mathint debtCombined = get_initial_debt(user);

    assert liquidatorStableCoinBalanceSeperate == liquidatorStableCoinBalanceCombined;
    assert debtSeperate == debtCombined;
}

// maybe have a case for the repay function (someone pays user loan)
rule noReducerToOther(method f, address user) 
    filtered { f -> f.contract == currentContract } {
    env e;
    
    calldataarg args;

    require e.msg.sender != user;
    uint256 userBalanceBefore = collateraltoken.balanceOf(e, user);

    f(e, args);

    uint256 userBalanceAfter = collateraltoken.balanceOf(e, user);

    assert userBalanceBefore >= userBalanceAfter;
}

rule liquidateOnlyIfHealthFactorNegative(address user, uint256 min_x, bool use_eth) {
    env e;

    int256 healthFactor = health(user, true);

    liquidate(e, user, min_x, use_eth);

    assert healthFactor < 0;
}


// rule discountEffectiveness(address user, uint256 increaseAmount, uint256 min_x, bool use_eth) {
//     env e;
//     require use_eth == false;

//     uint256 discountBefore = get_liquidation_discounts(user);

//     require discountBefore + increaseAmount < max_uint256;

//     storage initialStorage = lastStorage;

//     liquidate(e, user, min_x, use_eth);

//     mathint liquidatorStableCoinBalanceAfter = stablecoin.balanceOf(e.msg.sender);
//     mathint debtAfter = get_initial_debt(user);
//     int256 userHealthFactorAfter = health(user, true);

//     increaseDiscount(user, amount) at lastStorage;

//     liquidate(e, user, min_x, use_eth);

//     mathint liquidatorStableCoinBalanceAfterIncreased = stablecoin.balanceOf(e.msg.sender);
//     mathint debtAfterIncreased = get_initial_debt(user);
//     int256 userHealthFactorAfterIncreased = health(user, true);

// }


// // can always pay your debt.
// rule repayReverting() {}


