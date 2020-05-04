# Raft KV
# Testing
## [Done] Leader election
* 3 servers, no crashes
* 3 servers, leader crashes [and recovers]
* 3 servers, random crashes [and recovers]
* Repeat the above with 5 servers

## Log Replication (without failures)
* [Done] 3 servers
0 start 3 10000
1 start 3 10001
2 start 3 10002

* [Done] put x 3, get
0 start 3 10000
1 start 3 10001
2 start 3 10002
-1 put x 3
-1 get

* [Done] put x 3, put y 5, get
0 start 3 10000
1 start 3 10001
2 start 3 10002
-1 put x 3
-1 put y 5
-1 get

* [Done] put x 3, put x 4, get
0 start 3 10000
1 start 3 10001
2 start 3 10002
-1 put x 3
-1 put x 4
-1 get
-1 get
-1 get

* [Done] put x 3, put y 10, get, put x 7, put y 9, get
0 start 3 10000
1 start 3 10001
2 start 3 10002
-1 put x 3
-1 put y 10
-1 get
-1 put x 7
-1 put y 9
-1 get

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

0 start 5 10000
1 start 5 10001
2 start 5 10002
3 start 5 10003
4 start 5 10004
-1 put x 3
-1 put y 10
-1 get
-1 put x 7
-1 put y 9
-1 get

## KV Store
Above tests with get of a particular value. Also do -1 append z 10. -1 append z 3.
0 start 3 10000
1 start 3 10001
2 start 3 10002
-1 put x 3
-1 get x

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

## Failures
