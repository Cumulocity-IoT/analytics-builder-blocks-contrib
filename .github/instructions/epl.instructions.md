---
name: "EPL Development Guide"
description: "Instructions for Apama Event Processing Language (.mon files)"
applyTo: "**/*.mon"
---

# EPL (Event Processing Language) Development

## Overview
EPL is Apama's proprietary event processing language used for writing Analytics Builder blocks and for (deprecated) standalone EPL apps.

## Key EPL Concepts
- **Monitors** - The basic unit of EPL code (similar to classes in OOP). All monitors begin execution with the `onload` action.
- **Events** - Data structures passed between monitors, or to provide reusable helper functions. Also used for Analytics Builder blocks. 
- **Actions** - Functions/methods in EPL
- **Streams** - Declarative query language for processing event flows
- **Listeners** - Event handlers that react to incoming events, often with complex event expressions such as `on all (MeasurementFragment() as m -> OtherEvent() as o and OtherEvent(field="foo") as o2)`. 

## Common EPL Types

- **`string`** - Immutable text string. Operations: `length()`, `contains()`, `find()`, `substring()`, `split(delimiter)`, `replace(regex, replacement)`, `matches(regex)`, `toLower()`, `toUpper()`, `ltrim()`, `rtrim()`. Supports `+` concatenation and comparisons. String methods like `find()` return -1 if not found. Use `groupSearch(regex)` for regex extraction groups.

- **`sequence<TYPE>`** - Ordered list with dynamic size. Operations: `append(item)`, `insert(item, index)`, `remove(index)`, `size()`, `isEmpty()`, `contains(item)`, `indexOf(item)`, `sort()`, `reverse()`. Access elements with `[index]` (0-based, negative indexes from end), or iterate with `for item in sequence`. Use `getOr(index, default)` for safe access without exceptions.

- **`dictionary<KEY,VALUE>`** - Associative key-value map. Operations: `add(key, value)`, `remove(key)`, `hasKey(key)`, `size()`, `isEmpty()`, `keys()`, `values()`. Access with `[key]` operator (throws if missing), or use `getOr(key, default)`, `getOrDefault(key)`, `getOrAdd(key, default)` for safe access. Keys must be comparable type.

- **`any`** - A polymorphic type that can hold any EPL value. Useful for handling generic data (JSON, events of unknown type). Can be empty (like null in Java). Use `switch(a as value)` to handle different types safely. Accessed via `getTypeName()`, `getField()`, `getEntry()` methods.
  
- **`optional<TYPE>`** - A type-safe container for values that may or may not be present. Similar to Java's `Optional`. Either empty or contains a single value of specified type. Use `ifpresent` statement to safely access: `ifpresent opt as value { /* value is accessible here */ }`. Methods: `isEmpty()`, `getOr(default)`, `getOrThrow()`.

- **`context`** - Holds a reference to a context, which groups monitor instances for concurrent execution. Create with `context(name)` and spawn actions to it: `spawn action() to ctx;`. Send events to context: `send event to ctx;`. Use `context.current()` to get current context. Contexts cannot be empty once created.

- **`Channel`** - Holds a destination for events, either a string channel name or a context. Polymorphic - same code can send to string channels or contexts. Create from string `Channel("name")` or context. Use `isEmpty()` to check validity before sending.

- **`com.apama.exceptions.Exception`** - All exceptions are an instance of this. To throw an exception: `throw Exception("Message goes here", "ExceptionTypeGoesHere");`. Exceptions can be caught with `try {} catch (com.apama.exceptions.Exception e) {}` but use sparingly - main use is in listener statements to avoid the listener terminating if there is an exception. 

- **`com.apama.util.AnyExtractor`** - Type-safe way to extract nested values from `any` data (JSON, events, dictionaries). Supports path notation like `"field"`, `"field.nested"`, `"array[0].item"` with both `.` and `[]` operators. Methods: `getString(path)`, `getInteger(path)`, `getFloat(path)`, `getBoolean(path)`, or `getAny(path)` for any type. Use `*Or()` variants for safe extraction with defaults: `getStringOr(path, default)`.

- **`com.apama.correlator.timeformat.TimeFormat`** - Date/time formatting and parsing utility. Works with float timestamps (seconds since UNIX epoch). Key methods: `format(timestamp, pattern)` (format time), `parseTime(pattern, dateString)` (parse to timestamp), `formatUTC()`, `parseTimeUTC()` for UTC, or `*WithTimeZone()` variants for specific timezones. Also provides `getSystemTime()` to get current time and component extraction (dateComponent, timeComponent). Supports patterns like `"yyyy.MM.dd HH:mm:ss"`.

