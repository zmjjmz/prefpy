# CSCI 4110 - Computational Social Processes
##### Final Project by Nick Fay, Ravi Panse, and Will Rigby-Hall

### Top Trading Cycle
To run from command line as a standalone program:
```
	python toptradingcycle.py
```
will run unit tests that are laid out in the main block of code.

To run from another program (e.g. import):
```
	import prefpy.toptradingcycle
```

To use within prefpy files:
```
	from . import deferredacceptance
```

#### Example
```
    agents = [
        [4, 3, 2, 1, 5],
        [4, 1, 2, 3, 5],
        [1, 4, 3, 2, 5],
        [3, 2, 1, 4, 5],
        [1, 5, 2, 4, 3]
    ]

    #Returns an array of assignments
    #i.e., agents[0] is assigned result[0]
    result = topTradingCycle(agents)
```

### Deferred Acceptance
To run from command line as a standalone program:
```
	python deferredacceptance.py
```
will run unit tests that are laid out in the main block of code.

To run from another program (e.g. import):
```
	import prefpy.deferredacceptance
```

To use within prefpy files:
```
	from . import deferredacceptance
```

#### Example
```
    side1 = [[10, 1, 2, 3, 5, 4, 6],
             [20, 3, 1, 2, 4, 5, 6],
             [30, 3, 1, 2, 4, 5, 6],
             [40, 1, 2, 3, 4, 5, 6],
             [50, 1, 2, 3, 5, 4, 6],
             [60, 2, 1, 3, 4, 6, 5]]
    side2 = [[1, None, 10, 20, 30, 40, 50, 60],
             [2, 20, 30, None, 50, 10, 40, 60],
             [3, 20, 30, 10, None, 50, 40, 60],
             [4, 20, None, 30, 10, 50, 40, 60],
             [5, 10, 30, None, 20, 50, 40, 60],
             [6, 20, 30, 10, None, 50, 40, 60]]
    #The container that holds the result from running the DA algorithm
    #Where [0,1] corresponds to which side respectively is the proposing side
    stablematchingcontainer = deferredAcceptance(side1, side2, 0)
    
    #Added a stability checker to check the final matching
    #Will return True if it is stable and False if not
    result = stablematchingcontainer.checkStability()
```
