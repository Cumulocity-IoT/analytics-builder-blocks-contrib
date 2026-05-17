---
name: develop-analytics-builder-block
description: 'Develop a new custom Apama Analytics Builder block. Use when: creating a new block, implementing block logic, writing a .mon file for Analytics Builder, designing block inputs outputs and parameters, implementing stateful or stateless blocks, adding documentation to a block. Includes test writing and verification.'
argument-hint: 'Describe the block to create: what it does, its inputs, outputs, and any parameters'
---

# Develop a Custom Analytics Builder Block

## Overview

An Analytics Builder block is a self-contained `.mon` (EPL) file placed in a block directory (e.g. `blocks/`). Each block is an EPL `event` with special `$`-prefixed fields and actions recognized by the Analytics Builder framework. Blocks are stateless or stateful, never monitors. All EPL coding conventions from the EPL Development Guide apply.

For EPL language reference, consult [epl.instructions.md](../../instructions/epl.instructions.md).  
For writing tests, use the **write-analytics-builder-tests** skill.  
For building and packaging, use the **build-analytics-builder-blocks** skill.

---

## Phase 1 — Understand and Clarify the Requirements

Before writing any code, analyse the user's description. Check for the following and **ask the user to resolve any issues before proceeding**:

### Consistency checks

- **Inputs and outputs defined?** — Every input must have a clear type (see the type reference below). Every output must have a clear type declaration and a name that reflects its meaning.
- **Parameters valid?** — Parameters must use only the supported parameter types (see below). They cannot be arbitrary EPL sequences or dictionaries.
- **Logic complete?** — All combinations of inputs and parameters must have defined behaviour. Look for:
  - What happens when optional inputs are absent?
  - What happens at boundary values (zero divisor, empty window, first activation)?
  - Does the block need to track state across activations, or is each activation independent?
  - Do any inputs represent pulses (discrete events) rather than continuous values?
- **State needed?** — If the output depends on previous inputs (running totals, min/max tracking, previous value, counters), the block is **stateful**.
- **Naming conflicts?** — Block name must not clash with existing blocks in the same package.

### Parameter type reference

Block parameters must use one of these types:

| Type | Notes |
|---|---|
| `float` | Numeric value |
| `string` | Text value |
| `boolean` | True/false toggle |
| `optional<T>` | Optional version of any of the above; omitted means "not configured" |
| Enumeration | Declare `constant string <paramName>_<value>` constants on the `_$Parameters` event to define valid values; the UI renders these as a drop-down |
| `sequence<NameValue>` | Ordered list of name/value pairs (`NameValue` has `string name` and `any value` fields) |

Parameter UI rendering can be further controlled with semantic type tags on the parameter field comment:

| Tag | Effect in model editor |
|---|---|
| `pab_multiLine` | Multi-line text area |
| `pab_geofence` | Map area selector |
| `c8y_fragmentSeries_KPI_supportedMeasurements_DataPoints` | Data-point drop-down |
| `pab_codeEditor_<language>` | Code editor with syntax highlighting (e.g. `pab_codeEditor_python`) |

Add the tag as a `$METADATA_<paramName>` constant string on the `_$Parameters` event.

---

### Input and output type reference

#### Simple static types

`float`, `boolean`, `string` — continuous-time values. They **hold their last value** until new input arrives. Repeated inputs of the same value should not change the output.

`pulse` — discrete events. A pulse represents a **single point in time**. Multiple pulse inputs have significance even with no value change. **In EPL, pulse inputs and outputs use the `boolean` type** — the `pulse` tag is a semantic annotation only, not a separate EPL type. Declare with `constant string $INPUT_TYPE_<id> := "pulse"` or `$OUTPUT_TYPE_<id> := "pulse"`.

**Choose `pulse` when**: the signal represents an event firing (alarm triggered, button pressed, threshold crossed). **Choose a continuous type when**: the signal represents a measurement that holds until updated.

> **Optionality rule**: An input should be `optional<T>` only when the block functions correctly with that wire disconnected. If the block does not make sense — or produces errors — without that input being connected, declare it as a non-optional type (`boolean`, `float`, etc.). Using `optional<boolean>` for a required pulse input prevents correct operation.

> **Name uniqueness**: Input names and output names share one namespace per block. You cannot use the same identifier for both an `$input_<name>` parameter and a `$setOutput_<name>` action field. Choose distinct names (e.g. `$input_signal` and `$setOutput_result`).

#### Dynamic / polymorphic types

