pragma solidity >=0.0;

import "./AOAUpgradeMgmt.sol";

library SafeMath {
    function safeAdd(uint a, uint b) internal pure returns (uint c) {
        c = a + b;
        require(c >= a, "");
    }

    function safeSub(uint a, uint b) internal pure returns (uint c) {
        require(b <= a, "");
        c = a - b;
    }

    function safeMul(uint a, uint b) internal pure returns (uint c) {
        c = a * b;
        require(a == 0 || c / a == b, "");
    }

    function safeDiv(uint a, uint b) internal pure returns (uint c) {
        require(b > 0, "");
        c = a / b;
    }
}

/// @dev Models a uint -> uint mapping where it is possible to iterate over all keys.
library IterableMapping {
    struct itmap
    {
        mapping(address => IndexValue) data;
        KeyFlag[] keys;
        uint size;
    }

    struct IndexValue {uint keyIndex; bool value;}

    struct KeyFlag {address key; bool deleted;}

    function insert(itmap storage self, address key, bool value) internal returns (bool replaced)
    {
        uint keyIndex = self.data[key].keyIndex;
        self.data[key].value = value;
        if (keyIndex > 0)
            return true;
        else
        {
            keyIndex = self.keys.length++;
            self.data[key].keyIndex = keyIndex + 1;
            self.keys[keyIndex].key = key;
            self.size++;
            return false;
        }
    }

    function remove(itmap storage self, address key) internal returns (bool success)
    {
        uint keyIndex = self.data[key].keyIndex;
        if (keyIndex == 0)
            return false;
        delete self.data[key];
        self.keys[keyIndex - 1].deleted = true;
        self.size --;
    }

    function contains(itmap storage self, address key) internal returns (bool)
    {
        return self.data[key].keyIndex > 0;
    }

    function iterate_start(itmap storage self) internal returns (uint keyIndex)
    {
        return iterate_next(self, uint(- 1));
    }

    function iterate_valid(itmap storage self, uint keyIndex) internal returns (bool)
    {
        return keyIndex < self.keys.length;
    }

    function iterate_next(itmap storage self, uint keyIndex) internal returns (uint r_keyIndex)
    {
        keyIndex++;
        while (keyIndex < self.keys.length && self.keys[keyIndex].deleted)
            keyIndex++;
        return keyIndex;
    }

    function iterate_get(itmap storage self, uint keyIndex) internal returns (address key, bool value)
    {
        key = self.keys[keyIndex].key;
        value = self.data[key].value;
    }
}

