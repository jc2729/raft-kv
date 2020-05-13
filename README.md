# Raft KV
# Testing
##  Leader election
* 3 servers, no crashes
* 3 servers, leader crashes [and recovers]
* 3 servers, random crashes [and recovers]
* Repeat the above with 5 servers

##  Log Replication (without failures)
* [Done] 3 servers
0 start 3 10000 1
1 start 3 10001 1
2 start 3 10002 1

* [Done] put x 3, get
0 start 3 10000 1
1 start 3 10001 1
2 start 3 10002 1
-1 put x 3
-1 get x

* [Done] put x 3, put y 5, get
0 start 3 10000 1
1 start 3 10001 1
2 start 3 10002 1
-1 put x 3
-1 put y 5
-1 get x
-1 get y

* [Done] put x 3, put x 4, get
0 start 3 10000 1
1 start 3 10001 1
2 start 3 10002 1
-1 put x 3
-1 put x 4
-1 get x
-1 get x
-1 get x


* [Done] put x 3, put y 10, get, put x 7, put y 9, get
0 start 3 10000 1
1 start 3 10001 1
2 start 3 10002 1
-1 put x 3
-1 put y 10
-1 get x
-1 put x 7
-1 put y 9
-1 get x

* [Done] Repeat the above with 5 servers
0 start 5 10000
1 start 5 10001
2 start 5 10002
3 start 5 10003
4 start 5 10004
-1 put x 3
-1 get

0 start 5 10000
1 start 5 10001
2 start 5 10002
3 start 5 10003
4 start 5 10004
-1 put x 3
-1 put y 5
-1 get

0 start 5 10000
1 start 5 10001
2 start 5 10002
3 start 5 10003
4 start 5 10004
-1 put x 3
-1 put x 4
-1 get
-1 get
-1 get

0 start 5 10000 1
1 start 5 10001 1
2 start 5 10002 1
3 start 5 10003 1
4 start 5 10004 1
-1 put x 3
-1 put y 10
-1 get x
-1 put x 7
-1 put y 9
-1 get x
exit

## KV Store
Above tests with get of a particular value. Also do -1 append z 10. -1 append z 3.
0 start 3 10000
1 start 3 10001
2 start 3 10002
-1 put x 3
-1 get x
exit

0 start 5 10000
1 start 5 10001
2 start 5 10002
3 start 5 10003
4 start 5 10004
-1 put x 3
-1 put y 10
-1 get x
-1 get y
-1 put x 7
-1 put y 9
-1 get y
-1 get x
exit

0 start 5 10000
1 start 5 10001
2 start 5 10002
3 start 5 10003
4 start 5 10004
-1 put x 3
-1 put y 10
-1 get x
-1 get y
-1 put x 7
-1 put y 9
-1 get z
-1 append z 3
-1 get z
-1 append z 4
-1 get y
-1 get x
-1 get z
exit

## Failures w/o recovery
Halt if no majority

0 start 5 10000 1
1 start 5 10001 1
2 start 5 10002 1
3 start 5 10003 1
4 start 5 10004 1
-1 put x 3
-1 put y 10
-1 get x
-1 get y
-1 put x 7
-1 append z 3
-1 get z
-1 append z 4
-1 get y
-1 get x
-1 get z
exit

0 crash
1 crash
2 crash

### Progress with majority
Follower and/or leader crash

0 start 5 10000 1
1 start 5 10001 1
2 start 5 10002 1
3 start 5 10003 1
4 start 5 10004 1
-1 put x 3
-1 put y 10
-1 get x
-1 get y
-1 put x 7
-1 put y 9
-1 put x 5
-1 get x
exit

0 crash
1 crash
## Failures w/ recovery
### Recovered should catch up
* two recovery cases

0 start 5 10000
1 start 5 10001
2 start 5 10002
3 start 5 10003
4 start 5 10004
-1 put x 3
-1 put y 10
-1 get x
-1 get y
-1 put x 7
0 crash
-1 put y 9
1 crash
-1 put x 5
-1 get x
0 start 5 10000
-1 put x 155
-1 get x
exit


### Recovered should catch up and progress
0 start 5 10000 2
1 start 5 10001 2
2 start 5 10002 2
3 start 5 10003 2
4 start 5 10004 2
-1 put x 3
-1 put y 10
-1 get x
-1 get y
-1 put x 7
-1 put y 9
exit

0 crash in the middle
0 start 5 10000 2

## Modifications for concurrent clients
### 1 client
On master: 
0 start 5 10000 1
1 start 5 10001 1
2 start 5 10002 1
3 start 5 10003 1
4 start 5 10004 1

On client:
0 start 5 10000 1
1 start 5 10001 1
2 start 5 10002 1
3 start 5 10003 1
4 start 5 10004 1
-1 put x 3
-1 put y 10
-1 get x
-1 get y
-1 put x 7
-1 put y 9
-1 get x
-1 put x 155
-1 get x
exit

### 3 client no conflict/linearizable
On master: 
0 start 5 10000 3
1 start 5 10001 3
2 start 5 10002 3
3 start 5 10003 3
4 start 5 10004 3

On client 1:
0 start 5 10000 3
1 start 5 10001 3
2 start 5 10002 3
3 start 5 10003 3
4 start 5 10004 3
-1 append x 1
-1 get x
-1 append x 2
-1 get x
-1 append x 3
-1 get x
exit

On client 2:
0 start 5 10000 3
1 start 5 10001 3
2 start 5 10002 3
3 start 5 10003 3
4 start 5 10004 3
-1 append x 4
-1 get x
-1 append x 5
-1 get x
-1 append x 6
-1 get x
exit

On client 3:
0 start 5 10000 3
1 start 5 10001 3
2 start 5 10002 3
3 start 5 10003 3
4 start 5 10004 3
-1 append x 7
-1 get x
-1 append x 8
-1 get x
-1 append x 9
-1 get x
exit
