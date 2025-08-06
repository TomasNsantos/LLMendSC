pragma solidity >=0.8.0 <0.9.0;

// Using Solidity 0.8+ to leverage built-in overflow checks

contract VulnerableContractsAnalysis {

    address public owner;
    mapping(address => uint256) public balances;

    // Events
    event Transfer(address indexed from, address indexed to, uint256 value);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    // Constructor sets the deployer as owner
    constructor() {
        owner = msg.sender;
        emit OwnershipTransferred(address(0), owner);
    }

    // Modifier to restrict functions to owner only
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    // Function to transfer ownership
    function changeOwner(address _newOwner) public onlyOwner {
        require(_newOwner != address(0), "Invalid new owner");
        emit OwnershipTransferred(owner, _newOwner);
        owner = _newOwner;
    }

    // Example transfer function with security checks
    function transfer(address _to, uint256 _value) public returns (bool) {
        require(_to != address(0), "Invalid recipient address");
        require(balances[msg.sender] >= _value, "Insufficient balance");
        // Update balances
        balances[msg.sender] -= _value;
        balances[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    // Example function to deposit funds
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // Example function to withdraw funds safely, protected against reentrancy
    function withdraw(uint256 _amount) public {
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        // Effects: update balance before external call
        balances[msg.sender] -= _amount;
        // Interaction: external call placed after state changes
        (bool success, ) = msg.sender.call{value: _amount}();
        require(success, "Transfer failed");
    }
}
