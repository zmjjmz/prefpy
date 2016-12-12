The format for all election data is (each element on a new line):
* Number of Candidates
* 1, Candidate Name
* 2, Candidate Name
* ...
* Number of Voters, Sum of Vote Count, Number of Unique Orders
* count, preference list. (12,1,2,{3,4}). A strict ordering is indicated by a comma (,) and elements that are indifferent are grouped with a ({ }).
* count, preference list. (12,1,2,3,4). A strict ordering is indicated by a comma (,) and elements that are indifferent are grouped with a ({ }).
* ...

The above is based on preflib's format. [Visit them for more info](http://www.preflib.org/data/format.php#election-data)  

Demo usage code is in [mechanismSTVRunner.py](./prefpy/mechanismSTVRunner.py)  
Sample input are in [prefpy/tests](./tests)

There are two main mechanisms that implement STV: MechanismSTV and MechanismSTVAll.

* MechanismSTV has several child mechanisms, each implementing its own tie-breaking rule. Tie-breaking is done to determine which candidate is eliminated.
  * MechanismSTVForward implements forward tie-breaking
    * The candidate with the least votes in the earliest round is eliminated
  * MechanismSTVBackward implements backward tie-breaking
    * The candidate with the leave votes at the latest non-tied round is eliminated
  * MechanismSTVBorda implements borda tie-breaking
    * The candidate with the lowest Borda score is eliminated
  * MechanismSTVCoombs implements coombs tie-breaking
    * The candidate with the most last-place votes is eliminated
* MechanismSTVAll determines all possible winners given all possible tie-breaking schemes
