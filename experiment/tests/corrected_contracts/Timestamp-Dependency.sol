// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title SecureToken - Example of improved security practices
 * @dev Uses SafeMath, reentrancy guard, and access modifiers
 */
contract SecureToken {
    using SafeMath for uint256;

    // State variables
    mapping(address => uint256) private balances;
    mapping(address => mapping(address => uint256)) private allowed;
    address public owner;
    bool private locked;

    // Events
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Caller is not the owner");
        _;
    }

    // Re-entrancy guard
    modifier noReentrant() {
        require(!locked, "Reentrant call");
        locked = true;
        _;
        locked = false;
    }

    constructor() {
        owner = msg.sender;
        // Initialize balances or other setup
    }

    /**
     * @dev Transfer tokens with checks-effects and re-entrancy guard
     */
    function transfer(address _to, uint256 _amount) public noReentrant returns (bool) {
        require(_to != address(0), "Invalid address");
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        // Effects
        balances[msg.sender] = balances[msg.sender].sub(_amount);
        balances[_to] = balances[_to].add(_amount);
        emit Transfer(msg.sender, _to, _amount);
        return true;
    }

    /**
     * @dev Transfer tokens from an approved allowance
     */
    function transferFrom(address _from, address _to, uint256 _amount) public noReentrant returns (bool) {
        require(_to != address(0), "Invalid address");
        require(balances[_from] >= _amount, "Insufficient balance");
        require(allowed[_from][msg.sender] >= _amount, "Allowance exceeded");
        // Effects
        balances[_from] = balances[_from].sub(_amount);
        balances[_to] = balances[_to].add(_amount);
        allowed[_from][msg.sender] = allowed[_from][msg.sender].sub(_amount);
        emit Transfer(_from, _to, _amount);
        return true;
    }

    /**
     * @dev Approve allowance
     */
    function approve(address _spender, uint256 _amount) public returns (bool) {
        require(_spender != address(0), "Invalid spender");
        allowed[msg.sender][_spender] = _amount;
        emit Approval(msg.sender, _spender, _amount);
        return true;
    }

    /**
     * @dev View balance
     */
    function balanceOf(address _owner) public view returns (uint256) {
        return balances[_owner];
    }

    /**
     * @dev View allowance
     */
    function allowance(address _owner, address _spender) public view returns (uint256) {
        return allowed[_owner][_spender];
    }

    /**
     * @dev Owner-only function to transfer ownership
     */
    function transferOwnership(address _newOwner) public onlyOwner {
        require(_newOwner != address(0), "Invalid address");
        owner = _newOwner;
    }

    /**
     * @dev Minimal example of avoiding piggyback on block.timestamp; use external oracles for time-dependent logic if needed
     */
    function isActionAllowed() internal view returns (bool) {
        // Implement logic that does not rely on block.timestamp, or verify with external data
        // For example, only allow certain actions within a range or with external oracle
        return true;
    }

    // Additional functions and security controls as needed
}

// Note: For full secure implementation, all functions requiring time should avoid 'block.timestamp' or rely on verified external sources. All critical functions should incorporate checks-effects-interactions pattern and re-entrancy guards. Consider importing and extending from OpenZeppelin's fully tested contracts for standard ERC20 behavior.