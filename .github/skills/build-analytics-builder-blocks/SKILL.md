---
name: build-analytics-builder-blocks
description: 'Build, test, and package Apama Analytics Builder blocks as extension bundles for deployment to Cumulocity. Use when: building Analytics Builder blocks, packaging blocks as zip extensions, running PySys tests, deploying blocks to a Cumulocity tenant, creating a release, or investigating build or test failures.'
argument-hint: 'Describe the blocks to build and/or target Cumulocity tenant'
---

# Build and Package Analytics Builder Blocks for Cumulocity

## Prerequisites

- Running inside an **Apama Analytics Builder dev container** with:
  - Apama platform installed and environment pre-activated
  - Analytics Builder Block SDK available at the path in `$ANALYTICS_BUILDER_SDK`
- Block source files are `.mon` files, optionally accompanied by `.yaml` and `.properties` files in the same directory

## Concepts

An **extension bundle** is a `.zip` file produced by the Analytics Builder SDK that packages one or more blocks from a directory. Each source directory containing `.mon` files is built into its own bundle. If `.yaml` or `.properties` files exist alongside the `.mon` files, they are automatically included by the build tool — no extra flags required.

---

## Step 1 — Discover Block Directories

Identify which directories contain `.mon` block files:

```bash
find . -name "*.mon" -not -path "./.git/*" | sed 's|/[^/]*\.mon$||' | sort -u
```

Each unique directory in the output is a candidate for building a bundle. Note any that also contain `.yaml` or `.properties` files — these will be included automatically.

---

## Step 2 — Run Tests

**Always run the associated tests for every block being built before building.** Tests use the PySys framework and live in a `tests/` directory.

### Find tests for a block

Test directories are named after the block with a numeric suffix (e.g. `IntToFloat64_001`, `IntToFloat64_002`). For each block named `<BlockName>`, find its tests with:

```bash
ls tests/ | grep -i "^<BlockName>_"
```

### Run the associated tests

Run all tests associated with the blocks being built. For each matched test directory, run:

```bash
cd tests
pysys run <BlockName>_*
```

If building multiple blocks, run all their tests together:

```bash
cd tests
pysys run <BlockA>_* <BlockB>_*
```

If building an entire directory of blocks, run the full test suite:

```bash
cd tests
pysys run
```

### If no test directory exists for a block

Note this to the user — it means the block has no automated test coverage. Proceed with the build but warn that the block is untested.

### If tests fail

1. Read the failure output to identify the failing test and block.
2. Fix the block `.mon` file.
3. Re-run the affected test alone to confirm the fix.
4. Re-run the associated tests in full before proceeding.
5. **Do not build a block whose tests are failing.**

> **Note — compilation errors surface at test time, not build time.** The `analytics_builder build extension` tool packages `.mon` files into a zip without compiling them. Any EPL syntax or type errors (e.g. wrong argument types for `L10N.getLocalizedException()`) will only produce a failure when the correlator loads the code during a PySys test run. This is why passing tests before building is mandatory.

---

## Step 3 — Build Extension Bundles

For each block directory discovered in Step 1, run:

```bash
$ANALYTICS_BUILDER_SDK/analytics_builder build extension \
  --input <block-dir>/ \
  --output <output-dir>/<bundle-name>-<VERSION>.zip
```

- `<block-dir>/` — directory containing the `.mon` (and optional `.yaml`/`.properties`) files
- `<bundle-name>` — a descriptive name for the bundle (e.g. derived from the directory name)
- `<VERSION>` — version string, conventionally prefixed with `v` (e.g. `v1.2.0`)
- `<output-dir>` — e.g. `release-artifacts/`; create it first with `mkdir -p`

The SDK picks up all `.mon`, `.yaml`, and `.properties` files found directly in `<block-dir>/`.

### Building a single block in isolation

If you need to package just one `.mon` file:

