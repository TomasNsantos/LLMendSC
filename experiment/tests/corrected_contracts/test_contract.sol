pragma solidity ^0.8.0;

contract ReentrancyTest {
    mapping(address => uint) public balances;

    // Deposit function to add funds
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // Withdraw function with re-entrancy protection
    function withdraw() public {
        uint amount = balances[msg.sender];
        require(amount > 0, "No balance to withdraw");
        balances[msg.sender] = 0; // Effects: update state before external call
        (bool success, ) = msg.sender.call{value: amount}('');
        require(success, "Transfer failed");
    }
}
