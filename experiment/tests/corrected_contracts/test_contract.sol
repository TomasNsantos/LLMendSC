pragma solidity ^0.8.0;

contract ReentrancyTest {
    mapping(address => uint) public balances;

    // Reentrancy guard variable
    uint private unlocked = 1;

    modifier lock() {
        require(unlocked == 1, "Reentrant call detected");
        unlocked = 0;
        _;
        unlocked = 1;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public lock {
        uint amount = balances[msg.sender];
        require(amount > 0, "No balance to withdraw");
        // Effect: set balance to zero before external call
        balances[msg.sender] = 0;
        // Interaction: send Ether using transfer for safety
        payable(msg.sender).transfer(amount);
    }
}