pragma solidity >=0.0;

import "./AOAUpgradeLogic.sol";

contract AOAUpgradeMgmt {

    using SafeMath for uint;

    address  private logic;

    struct Order {
        address oldAddress;
        address newAddress;
        uint256 orderId;
        uint expiration;
        bool ended;
    }

    Order[] public orders;

    mapping(uint => IterableMapping.itmap) votes;

    // event upgrade(address indexed newAddress, address indexed oldAddress);
    event DelegateVoteResultEvent(uint indexed orderId, address indexed new_address);
    //update upgrade contract
    event UpdateUpgradeContractEvent(uint256 indexed orderId, address indexed old_address, address indexed new_address);
    event RevokeUpdateVoteEvent(uint256 indexed orderId);
    event VoteUpdateEvent(uint256 indexed orderId);


    //isContractUpdating event
    event UpgradeContractAddressUpdateEvent(bool indexed update, bool indexed voteEnded);
    // SendRequest expired event
    event UpgradeContractAddressValidEvent(bool indexed valid);

    // is vote end event
    event VoteEndedEvent(bool indexed ended);

    // is upgrade address unexpired event
    event UpgradeAddressUnexpiredEvent(bool indexed unexpired);


    modifier preCheckForVote(uint orderId){
        // only delegate can vote
        require(msg.sender.isDelegate(), "only delegate");
        // order not expired
        require(orders[orderId].expiration > now, "order is expirated");
        // order not ended
        require(!orders[orderId].ended, "order is ended");
        // msg.sender not vote yet
        require(!IterableMapping.contains(votes[orderId], msg.sender), "voter is signed");
        _;
    }

    modifier preCheckForRevokeVote(uint orderId){
        // only delegate can vote
        require(msg.sender.isDelegate(), "only delegate");
        // order not expired
        require(orders[orderId].expiration > now, "order is expirated");
        // order not ended
        require(!orders[orderId].ended, "order is ended");
        // msg.sender not vote yet
        require(IterableMapping.contains(votes[orderId], msg.sender), "voter is signed");
        _;
    }

    modifier preCheckForNewRequest(){
        // only delegate can vote
        require(msg.sender.isDelegate(), "only delegate");
        // require(orders[orders.length-1].expiration > now,"order is expirated");
        _;
    }

    modifier preCheckOrdersLength(uint length){
        require(length > 0, "length need > 0");
        _;
    }

    function SendRequest(address newAddress) public preCheckForNewRequest() returns (uint256) {
        require(newAddress != address(0), "new logic address error");
        require(logic != newAddress, "old logic address == new logic address");

        //check upgrade is not in progress
        if (logic != address(0) && AOAUpgradeLogic(logic).isUpgrading()) {
            revert("upgrading");
        }

        if (orders.length != 0 && !isVoteEnded() && isUpgradeAddressUnexpired()) {
            revert("updating");
        }

        uint256 orderId = orders.length;

        uint time = now + 2 weeks;
        //         uint time = now + 1 minutes;
        orders.push(Order({
            oldAddress : logic,
            newAddress : newAddress,
            orderId : orderId,
            expiration : time,
            ended : false
            }));

        emit UpdateUpgradeContractEvent(orderId, logic, newAddress);
        return orders.length;
    }

    function vote() public preCheckOrdersLength(orders.length) preCheckForVote(orders.length - 1) returns (bool) {
        uint orderId = orders.length - 1;
        IterableMapping.insert(votes[orderId], msg.sender, true);

        //check votes
        uint totalVotes = msg.sender.getDelegateTotalVote();
        totalVotes = totalVotes.safeMul(2).safeDiv(3);
        emit VoteUpdateEvent(orderId);
        uint sum = 0;
        if (votes[orderId].keys.length > totalVotes - 1) {
            for (uint i = IterableMapping.iterate_start(votes[orderId]); IterableMapping.iterate_valid(votes[orderId], i); i = IterableMapping.iterate_next(votes[orderId], i)) {

                (address delegateAddress,) = IterableMapping.iterate_get(votes[orderId], i);
                sum = delegateAddress.getDelegateInfo() + sum;
                if (sum >= totalVotes) {
                    // vote pass
                    orders[orderId].ended = true;
                    doTransaction(orderId);
                    break;
                }
            }
        }
        return true;
    }

    function revokeVote() public preCheckOrdersLength(orders.length) preCheckForRevokeVote(orders.length - 1) returns (bool) {
        uint orderId = orders.length - 1;
        IterableMapping.remove(votes[orderId], msg.sender);
        emit RevokeUpdateVoteEvent(orderId);
        return true;
    }

    function isVoteEnded() internal preCheckOrdersLength(orders.length) view returns (bool){
        bool ended = orders[orders.length - 1].ended;
        emit VoteEndedEvent(ended);
        return ended;
    }

    function isUpgradeAddressUnexpired() public preCheckOrdersLength(orders.length) view returns (bool){
        bool unexpired = orders[orders.length - 1].expiration > now;
        emit UpgradeAddressUnexpiredEvent(unexpired);
        return unexpired;
    }


    function doTransaction(uint orderId) internal preCheckOrdersLength(orders.length) returns (bool) {
        logic = orders[orderId].newAddress;
        AOAUpgradeLogic(orders[orderId].newAddress).setUpgradeManager(this);
        emit DelegateVoteResultEvent(orderId, logic);
        return true;
    }

    function getLogic() public returns (address)  {
        return address(logic);
    }

}