pragma solidity ^0.8.0;

contract ReentrancyTest {
    mapping(address => uint) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        if (payable(msg.sender).send(balances[msg.sender])) {
            balances[msg.sender] = 0;
        }
    }
}