## Coding Standards
- Always include proper documentation comments using `/** ... */` ApamaDoc format for events, monitors, and public or non-trivial actions and fields
- Built-in actions like `onload`, `ondie`, `onunload` do not need documentation
- Ensure proper error handling and logging (`log "My message" at INFO;`)
- Follow naming conventions: PascalCase for monitors and events, camelCase for actions and fields (but for blocks, `$` can be used e.g. `Gate_$Parameters`)
- Use constants for configuration values, magic numbers, and strings (see examples below)
- Organize code logically: parameters/events first, then monitor/action definitions, then implementation
- Prefer tabs over spaces for indentation

## Documentation Comments (ApamaDoc)
- Use `/** ... */` for all public events, monitors, and non-obvious actions
- Document parameters and return values using `@param` and `@returns` tags
- Include examples for complex monitors
- For Analytics Builder blocks, use `@$blockCategory`, `@$inputName`, `@$derivedName` annotations

## Common EPL Patterns

### 1. Subscribing to Cumulocity Events
Most Cumulocity integrations follow this pattern:

```epl
using com.apama.cumulocity.MeasurementFragment;

monitor MyMonitor {
    action onload() {
        monitor.subscribe(MeasurementFragment.SUBSCRIBE_CHANNEL);
        on all MeasurementFragment(type="c8y_Temperature", valueSeries="T") as m {
            log "Temperature: " + m.value.toString() at INFO;
        }
    }
}
```

See: EPL sample `AlarmOnMeasurementThreshold.mon`

### 2. Querying Cumulocity Data
Use request/response pattern with ID correlation:

```epl
using com.apama.cumulocity.FindMeasurement;
using com.apama.cumulocity.FindMeasurementResponse;
using com.apama.cumulocity.FindMeasurementResponseAck;
using com.apama.cumulocity.Util;

monitor QuerySample {
    action onload() {
        FindMeasurement req := new FindMeasurement;
        req.reqId := Util.generateReqId();
        req.params.add("valueFragmentType", "SpeedMeasurement");
        monitor.subscribe(FindMeasurementResponse.SUBSCRIBE_CHANNEL);
        on all FindMeasurementResponse(reqId=req.reqId) as resp and not FindMeasurementResponseAck(reqId=req.reqId) {
            log resp.measurement.toString() at INFO;
        }
        on FindMeasurementResponseAck(reqId=req.reqId) {
            monitor.unsubscribe(FindMeasurementResponse.SUBSCRIBE_CHANNEL);
        }
        send req to FindMeasurement.SEND_CHANNEL;
    }
}
```

See EPL sample: `FindMeasurementSample.mon`

### 3. Calling Other Microservices
Use CumulocityRequestInterface for HTTP requests:

```epl
using com.apama.cumulocity.CumulocityRequestInterface;
using com.softwareag.connectivity.httpclient.Request;

monitor MicroserviceCall {
    action onload() {
        CumulocityRequestInterface iface := CumulocityRequestInterface.connectToCumulocity();
        Request req := iface.createRequest("GET", "/service/path", any());
        req.execute(handleResponse);
    }
    action handleResponse(any resp) {
        log resp.toString() at INFO;
    }
}
```

See: EP sample `CallAnotherMicroservice.mon`

### 4. Analytics Builder Blocks
Blocks use parameters, state, and process actions:

```epl
package apama.analyticskit.blocks.myblocks;

using apama.analyticsbuilder.BlockBase;
using apama.analyticsbuilder.Activation;

/** Parameters for the block. */
event MyBlock_$Parameters { float threshold; }

/** State of the block - tracks internal state across activations. */
event MyBlock_$State { boolean prevState; }

/** 
 * My Block.
 * 
 * Processes input value and produces output based on configured threshold.
 * @$blockCategory Calculations
 * @$derivedName MyBlock $threshold
 */
 event MyBlock {
    MyBlock_$Parameters $parameters;
    BlockBase $base;
    action $process(Activation $activation, MyBlock_$State $state, float $input_value) {
        $setOutput_result($activation, $input_value > $parameters.threshold);
    }
}
```

See blocks: `Threshold.mon`, `ConstantValue.mon`

## Resources
- API documentation for the base events provided by Apama CEP including `com.apama.cumulocity.*` is at: https://cumulocity.com/apama/docs/latest/related/ApamaDoc/overview-summary.html