- Use `any` or `Value` as the `$process` parameter type when the block must accept different types depending on what is connected.
- Use `BlockBase.getInputTypeName(inputId)` inside `$validate()` to inspect the connected type and throw an exception if it is incorrect.
- `Value` carries a `value` field of type `any` plus optional extra properties (`dictionary<string,any>`). When a `Value` output is connected to a simple-typed input, the framework automatically unpacks it. Use `Value` when the block needs to pass along extra properties (e.g. Cumulocity measurement metadata, GPS coordinates).

**When to use `Value` inputs**: use a `Value` input whenever the signal carries structured data in its `properties` dictionary (e.g. a GPS position with `lat`/`lng` fields, a measurement with multiple series). The wire type in Analytics Builder is treated as `pulse` — the `value` field carries the boolean pulse signal and the `properties` dictionary carries the structured payload.

**Extracting properties from a `Value` input**: use `AnyExtractor` to safely extract fields from `$input_<name>.properties`:

```epl
using com.apama.util.AnyExtractor;
using apama.analyticsbuilder.Value;

action $process(Activation $activation, Value $input_position) {
    if not $input_position.properties.hasKey("lat") or
       not $input_position.properties.hasKey("lng") {
        return; // missing required fields — skip this activation
    }
    float lat := AnyExtractor($input_position.properties).getFloatOr("lat", 0.0);
    float lng := AnyExtractor($input_position.properties).getFloatOr("lng", 0.0);
    // ... process lat/lng
}
```

`AnyExtractor.getFloatOr()` handles both `float` and `integer` values in the dictionary automatically. Always validate that required keys exist via `hasKey()` before extracting.

#### BlockBase API (`$base` field)

The block's `$base` field (type `BlockBase`) provides contextual information about the model. Useful methods:

| Method | Returns | Use |
|---|---|---|
| `$base.getBlockId()` | `string` | Unique identifier of this block within the model — useful for debug logging |
| `$base.getInputCount(inputId)` | `integer` | Number of connections to the named input (currently 0 or 1) — use to check whether an optional input is wired |
| `$base.getInputTypeName(inputId)` | `string` | Type name of the wire attached to the named input — use inside `$validate()` to enforce type constraints on `any`/`Value` inputs |

#### Declaring output types

Declare the type of each output using **exactly one** of:

```epl
// 1. Type parameter on the $setOutput action (for a fixed known type)
action<Activation, float> $setOutput_result;

// 2. String constant (cannot coexist with option 3)
constant string $OUTPUT_TYPE_result := "pulse";          // fixed type
constant string $OUTPUT_TYPE_result := "input(value1)";  // same type as input 'value1'
constant string $OUTPUT_TYPE_result := "sameAsAll(a,b)"; // same as inputs a and b (error if they differ)
constant string $OUTPUT_TYPE_result := "pulseOrBoolean(a,b)"; // pulse if any input is pulse, else boolean

// 3. Action (cannot coexist with option 2)
action $outputType_result() returns string {
    return "float";
}
```

For `pulseOrBoolean`, use `boolean` as the `$setOutput` parameter type. For `input()` or `sameAsAll()`, use `Value` or `any`.

---

### Output the development plan

Present the following to the user and wait for confirmation before implementing:

```
## Development Plan: <BlockName>

**Block ID**: `<package>.<BlockName>`
**Category**: <e.g. Calculations / Logic / Aggregates>
**Template**: Stateless / Stateful

**Parameters**:
| Name | Type | Description | Validation |
|------|------|-------------|------------|

**Inputs**:
| Name | Type | Description |
|------|------|-------------|

**Outputs**:
| Name | Type | Description |
|------|------|-------------|

**Logic summary**: <1-3 sentence description of the processing logic>

**Test cases**:
| # | Scenario | Inputs | Expected output |
|---|----------|--------|-----------------|
| 001 | Happy path — ... | ... | ... |
| 002 | Edge case — ... | ... | ... |
| ... | Failure/boundary — ... | ... | no output / error |

**Inconsistencies / open questions** (resolve before proceeding):
- <list any, or "None">
```

Only proceed to implementation once the user confirms the plan.

---

## Phase 2 — Choose a Template

> **Pulse vs continuous reminder**: before choosing a template, confirm whether any input or output is a pulse. If so, note that pulse inputs are automatically reset after each evaluation — do not rely on a pulse input holding its value between activations.

### Decision: Stateless or Stateful?

| Condition | Template |
|---|---|
| Output depends only on the **current** inputs and parameters | **Stateless** |
| Output depends on **previous** inputs (history, counters, previous value) | **Stateful** |

---

## Phase 3 — Implement the Block

### File location and naming

- Place the block in `blocks/<BlockName>.mon` (or the appropriate subdirectory for Cumulocity/simulation blocks).
- Package: `apamax.analyticsbuilder.custom` for generic blocks, or choose an existing package to match the subdirectory.
- Block name: PascalCase. Parameters event: `<BlockName>_$Parameters`. State event: `<BlockName>_$State`.

