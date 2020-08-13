# Regex-Engine
A simple, but powerful regular expression recognizer, made using the **Ken Thompson** algorithm, presented in his paper *Regular Expression Search Algorithm* (1968). 

It supports:

-  Concatenation, 
- Union (**|**), 
- Closure (__*__), 
- One or More (**+**), 
- Zero or One (**?**) ,
- Grouping (**( )**) and 
- Range (__[__start__-__end__]__) regex operators.

### Example

```python
import regeng

#grouping, union, closure and concatenation
r = regeng.Regex('(a|b)*c')

r.match('baabac') #True
r.match('cabbba') #False
r.match('c') #True

#match an acepptable identifier name
r = regeng.Regex('([a-z]|[A-Z]|_)([a-z]|[A-Z]|[0-9])*')

r.match('') #False
r.match('identifer') #True
r.match('987c') #False
r.match('_usr501132') #True

#match numbers from 0 to 99
r = regeng.Regex('[0-9]?[0-9]')

r.match('00') #True
r.match('125') #False
r.match('12') #True
r.match('5') #True
```



## Running Tests

```
$ git clone https://github.com/tonisidneimc/Regex-Engine
$ cd Regex-Engine
$ make run
```