contract AOAUpgradeLogic {

    using SafeMath for uint;
    using IterableMapping for IterableMapping.itmap;

    uint private upgradeHeight;

    address private mgmt;

    struct UpgradeOrder {
        string version;
        string url;
        string note;
        string md5;
        uint orderId;
        uint expiration;
        bool ended;
        address owner;
        bool canceled;
    }
    
    UpgradeOrder[] public upgradeOrders;

    mapping(uint => IterableMapping.itmap) votes;

    //vote event
    event VoteUpgradeEvent(uint indexed orderId);
    //vote result event
    event VoteOrderIdAndUpgradeHeightEvent(uint indexed orderId, uint indexed upgradeHeight);
    event VoteUpgradeResultEvent(uint indexed orderId, uint indexed upgradeHeight, string upgradeInfo);
    //send upgrade request
    event SendUpgradeRequestEvent(uint indexed orderId, string indexed version);
    //
    event RevokeVoteEvent(uint indexed orderId);
    //
    event CancelUpgradeEvent(uint indexed orderId);

    // isUpgrading event
    event UpgradingEvent(bool indexed flag);

    modifier preCheckForVote(uint orderId){
        // only delegate can vote
        require(msg.sender.isDelegate(), "only delegate");
        // order not expired
        require(upgradeOrders[orderId].expiration > now, "order is expired");
        // order not ended
        require(!upgradeOrders[orderId].ended, "order is ended");
        // msg.sender not vote yet
        require(!votes[orderId].contains(msg.sender), "voter is signed");
        _;
    }

    modifier preCheckForRevokeVote(uint orderId){
        // only delegate can vote
        require(msg.sender.isDelegate(), "only delegate");
        // order not expired
        require(upgradeOrders[orderId].expiration > now, "order is expired");
        // order not ended
        require(!upgradeOrders[orderId].ended, "order is ended");
        // msg.sender not vote yet
        require(votes[orderId].contains(msg.sender), "voter is signed");
        _;
    }

    modifier cancelCheck(uint orderId){
        // only delegate can vote
        require(msg.sender == upgradeOrders[orderId].owner, "only owner can pause.");
        // have canceled
        require(!upgradeOrders[orderId].canceled, "order have canceled");
        // order not expired
        require(upgradeOrders[orderId].expiration > now, "order is expired");
        _;
    }

    modifier preCheckForNewRequest(){
        // only delegate can vote
        require(msg.sender.isDelegate(), "only delegate");
        _;
    }

    modifier preCheckOrdersLength(uint length){
        require(length > 0, "length need > 0");
        _;
    }

    function getUpgradeHeight() public view returns (uint) {
        return upgradeHeight;
    }

    // compare string
    function hashCompareWithLengthCheckInternal(string memory a, string memory b) internal pure returns (bool) {
        if (bytes(a).length != bytes(b).length) {
            return false;
        }
        return keccak256(abi.encode(a)) == keccak256(abi.encode(b));
    }

    function strConcat(string memory _a, string memory _b, string memory _c, string memory _d, string memory _e) internal returns (string memory){
        bytes memory _ba = bytes(_a);
        bytes memory _bb = bytes(_b);
        bytes memory _bc = bytes(_c);
        bytes memory _bd = bytes(_d);
        bytes memory _be = bytes(_e);
        string memory abcde = new string(_ba.length + _bb.length + _bc.length + _bd.length + _be.length);
        bytes memory babcde = bytes(abcde);
        uint k = 0;
        uint i = 0;
        for (i = 0; i < _ba.length; i++) babcde[k++] = _ba[i];
        for (i = 0; i < _bb.length; i++) babcde[k++] = _bb[i];
        for (i = 0; i < _bc.length; i++) babcde[k++] = _bc[i];
        for (i = 0; i < _bd.length; i++) babcde[k++] = _bd[i];
        for (i = 0; i < _be.length; i++) babcde[k++] = _be[i];
        return string(babcde);
    }

    function strConcat(string memory _a, string memory _b, string memory _c, string memory _d) internal returns (string memory) {
        return strConcat(_a, _b, _c, _d, "");
    }

    function strConcat(string memory _a, string memory _b, string memory _c) internal returns (string memory) {
        return strConcat(_a, _b, _c, "", "");
    }

    function strConcat(string memory _a, string memory _b) internal returns (string memory) {
        return strConcat(_a, _b, "", "", "");
    }

    // send upgrade reqeust for voting
    function SendUpgradeRequest(string memory version, string memory url, string memory md5, string memory note) public preCheckForNewRequest() returns (uint) {
        require(bytes(version).length > 0, "new logic address error");
        require(bytes(url).length > 0, "new logic address error");
        require(bytes(md5).length > 0, "new logic address error");
        require(mgmt != address(0), "mgmt address error");

        if (isUpgrading()) {
            revert("upgrading");
        }

        address logic = AOAUpgradeMgmt(mgmt).getLogic();
        if (logic == address(0) || logic != address(this)) {
            revert("logic address error");
        } else {
            if (!AOAUpgradeMgmt(mgmt).isUpgradeAddressUnexpired()) {
                revert("upgrading");
            }
        }


        uint orderId = upgradeOrders.length;

        uint time = now + 2 weeks;
        //        uint time = now + 1 minutes;
        // UpgradeOrder memory uo = UpgradeOrder(version,url,note,md5,orderId,time,false,msg.sender,false);
        UpgradeOrder memory uo = UpgradeOrder({
            version : version,
            url : url,
            note : note,
            md5 : md5,
            orderId : orderId,
            expiration : time,
            ended : false,
            owner : msg.sender,
            canceled : false
            });
        upgradeOrders.push(uo);
        emit SendUpgradeRequestEvent(orderId, version);
        return upgradeOrders.length;
    }

    function vote() public preCheckOrdersLength(upgradeOrders.length) preCheckForVote(upgradeOrders.length - 1) returns (bool) {
        uint orderId = upgradeOrders.length - 1;
        votes[orderId].insert(msg.sender, true);
        emit VoteUpgradeEvent(orderId);

        //check votes
        uint totalVotes = msg.sender.getDelegateTotalVote();
        totalVotes = totalVotes.safeMul(2).safeDiv(3);
        uint sum = 0;
        if (votes[orderId].keys.length > totalVotes - 1) {
            for (uint i = votes[orderId].iterate_start(); votes[orderId].iterate_valid(i); i = votes[orderId].iterate_next(i)) {

                (address delegateAddress,) = votes[orderId].iterate_get(i);
                sum = delegateAddress.getDelegateInfo() + sum;
                if (sum >= totalVotes) {
                    // vote pass
                    upgradeOrders[orderId].ended = true;
                    // one week after the voting ended, upgrading will start. 60480 is the block height can be reached in one week
                    upgradeHeight = block.number + 10;//10 for test
                    // emit VoteOrderIdAndUpgradeHeightEvent(orderId, upgradeHeight);
                    string memory upgradeInfo1 = strConcat(upgradeOrders[orderId].version, ";", upgradeOrders[orderId].url, ";", upgradeOrders[orderId].md5);
                    string memory upgradeInfo = strConcat(upgradeInfo1, ";", upgradeOrders[orderId].note);
                    emit VoteUpgradeResultEvent(orderId, upgradeHeight, upgradeInfo);
                    break;
                }
            }
        }
        return true;
    }

    function revokeVote() public preCheckOrdersLength(upgradeOrders.length) preCheckForRevokeVote(upgradeOrders.length - 1) returns (bool) {
        uint orderId = upgradeOrders.length - 1;
        votes[orderId].remove(msg.sender);
        emit RevokeVoteEvent(orderId);
        return true;
    }

    function isUpgrading() public view returns (bool) {
        bool flag = upgradeOrders.length != 0 && (upgradeOrders[upgradeOrders.length - 1].ended ? block.number < upgradeHeight : upgradeOrders[upgradeOrders.length - 1].expiration > now);
        emit UpgradingEvent(flag);
        return flag;
    }


    // cancel the upgrading process
    function cancel() public preCheckOrdersLength(upgradeOrders.length) cancelCheck(upgradeOrders.length - 1) returns (bool){
        uint orderId = upgradeOrders.length - 1;
        upgradeOrders[orderId].canceled = true;
        emit CancelUpgradeEvent(orderId);
        return true;
    }

    function setUpgradeManager(address manager) public {
        mgmt = manager;
    }

}