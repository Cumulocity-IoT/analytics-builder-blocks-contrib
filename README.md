# analytics-builder-blocks-contrib
This repository contains non-productized blocks for Apama Analytics Builder that have been contributed by the community.

## Installation
Working with this repository requires either a local installation of the dependencies and tools or the usage of a Development Container.

### Local installation
To add these blocks to a tenant, you will require:

* A copy of the [block-sdk](https://github.com/Cumulocity-IoT/apama-analytics-builder-block-sdk) github repo
* A local install of the Apama Full Edition from https://download.cumulocity.com/Apama/
* A Cumulocity tenant with a suitable apama-ctrl microservice subscribed (custom blocks are not supported with apama-ctrl-starter).

Installation Steps:

```
. /opt/cumulocity/Apama/bin/apama_env
git clone https://github.com/Cumulocity-IoT/apama-analytics-builder-block-sdk.git
git clone https://github.com/Cumulocity-IoT/analytics-builder-blocks-contrib.git
./apama-analytics-builder-block-sdk/analytics_builder build extension \
      --input analytics-builder-blocks-contrib/blocks/  --name contrib-blocks\
      --cumulocity_url https://$TENANT/ \
      --username $USERNAME --password $PASSWORD --restart
```

### Development Containers
The repository contains a Development Container setup that starts a container with all dependencies and tools already installed. If you use Visual Studio Code, it will detect the presence of the Development Container setup and ask if it should restart in a container.

* When using the default Dockerfile, the latest versions of Apama, the Block SDK and the EPL Apps Tools will be installed by default. This is the recommended setup but if you require a specific version of each, you can overwrite the APAMA_VERSION, APAMA_ANALYTICS_BUILDER_SDK_BRANCH, and APAMA_EPLAPPS_TOOLS_BRANCH variables in devcontainer.json.
* If you are using a computer running macOS on Apple silicon, it is recommended to replace the Dockerfile in devcontainer.json with Dockerfile.apple which uses an ARM64 base image yielding significantly better performance. This Dockerfile will currently always use Apama 27.


## Repository Structure

The repository organises blocks into separate folders by category, with shared infrastructure for tests and tooling alongside.

```
analytics-builder-blocks-contrib/
├── blocks/                    # General-purpose calculation and utility blocks
├── cumulocity-blocks/         # Blocks that integrate directly with Cumulocity IoT
├── simulation-blocks/         # Blocks for generating simulated data streams
├── service-request-blocks/    # Blocks for calling external services
├── python-blocks/             # Blocks that execute Python functions
├── generated-blocks/          # Blocks generated or created via the Copilot agent skills
├── tests/                     # PySys test cases (one subdirectory per test)
├── utils/                     # Shared EPL utilities used by tests (e.g. mocks)
├── config/                    # Connectivity configuration files
```

### Block folders

| Folder | Contents |
|---|---|
| `blocks/` | General-purpose blocks: mathematical operations (`Abs`, `MathOperation`, `Offset`), signal processing (`EdgeDetection`, `RateLimiter`, `RootMeanSquare`), statistics (`DiscreteStatistics`), time utilities (`CronTimer`, `DateTimeStringToSeconds`, `TimeOffset`, `ModelTime`), data format helpers (`CSVReader`, `CSVWriter`, `BaseNConverter`), and integration helpers (`HttpOutputBlock`, `SendEmail`, `WebHook`, `Logging`). |
| `cumulocity-blocks/` | Blocks that read from or write to Cumulocity: measurement input/output (`DeviceMeasurementInput`, `CreateMeasurement`, `CreateMultiMeasurement`, `CreateBatchMeasurements`), device messaging (`InboundDeviceMessage`), OPC UA (`CreateOpcUAWrite`), and aggregation helpers (`LastestValue`, `SumLast`, `TimeTicker`). These blocks depend on Cumulocity event types and connectivity. |
| `simulation-blocks/` | Blocks for producing synthetic data streams: waveform generators (`WaveFormGenerator`, `ApproximateWaveFormGenerator`), random signals (`Random`, `RandomWalk`, `RandomWalk2D`), a fixed-value `Constant`, an `IntervalPulseGenerator`, and a `ProcessControl` block. Useful for model testing without live device data. |
| `service-request-blocks/` | Blocks for making request to [Field Service Management (FSM) Integration](https://github.com/Cumulocity-IoT/cumulocity-microservice-service-request-mgmt). Currently contains `CreateServiceRequest`. |
| `python-blocks/` | The `PythonFunction` block, which allows an Analytics Builder model to execute arbitrary Python code. |
| `generated-blocks/` | Blocks created during development using the Copilot agent skills (e.g. `CountBy`, `Limit`, `DistanceTravelled`). New agent-generated blocks are placed here by convention unless a more specific folder applies. |

### Other top-level folders

| Folder | Purpose |
|---|---|
| `tests/` | PySys test cases. Each subdirectory (`<BlockName>_NNN/`) contains a `pysystest.py` for one scenario. Run with `pysys run <TestId>` or `pysys run` to run all. |
| `utils/` | Shared EPL helpers loaded by tests — currently contains `DeviceServiceMock.mon`, a mock for Cumulocity device/service interactions. |
| `config/` | Connectivity configuration used when running the correlator locally (YAML/properties files under `config/connectivity/`). |

## GitHub Copilot Agent Skills

This repository ships three GitHub Copilot agent skills that let you create, test, and ship Analytics Builder blocks using natural language instructions. The skills are located under `.github/skills/` and are automatically offered to the agent when relevant tasks are requested.

### Skills overview

| Skill | Trigger phrase examples |
|---|---|
| **develop-analytics-builder-block** | *"Create a block that…"*, *"Add a new block…"*, *"Write a .mon file for…"* |
| **write-analytics-builder-tests** | *"Write tests for the X block"*, *"Add a test case for…"*, *"Test the edge case where…"* |
| **build-analytics-builder-blocks** | *"Build and package the blocks"*, *"Run all tests and create a release"*, *"Deploy the block to my tenant"* |

---

### Skill: develop-analytics-builder-block

Guides the agent through the full lifecycle of creating a new block: requirements analysis, development plan, EPL implementation, and test verification.

*Limitations* The skill does not contain information to develop input & output blocks (especially for Cumulocity) and will consequently not do well for these. It also contains no knowledge about partitions thus will not work well for blocks that run across groups.

**Example prompts:**

```
Create a block that clamps a float value to configurable upper and lower limits.
At least one limit must be configured.
Put the block in the generated-blocks/ folder.
```

```
Create a stateful block that counts pulse signals on one input and outputs
the accumulated count when a reset pulse arrives on a second input.
```

The agent will:
1. Analyse the requirements and flag any inconsistencies (naming conflicts, missing types, ambiguous edge cases)
2. Present a development plan for confirmation — including parameters, inputs, outputs, and planned test cases
3. Implement the `.mon` file using the correct EPL template (stateless or stateful)
4. Create PySys test cases and run them before declaring the block complete

---

### Skill: write-analytics-builder-tests

Guides the agent through writing `pysystest.py` files for any existing block.

**Example prompts:**

```
Write two more test cases for the Limit block: one where only the lower limit
is set and the input is below it, one where only the upper limit is set and
the input is above it.
```

```
Add a test that verifies the CountBy block resets correctly after outputting.
```

The agent will:
1. Read the block's `.mon` file to discover inputs, outputs, and parameter names
2. Create numbered test directories (`tests/<BlockName>_NNN/pysystest.py`)
3. Run the tests and fix any failures before finishing

---

### Skill: build-analytics-builder-blocks

Guides the agent through running the full test suite, building extension bundles, and optionally deploying them to a Cumulocity tenant.

**Example prompts:**

```
Build and package all blocks in the generated-blocks/ folder.
```

```
Run tests for the Limit block, then build a release zip.
```

```
Deploy the Limit block to my tenant at https://my-tenant.cumulocity.com
using username admin and password $MY_PASSWORD.
```

The agent will:
1. Discover all block source directories
2. Run associated PySys tests — stopping if any fail
3. Build `.zip` extension bundles into `release-artifacts/`
4. Optionally deploy to a Cumulocity tenant (always asks for explicit approval before doing so)

---

### Auto-approved and approval-required commands

A pre-tool-use hook (`.github/hooks/build-blocks-permissions.json`) controls which terminal commands the agent may run without pausing to ask for permission.

#### Auto-approved (run without prompting)

These commands are considered safe and local-only:

| Category | Commands / patterns |
|---|---|
| File discovery | `find`, `ls`, `grep`, `wc`, `cat`, `head`, `tail`, `sed`, `unzip -l` |
| Directory setup | `mkdir -p temp-…` or `mkdir -p …release-artifacts` |
| Staging files | `cp *.mon temp-…`, `cp *.yaml temp-…`, `cp *.properties temp-…` |
| Running tests | `pysys run …` |
| Building bundles | `analytics_builder build extension …` *(no `--cumulocity_url` or `--restart`)* |
| Cleanup | `rm -rf temp-…`, `rm -rf tests/…/Output` |

#### Always requires explicit approval

| Scenario | Reason |
|---|---|
| Any command containing `--cumulocity_url` | Deploys code to a live tenant |
| Any command containing `--restart` | Restarts the Apama microservice, affecting running models |

Everything else is passed through to the default VS Code approval flow.

---

## Licensing

Copyright (c) 2019-present Cumulocity GmbH

This project is licensed under the Apache 2.0 license - see <https://www.apache.org/licenses/LICENSE-2.0>

______________________
These tools are provided as-is and without warranty or support. They do not constitute part of the Cumulocity products. Users are free to use, fork and modify them, subject to the license agreement. While Cumulocity welcomes contributions, we cannot guarantee to include every contribution in the master project.

Contact us at https://community.cumulocity.com/ if you have any questions.
______________________

