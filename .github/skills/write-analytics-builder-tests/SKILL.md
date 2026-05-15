---
name: write-analytics-builder-tests
description: 'Write PySys tests for Apama Analytics Builder blocks. Use when: creating a test for a block, adding test cases for a block, writing pysystest.py files, testing block inputs and outputs, verifying block behaviour with assertBlockOutput or assertGrep, testing block parameters or state.'
argument-hint: 'Name of the block to test, and any specific scenarios to cover'
---

# Write PySys Tests for Analytics Builder Blocks

## Overview

Tests live in `tests/<BlockName>_NNN/pysystest.py` (e.g. `tests/Nand_001/pysystest.py`). Each test is a single Python file — no other files are needed. Tests use the PySys framework with the Analytics Builder test extension.

The correlator is **externally clocked** — time only advances when a `self.timestamp()` event is sent. Always send a final timestamp after the last input to ensure the last events are flushed and processed.

---

## Step 1 — Read the Block

Before writing a test, read the block's `.mon` file to identify:
- The **fully qualified block ID** (the `event` name in the package, e.g. `apamax.analyticsbuilder.custom.Nand`)
- All **input names** (parameters of the `$process` action prefixed with `$input_`)
- All **output names** (calls to `$setOutput_<name>`)
- All **parameters** (fields of the `_$Parameters` event)
- The **block logic** — what inputs and parameter combinations produce which outputs

---

## Step 2 — Plan Test Cases

Design one `pysystest.py` per scenario. A minimal test suite for a block should cover:

| Test | Purpose |
|---|---|
| `_001` | **Touch test** — deploys successfully, basic happy-path input → output |
| `_002` ... | Edge cases, parameter variations, boundary values, inverse inputs |

Each test should be focused — test one behaviour per file.

---

## Step 3 — Create the Test File

### Naming and location

```
tests/<BlockName>_<NNN>/pysystest.py
```

The `<NNN>` suffix is a zero-padded 3-digit number starting at `001`.

### `pysystest.py` template

```python
__pysys_title__   = r""" <BlockName> block - <short description of scenario>. """
#                        =========================================================================
__pysys_purpose__ = r""" <BlockName> block - <short description of scenario>. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
    def execute(self):
        correlator = self.startAnalyticsBuilderCorrelator(
            blockSourceDir=f'{self.project.SOURCE}/blocks/')

        # engine_receive process listening on all the channels.
        correlator.receive('all.evt')

        # Deploy the model. Pass parameters if the block has any.
        self.modelId = self.createTestModel('<fully.qualified.BlockId>',
                                           {'paramName': value})  # omit if no params

        self.sendEventStrings(correlator,
                              self.timestamp(1),
                              self.inputEvent('<inputName>', <value>, id=self.modelId),
                              self.timestamp(2),
                              self.inputEvent('<inputName>', <value>, id=self.modelId),
                              self.timestamp(20),  # final flush
                              )

    def validate(self):
        # Always verify the model started successfully.
        self.assertGrep(self.analyticsBuilderCorrelator.logfile,
                        expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

        # Always add at least one output assertion — an empty validate() is a Python IndentationError.
        self.assertBlockOutput('<outputName>', [<expected_value>])
```

#### `blockSourceDir` path

- For blocks in `blocks/`:  `f'{self.project.SOURCE}/blocks/'`
- For blocks in other directories (e.g. `cumulocity-blocks/`): `f'{self.project.SOURCE}/cumulocity-blocks/'`

---

## Step 4 — Choose an Assertion Method

### Option A — `assertBlockOutput` (simplest, for ordered value sequences)

Use when you want to assert the full sequence of values produced on an output:

```python
self.assertBlockOutput('outputName', [value1, value2, ...])
```

### Option B — `outputExpr` + `assertGrep` (for specific value at a specific time)

Use `self.outputExpr(outputId, value, time=t)` to build a regex that matches an output event:

```python
self.assertGrep('output.evt', expr=self.outputExpr('trigger', None, time=40))
self.assertGrep('output.evt', expr=self.outputExpr('result', 10.5))
```

Pass `None` as value when you only care that the output fired, not its value.

> **Floating-point caution**: avoid asserting exact float values that may render with rounding (e.g. `4.6` may appear as `4.599999999997`). Prefer `assertBlockOutput` which handles this, or use `assertGrep` with a lenient regex.

### Option C — `assertGrep` on correlator log (quick smoke check)

For simple blocks that log their output:

```python
self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='myOutput = true')
```

### Option D — `OUTPUT_REGEX` pattern (for multiple outputs at specific times)

