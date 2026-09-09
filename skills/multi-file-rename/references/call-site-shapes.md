# Call-site shapes (illustrative)

Placeholder names only: `old_name` → `new_name`, or `m.old` / `m.new`.
These snippets are examples, not a gold tree. One shape per classification-table
row from `SKILL.md`.

## Definition — Rename

```python
# before                         # after
def old_name(x):                 def new_name(x):
    return x                     return x
```

## Import-as — Rename the symbol; leave local alias after `as`

```python
# before                                    # after
from m import old_name as helper            from m import new_name as helper
result = helper(1)                          result = helper(1)
```

## Attribute call — Rename

```python
# before                         # after
import m                         import m
m.old_name(payload)              m.new_name(payload)
```

## `__all__` / `patch.object` string — Rename

```python
# before                                      # after
__all__ = ["old_name"]                        __all__ = ["new_name"]
with patch.object(m, "old_name"):             with patch.object(m, "new_name"):
    ...                                       ...
```

## Descriptive log string — Rename; list for reviewer veto

```python
# before                                      # after
logger.info("calling old_name")               logger.info("calling new_name")
```

## Derived identifier — Leave alone

```python
# before (and after — unchanged)
class OldNameTest(unittest.TestCase):
    def test_legacy_old_name_path(self):
        ...
```

Whole-word rename must not turn `OldNameTest` or `legacy_old_name_path` into
something else. Flag derived names under "Not done".

## External CLI key — Leave alone

```python
# before (and after — unchanged)
COMMANDS = {
    "run-old": old_name,   # key is an external CLI contract; leave the key
}
# after rename of the Python symbol only:
COMMANDS = {
    "run-old": new_name,   # key still "run-old"; value updated
}
```

Recipe `<step id="...">`, YAML keys, and metric names that merely contain the
old spelling are also out of scope — list them in the report, do not edit.
