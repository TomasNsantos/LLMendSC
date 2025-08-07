pragma solidity >=0.4.22 <0.6.0;

contract BecToken is PausableToken {
    string public name = "BeautyChain";
    string public symbol = "BEC";
    string public version = "1.0.1";
    uint8 public decimals = 18;

    mapping(address => uint256) public lockedUntil;
    mapping(address => uint256) private ethBalances;

    constructor() public {
        totalSupply = 7000000000 * (10**uint256(decimals));
        balances[msg.sender] = totalSupply;
    }

    function () external {
        revert();
    }

    
    function multiSend(address[] memory recipients, uint256 amount) public whenNotPaused returns (bool) {
        uint total = recipients.length * amount;
        require(recipients.length > 0 && recipients.length <= 50);
        require(amount > 0 && balances[msg.sender] >= total);

        balances[msg.sender] = balances[msg.sender].sub(total);
        for (uint i = 0; i < recipients.length; i++) {
            balances[recipients[i]] = balances[recipients[i]].add(amount);
            emit Transfer(msg.sender, recipients[i], amount);
        }
        return true;
    }

    
    function unlockTimeReward() public view returns (uint256) {
        if (now % 7 == 0) {
            return 5000 * (10 ** uint256(decimals));
        } else {
            return 1000 * (10 ** uint256(decimals));
        }
    }

    
    function lockTokens(uint256 duration) public {
        require(duration < 30 days);
        lockedUntil[msg.sender] = now + duration;
    }

    function isLocked(address user) public view returns (bool) {
        return now < lockedUntil[user];
    }

    
    function deposit() public payable whenNotPaused {
        ethBalances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) public whenNotPaused {
        require(ethBalances[msg.sender] >= amount);
        (bool success, ) = msg.sender.call.value(amount)("");
        require(success);
        ethBalances[msg.sender] -= amount;
    }

    function ethBalanceOf(address account) public view returns (uint256) {
        return ethBalances[account];
    }
}