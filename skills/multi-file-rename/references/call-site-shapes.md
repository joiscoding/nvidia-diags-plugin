# Call-site shapes (illustrative)

Placeholder names only: `old_name` to `new_name`, or `m.old` / `m.new`.
These snippets are examples, not expected output. One shape per
classification-table row from `SKILL.md`.

## Rename definitions

```python
# before                         # after
def old_name(x):                 def new_name(x):
    return x                     return x
```

## Rename import aliases

```python
# before                                    # after
from m import old_name as helper            from m import new_name as helper
result = helper(1)                          result = helper(1)
```

## Rename attribute calls

```python
# before                         # after
import m                         import m
m.old_name(payload)              m.new_name(payload)
```

## Rename `__all__` and `patch.object` strings

```python
# before                                      # after
__all__ = ["old_name"]                        __all__ = ["new_name"]
with patch.object(m, "old_name"):             with patch.object(m, "new_name"):
    ...                                       ...
```

## Rename descriptive log strings

```python
# before                                      # after
logger.info("calling old_name")               logger.info("calling new_name")
```

## Leave derived identifiers alone

```python
# before and after, unchanged
class OldNameTest(unittest.TestCase):
    def test_legacy_old_name_path(self):
        ...
```

Whole-word rename must not turn `OldNameTest` or `legacy_old_name_path` into
something else. Flag derived names under "Not done".

## Leave external CLI keys alone

```python
# before and after, unchanged
COMMANDS = {
    "run-old": old_name,   # key is an external CLI contract; leave the key
}
# after rename of the Python symbol only:
COMMANDS = {
    "run-old": new_name,   # key still "run-old"; value updated
}
```

Recipe `<step id="...">`, YAML keys, and metric names that merely contain the
old spelling are also out of scope. List them in the report, do not edit them.
