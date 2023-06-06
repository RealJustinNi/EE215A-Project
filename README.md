# Project Router for EE215A Spring2023
_ShanghaiTech University_
_Author : NiZhaojun, NingBin_  
_Student ID : 2022231102,2022231104_  
_Date : 20230529_
## Run the program
- Requirement Install
```
pip install -r requirements.txt
```
- Run main code
```
 cd ./src
 python router.py -f bench1/bench2/bench3/bench4/bench5/fract2/primary1/industry1
```
## Reference running time  
In order to get smaller costs and less time, we introduced an iterative mechanism in the last four testbenchs (18 iterations)   

| bench5 | fract2 | primary1 | industry1 |
| ------- | ------- | ------- |------- |
| 12mins | 18mins | 9mins | 36mins |

## Result  
The results _(.route)_ are saved in the _./out_ , and we have visualized the individual problems and layout results, saved in _./out/figure_ .  