---

### Template A — Stateless block (no memory between activations)

Use for: pure functions, transformations, gate logic, threshold checks.

```epl
package apamax.analyticsbuilder.custom;

using apama.analyticsbuilder.BlockBase;
using apama.analyticsbuilder.Activation;
// Add further 'using' statements as needed

/**
 * Parameters for <BlockName>.
 *
 * Delete this event entirely if the block has no parameters.
 */
event <BlockName>_$Parameters {

	/**
	 * <ParameterDisplayName>
	 *
	 * <What this parameter controls. State valid values and constraints.>
	 */
	<type> <paramName>;

	// Optional: Add validation. Throw a localized exception for invalid values.
	// action $validate() {
	//     if (<paramName> <= 0.0) {
	//         throw L10N.getLocalizedException("fwk_param_finite_positive_value",
	//             [BlockBase.getL10N_param("<paramName>", self), <paramName>]);
	//     }
	// }
}

/**
 * <BlockDisplayName>
 *
 * <One sentence summary — shown as the block's tooltip in Analytics Builder.>
 *
 * <Further description: when to use this block, what it does with its inputs,
 * what the outputs represent, any important limitations.>
 *
 * @$blockCategory <Calculations|Logic|Aggregates|Utilities>
 * @$derivedName <BlockDisplayName> $<paramName>
 */
event <BlockName> {

	BlockBase $base;
	<BlockName>_$Parameters $parameters;  // Remove if no parameters

	/**
	 * @param $activation The current activation.
	 * @param $input_<inputName> <Description of this input.>
	 * @param $input_<inputName2> <Description of this input.>
	 *
	 * @$inputName <inputName> <Display Name>
	 * @$inputName <inputName2> <Display Name 2>
	 */
	action $process(Activation $activation, <type> $input_<inputName>, <type> $input_<inputName2>) {
		// Implement processing logic here.
		// Call $setOutput_<name>($activation, value) to produce output.
	}

	/**
	 * <OutputDisplayName>
	 *
	 * <What this output represents.>
	 */
	action<Activation,<type>> $setOutput_<outputName>;

	// Declare output type only if not the default (float).
	// Uncomment for boolean pulse outputs:
	// constant string $OUTPUT_TYPE_<outputName> := "pulse";
}
```

---

### Template B — Stateful block (tracks history across activations)

Use for: running totals, counters, previous-value comparisons, windowed aggregates, hysteresis.

```epl
package apamax.analyticsbuilder.custom;

using apama.analyticsbuilder.BlockBase;
using apama.analyticsbuilder.Activation;
using apama.analyticsbuilder.L10N;
// Add further 'using' statements as needed

/**
 * Parameters for <BlockName>.
 *
 * Delete this event entirely if the block has no parameters.
 */
event <BlockName>_$Parameters {

	/**
	 * <ParameterDisplayName>
	 *
	 * <What this parameter controls. State valid values and constraints.>
	 */
	<type> <paramName>;

	action $validate() {
		if (not <paramName>.isFinite() or <paramName> <= 0.0) {
			throw L10N.getLocalizedException("fwk_param_finite_positive_value",
				[BlockBase.getL10N_param("<paramName>", self), <paramName>]);
		}
	}
}
```

#### Available L10N validation keys

| Key | Arguments | When to use |
|-----|-----------|-------------|
| `fwk_param_finite_positive_value` | `[paramName, actualValue]` | Value must be > 0.0 and finite |
| `fwk_param_valid_range` | `[paramName, min, max, actualValue]` | Value must be within a bounded range (e.g. 0.0 to 1.0) |
| `fwk_param_missing_required_value` | `[paramName]` | Required parameter not provided |
| `fwk_param_invalid_value` | `[fieldName1, fieldName2]` | Related fields in conflict (e.g. lower > upper) |

Example — range-bounded parameter:
```epl
action $validate() {
	if (not alpha.isFinite() or alpha < 0.0 or alpha > 1.0) {
		throw L10N.getLocalizedException("fwk_param_valid_range",
			[BlockBase.getL10N_param("alpha", self), "0.0", "1.0", alpha]);
	}
}
```

/**
 * State of the block — persisted across activations by the framework.
 *
 * Add one field per piece of state the block must remember.
 * Keep state minimal: prefer primitive types (float, boolean, integer).
 * Complex state (sequences, dictionaries) is allowed but increases memory use.
 *
 * State fields must be serializable. The following EPL types are NOT allowed in state:
 * - action<...> (action references)
 * - chunk
 * - listener
 * - any value of the above types, including nested inside events or sequences
 *
 * Prefer `optional<T>` over a separate `boolean initialized` field when tracking first activation.
 * The `ifpresent` pattern is cleaner:
 *   optional<float> previousValue;  // empty = first activation
 */