Use when a block fires multiple output ports at the same timestamp:

```python
OUTPUT_REGEX = r'apamax.analyticsbuilder.test.Output\("%(outputId)s","%(modelId)s","[^"]*",%(time)s,any\([^"]*,(.*)\),\{.*\}\)'
self.assertThat("expected == output",
                expected='true',
                output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX % {'outputId': 'entered', 'modelId': 'model_0', 'time': 2}).group(1)")
```

---

## Step 5 — Key Rules

- **Always send a final `self.timestamp()` after the last input** — otherwise the last events may not be processed.
- Events sent between two timestamps that are **less than 0.1 s apart** are held and processed together.
- **For blocks with multiple inputs that must be evaluated together** (e.g. `value1` and `value2`), send all of them _between the same pair of timestamps_. Sending them at different timestamps causes the block to fire once per input, producing more outputs than expected:

  ```python
  # CORRECT — both inputs processed simultaneously at t=1
  self.sendEventStrings(correlator,
                        self.timestamp(1),
                        self.inputEvent('value1', 10.0, id=self.modelId),
                        self.inputEvent('value2', 5.0, id=self.modelId),
                        self.timestamp(2),
                        )
  # assertBlockOutput('output', [15.0])  ✓ one output

  # WRONG — block fires at t=1 and again at t=2, producing two outputs
  self.sendEventStrings(correlator,
                        self.timestamp(1),
                        self.inputEvent('value1', 10.0, id=self.modelId),
                        self.timestamp(2),
                        self.inputEvent('value2', 5.0, id=self.modelId),
                        self.timestamp(3),
                        )
  # assertBlockOutput('output', [15.0])  ✗ fails — actual output is [10.0, 15.0]
  ```

- **`validate()` must never be empty** — an empty method body is a Python `IndentationError`. Always include at least the model-started assertion.
- `inputEvent` default type is `float`. For boolean inputs pass `True`/`False`. For string inputs include `inputs={'inputName': 'string'}` in `createTestModel`.
- To leave an input disconnected, pass `inputs={'inputName': None}` in `createTestModel`.
- `self.modelId` is automatically assigned `model_0`, `model_1`, etc. if not specified.

---

## Examples

### Boolean gate block (no parameters)

```python
self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.Nand')
self.sendEventStrings(correlator,
                      self.timestamp(1),
                      self.inputEvent('value1', True, id=self.modelId),
                      self.timestamp(2),
                      self.inputEvent('value2', False, id=self.modelId),
                      self.timestamp(20),
                      )
# validate
self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='nandOutput = true')
```

### Block with two inputs that are evaluated together (e.g. binary operations)

For blocks where the output depends on both inputs simultaneously (arithmetic, logic gates), always send both inputs between the same timestamp pair:

```python
self.modelId = self.createTestModel('apamax.analyticsbuilder.blocks.MathOperation',
                                    {'operation': 'add'})
self.sendEventStrings(correlator,
                      self.timestamp(1),
                      self.inputEvent('value1', 10.0, id=self.modelId),  # both in same window
                      self.inputEvent('value2', 5.0, id=self.modelId),
                      self.timestamp(2),
                      )
# validate
self.assertBlockOutput('output', [15.0])  # exactly one output: 10.0 + 5.0
```

### Block with parameters and numeric output

```python
self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.AlarmBand',
                                    {'upper': 10.0, 'lower': 5.0})
self.sendEventStrings(correlator,
                      self.timestamp(1),
                      self.inputEvent('value', 3.0, id=self.modelId),
                      self.timestamp(2),
                      )
# validate
self.assertBlockOutput('entered', [False])
```

### Block with numeric float output

```python
self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.IntToFloat64')
self.sendEventStrings(correlator,
                      self.timestamp(1),
                      self.inputEvent('value', 0x4024000000000000, id=self.modelId),
                      self.timestamp(2),
                      )
# validate
self.assertGrep('output.evt', expr=self.outputExpr('floatOutput', 10))
```

---

## Completion Checklist

- [ ] Test file is at `tests/<BlockName>_<NNN>/pysystest.py`
- [ ] `__pysys_title__` and `__pysys_purpose__` are set
- [ ] `blockSourceDir` points to the correct block source directory
- [ ] `createTestModel` uses the correct fully-qualified block ID
- [ ] All block parameters under test are passed to `createTestModel`
- [ ] A final `self.timestamp()` is sent after all inputs
- [ ] Model deployment is asserted with `assertGrep` on the logfile
- [ ] Block output values are asserted with an appropriate assertion method
- [ ] Test passes when run with `cd tests && pysys run <TestDir>`
