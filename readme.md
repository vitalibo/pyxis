# PyBoost

![status](https://github.com/vitalibo/pyboost/actions/workflows/ci.yaml/badge.svg)

Python collection of helpful classes for boosting your productivity

### Installation

```bash
pip install 'git+https://github.com/vitalibo/pyboost.git@0.1.1'
```

### Usage

```python
from dataclasses import dataclass
from pyboost.streams import Stream
from pyboost.functions import field_ref


@field_ref
@dataclass
class User:
    name: str
    age: int


users = Stream \
    .of(User('foo', 25), User('bar', 22), User('baz', 30)) \
    .key_by(lambda user: user.age // 10) \
    .group_by_key(User.name) \
    .to_dict()

print(users)
```

Output
```text
{2: ('foo', 'bar'), 3: ('baz',)}
```