event <BlockName>_$State {
	optional<float> <stateField>;  // empty means first activation has not occurred
}

/**
 * <BlockDisplayName>
 *
 * <One sentence summary — shown as the block's tooltip in Analytics Builder.>
 *
 * <Further description: what history the block maintains, when outputs are
 * produced, how parameters control the windowing or threshold behaviour,
 * any important edge cases (first activation, reset behaviour).>
 *
 * @$blockCategory <Calculations|Logic|Aggregates|Utilities>
 * @$derivedName <BlockDisplayName> $<paramName>
 */
event <BlockName> {

	BlockBase $base;
	<BlockName>_$Parameters $parameters;  // Remove if no parameters

	/**
	 * Called once when the block is first instantiated.
	 * Use to copy parameters into block fields for efficiency.
	 */
	// action $init() {
	//     <localField> := $parameters.<paramName>;
	// }

	/**
	 * @param $activation The current activation.
	 * @param $input_<inputName> <Description of this input.>
	 * @param $input_reset Resets the block state. (Include only if applicable.)
	 * @param $blockState The current persisted state of the block.
	 *
	 * @$inputName <inputName> <Display Name>
	 * @$inputName reset Reset
	 */
	action $process(Activation $activation, <type> $input_<inputName>, boolean $input_reset,
	                <BlockName>_$State $blockState) {

		// Handle optional reset input.
		if ($input_reset) {
			$blockState.<stateField> := new optional<float>;
		}

		// First-activation pattern using optional + ifpresent:
		ifpresent $blockState.<stateField> as prevValue {
			// Subsequent activations: use prevValue and current input
			// $setOutput_<outputName>($activation, ...);
		} else {
			// First activation: initialize state
			$blockState.<stateField> := $input_<inputName>;
		}
	}

	/**
	 * <OutputDisplayName>
	 *
	 * <What this output represents.>
	 */
	action<Activation,<type>> $setOutput_<outputName>;

	// Declare output type only if not the default (float).
	// constant string $OUTPUT_TYPE_<outputName> := "pulse";

	// Declare input type if not the default (float).
	// constant string $INPUT_TYPE_reset := "pulse";
}
```

---

## Phase 4 — Documentation Rules

Documentation appears directly in the Analytics Builder UI. Keep it accurate and useful:

- **Block docstring** (`/** ... */` on the `event`): One-sentence summary + when/where to use it + what the outputs mean. Mention important constraints (e.g. "requires at least 2 inputs before producing output").
- **Parameter docstrings**: Describe what the parameter controls, its unit (e.g. seconds), and valid range.
- **Input docstrings** (`@param $input_<name>`): Describe what the input represents and any preconditions.
- **Output docstrings** (on `$setOutput_` actions): Describe what the output value means and when it fires.
- Use `@$derivedName` when the block name should reflect a parameter value (e.g. `$derivedName MyBlock $operation` makes the block show as "MyBlock add" in the canvas).
- Use `@$blockCategory` to place the block in the correct palette group.

---

## Phase 5 — Write Tests

After the block is implemented, use the **write-analytics-builder-tests** skill to write tests.

Minimum test coverage for every new block:

| # | Test |
|---|------|
| `_001` | Touch test — block deploys and basic happy-path input → expected output |
| `_002` | Second happy-path scenario (different parameters or input combination) |
| `_003`+ | Edge cases: boundary values, zero/empty inputs, reset behaviour, first activation |
| N | Negative/suppression case: verify no output is produced when the block should be silent (e.g. division by zero, first activation before state is ready) |

Follow the test naming convention: `tests/<BlockName>_NNN/pysystest.py`.

---

## Phase 6 — Run Tests and Verify

Run the block's tests and confirm all pass before concluding:

```bash
cd tests
pysys run <BlockName>_*
```

**Do not consider the block done if any test fails.** Fix the block or test as appropriate, then re-run.

---

## Completion Checklist

- [ ] Development plan confirmed by user before implementation
- [ ] All inconsistencies in the description resolved
- [ ] Block file is in the correct directory with correct package
- [ ] Correct template used (stateless vs stateful)
- [ ] All inputs, outputs, and parameters have ApamaDoc comments
- [ ] Block-level docstring includes summary, use case, and output descriptions
- [ ] `$validate()` added to `_$Parameters` for any numeric parameters with constraints
- [ ] At least one happy-path test and one edge/failure test written
- [ ] All tests pass with `pysys run <BlockName>_*`
