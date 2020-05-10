## System
- MB Air with 4 cores


0 start 3 10000 1
1 start 3 10001 1
2 start 3 10002 1

## Latency Experiments
### 1 client, 5 servers
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
-1 put x 1
-1 put x 2
-1 put x 3
-1 put x 4
-1 put x 5
-1 put x 6
-1 put x 7
-1 put x 8
-1 put x 9
-1 put x 10
-1 put x 11
-1 put x 12
-1 put x 13
-1 put x 14
-1 put x 15
-1 put x 16
-1 put x 17
-1 put x 18
-1 put x 19
-1 put x 20
-1 put x 21
-1 put x 22
-1 put x 23
-1 put x 24
-1 put x 25
-1 put x 26
-1 put x 27
-1 put x 28
-1 put x 29
-1 get x
exit

Observations:
- ran 30 requests

### 3 client, 5 servers
On master: 
0 start 5 10000 15
1 start 5 10001 15
2 start 5 10002 15
3 start 5 10003 15
4 start 5 10004 15

On clients:
0 start 5 10000 15
1 start 5 10001 15
2 start 5 10002 15
3 start 5 10003 15
4 start 5 10004 15
-1 put x 1
-1 put x 2
-1 put x 3
-1 put x 4
-1 put x 5
-1 put x 6
-1 put x 7
-1 put x 8
-1 put x 9
-1 put x 10
-1 put x 11
-1 put x 12
-1 put x 13
-1 put x 14
-1 put x 15
-1 put x 16
-1 put x 17
-1 put x 18
-1 put x 19
-1 put x 20
-1 put x 21
-1 put x 22
-1 put x 23
-1 put x 24
-1 put x 25
-1 put x 26
-1 put x 27
-1 put x 28
-1 put x 29
-1 get x
exit


0 start 9 10000 1
1 start 9 10001 1
2 start 9 10002 1
3 start 9 10003 1
4 start 9 10004 1
5 start 9 10005 1
6 start 9 10006 1
7 start 9 10007 1
8 start 9 10008 1
9 start 9 10009 1

0 start 15 10000 1
1 start 15 10001 1
2 start 15 10002 1
3 start 15 10003 1
4 start 15 10004 1
5 start 15 10005 1
6 start 15 10006 1
7 start 15 10007 1
8 start 15 10008 1
9 start 15 10009 1
10 start 15 10010 1
11 start 15 10011 1
12 start 15 10012 1
13 start 15 10013 1
14 start 15 10014 1




