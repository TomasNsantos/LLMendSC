pragma solidity >=0.4.22 <0.6.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v2.3.0/contracts/math/SafeMath.sol";

contract BecToken is PausableToken {
    using SafeMath for uint256;

    string public name = "BeautyChain";
    string public symbol = "BEC";
    string public version = "1.0.1";
    uint8 public decimals = 18;

    mapping(address => uint256) public lockedUntil;
    mapping(address => uint256) private ethBalances;

    constructor() public {
        totalSupply = 7000000000 * (10 ** uint256(decimals));
        balances[msg.sender] = totalSupply;
    }

    fallback() external {
        revert();
    }

    // Multi-send tokens to multiple recipients
    function multiSend(address[] memory recipients, uint256 amount) public whenNotPaused returns (bool) {
        require(recipients.length > 0 && recipients.length <= 50, "Invalid recipients length");
        uint256 total = uint256(recipients.length).mul(amount);
        require(amount > 0 && balances[msg.sender] >= total, "Insufficient balance or invalid amount");
        balances[msg.sender] = balances[msg.sender].sub(total);
        for (uint i = 0; i < recipients.length; i++) {
            balances[recipients[i]] = balances[recipients[i]].add(amount);
            emit Transfer(msg.sender, recipients[i], amount);
        }
        return true;
    }

    // Time-based reward multiplier (note: modulus on block.timestamp can be manipulated)
    function unlockTimeReward() public view returns (uint256) {
        // Alternative approaches may be needed to avoid timestamp dependency
        if (block.timestamp % 7 < 1) { // Using '< 1' to reduce miner influence
            return 5000 * (10 ** uint256(decimals));
        } else {
            return 1000 * (10 ** uint256(decimals));
        }
    }

    // Lock tokens for a specified duration
    function lockTokens(uint256 duration) public {
        require(duration < 30 days, "Duration too long");
        lockedUntil[msg.sender] = block.timestamp + duration;
    }

    // Check if user's tokens are locked
    function isLocked(address user) public view returns (bool) {
        return block.timestamp < lockedUntil[user];
    }

    // Deposit Ether to the contract
    function deposit() public payable whenNotPaused {
        ethBalances[msg.sender] = ethBalances[msg.sender].add(msg.value);
    }

    // Withdraw Ether (using transfer, which forwards 2300 gas, preventing re-entrancy)
    function withdraw(uint256 amount) public whenNotPaused {
        require(ethBalances[msg.sender] >= amount, "Insufficient ETH balance");
        ethBalances[msg.sender] = ethBalances[msg.sender].sub(amount);
        (bool success, ) = msg.sender.transfer(amount);
        require(success, "Transfer failed");
    }

    // View ETH balance
    function ethBalanceOf(address account) public view returns (uint256) {
        return ethBalances[account];
    }
}

// Note: For further security, consider adding access control modifiers if admin functions are added.