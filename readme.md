# PyXIS

![status](https://github.com/vitalibo/pyxis/actions/workflows/ci.yaml/badge.svg)

Pyxis is a comprehensive Python toolkit designed to enhance developer productivity.
It offers a suite of tools and classes that streamline various aspects of software development.
From data stream processing to advanced configuration management, Pyxis provides an array of functionalities
to tackle complex challenges efficiently.

### Installation

```bash
pip install 'git+https://github.com/vitalibo/pyxis.git@0.2.1-pyspark'
```

### Usage

```python
from dataclasses import dataclass
from pyxis.dataclasses import reference
from pyxis.streams import Stream


@reference
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
