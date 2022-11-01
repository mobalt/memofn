# MemoFN

A python library for memoizing functions for quick debugging/translations.

## Usage

```python
from memofn import memofn, load_cache, save_cache

def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

load_cache('fib.cache.pkl')
mfib = memofn(expire_in_days=9)(fib)
mfib(10)
save_cache('fib.cache.pkl')
```