```bash
BLOCK_NAME=<BlockName>
mkdir -p temp-${BLOCK_NAME}
cp <block-dir>/${BLOCK_NAME}.mon temp-${BLOCK_NAME}/
# Copy companion files if present
for ext in yaml properties; do
  [ -f "<block-dir>/${BLOCK_NAME}.${ext}" ] && cp "<block-dir>/${BLOCK_NAME}.${ext}" temp-${BLOCK_NAME}/
done

$ANALYTICS_BUILDER_SDK/analytics_builder build extension \
  --input temp-${BLOCK_NAME}/ \
  --output release-artifacts/${BLOCK_NAME}-<VERSION>.zip

rm -rf temp-${BLOCK_NAME}
```

---

## Step 4 — Validate Artifacts

```bash
ls -lh release-artifacts/
```

Check:
- Every expected bundle zip exists and is non-zero in size.
- If building individual block zips, the count matches the number of `.mon` files found in Step 1 plus the number of bundles.

```bash
# Count .mon files
find <block-dirs...> -maxdepth 1 -name "*.mon" | wc -l

# Count produced zips
ls release-artifacts/*.zip | wc -l
```

---

## Step 5 — Deploy to a Cumulocity Tenant

Install a bundle to a live Cumulocity tenant by adding connection flags to the build command:

```bash
$ANALYTICS_BUILDER_SDK/analytics_builder build extension \
  --input <block-dir-or-zip> \
  --cumulocity_url https://<TENANT_HOSTNAME>/ \
  --username <USERNAME> \
  --password <PASSWORD> \
  --restart
```

- `--input` accepts either a source directory **or** a pre-built `.zip` file.
- `--restart` restarts the Apama microservice so new blocks are immediately available.
- **Never hard-code credentials in files.** Use environment variables or prompt the user.

After deployment, verify the new blocks appear in the Analytics Builder palette in the Cumulocity UI.

---

## Quick Reference

| Task | Command |
|---|---|
| Find block directories | `find . -name "*.mon" \| sed 's\|/[^/]*\.mon$\|\|\|' \| sort -u` |
| Find tests for a block | `ls tests/ \| grep -i "^<BlockName>_"` |
| Run tests for a block | `cd tests && pysys run <BlockName>_*` |
| Run all tests | `cd tests && pysys run` |
| Build a bundle | `$ANALYTICS_BUILDER_SDK/analytics_builder build extension --input <dir>/ --output <file>.zip` |
| Deploy to tenant | Add `--cumulocity_url`, `--username`, `--password`, `--restart` to the build command |
| List artifacts | `ls -lh release-artifacts/` |

---

## Presenting Results

After completing the build, present a summary to the user containing:

1. A **test results table** with one row per test that was run:

| Test | Block | Result |
|---|---|---|
| IntToFloat64_001 | IntToFloat64 | PASSED |
| IntToFloat64_002 | IntToFloat64 | PASSED |
| Nand_001 | Nand | FAILED |

   - The **Block** column is the block name derived from the test directory name (everything before the last `_NNN` suffix).
   - The **Result** column uses the PySys outcome: `PASSED`, `FAILED`, `BLOCKED`, or `NOT VERIFIED`.
   - If a block had **no associated tests**, include a row with Result = `NO TESTS`.

2. A **build artifacts table** listing what was produced:

| Artifact | Size |
|---|---|
| release-artifacts/IntToFloat64-v1.0.0.zip | 3.0K |

3. A clear **overall status** — whether the build succeeded or was blocked by test failures.

---

## Completion Checklist

- [ ] All tests associated with the built blocks pass (or absence of tests noted to user)
- [ ] A bundle zip exists for every block directory
- [ ] Each zip is non-zero in size
- [ ] `.yaml` and `.properties` companion files are present in the source directory (they are included automatically)
- [ ] (If deploying) Blocks appear in the Cumulocity Analytics Builder palette after restart
