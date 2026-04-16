## 0.8.5 (2026-04-16)

### Feat

- Add additional noise policies
- Add distribution-based update policies
- Add an off-the-shelf example
- Add built-in update policies

### Fix

- Restore Python 3.11 compatibility
- Improve report and simulation compatibility

### Refactor

- Improve runtime logging across simulation components
- Simplify degrade policy primitives
- Rename policy families and simplify degradation helpers
- Simplify the policies public API
- Simplify distribution policy selection
- Remove the shared tools module
- Refine built-in policy APIs
- Organise shared utility declarations
- Expose stateful replay policies as callable classes
- Expose scheduled policies as callable classes
- Unify update policies

## 0.8.4 (2026-04-07)

### Fix

- Keep services running on missing routes
- Add context to remote operation failures

### Refactor

- Centralise shared defaults and type aliases
- Convert remote value objects to dataclasses
- Introduce explicit event roles and report queries
- Rename report schema module
- Modernise typing annotations across the codebase
- Simplify builder exports and restore link naming
- Align remote communication naming and request handling
- Use explicit placement reset and deployment state
- Simplify report frame loading and reporter initialization
- Separate runtime preparation from simulation configuration
- Clarify event payload helpers and simulator attachment

## 0.8.3 (2026-03-27)

### BREAKING CHANGE

- path() return type changed. Use processing_time() for total processing time.

### Feat

- Add selectable report dataframe backend

### Fix

- Improve simulation interrupt handling
- Add check in placement view when src and dst node are the same
- update callers of path() method after refactor
- handle zero cached costs correctly in path recomputation logic Introduced `_cost_changed` helper function to properly detect cost changes, minor changes in the docstring
- **infrastructure**: replace manual subgraph patching with nx.subgraph_view
- **infrastructure**: invalidate path/cost cache on topology changes _paths, _costs and _available were never cleared when nodes or edges were added or removed, causing stale cached paths to be returned. Added overrides which clears both caches and resets the available view.
- **infrastructure**: correct path aggregator validation
- prevent silent overwriting and raise quick fail instead

### Refactor

- Remove unused code
- Separate configuration defaults from shared constants
- Make report backends load frames from configurable report formats
- decouple path() and processing_time() methods
- **infrastructure**: separate processing time from path cost caching

### Perf

- Flatten callback metric payloads into tuple rows for reporting
- Streamline reporter streaming and persistent writer handling
- Stream report traversal and filter events by range
- Cache remote actor handles and bound step buffers
- Reduce residual rebuilds and placement mapping overhead
- Cache path resources and simplify default flow generation
- Cache event ordering in local simulator loop
- optimize has_logic memory usage

## 0.8.2 (2026-01-26)

This release tag was created on a side branch and does not correspond to a
separate linear release section in the main changelog history.

## 0.8.1 (2025-11-06)

### BREAKING CHANGE

- Import paths and dependencies have changed.

### Feat

- **core**: Integrate eclypse_core into eclypse and remove the external core dependency

### Fix

- Remove batch_mapping_phase and fix placement_view build
- Switch ruff check and format in pre-commit
- Correct prune_asset in sock_shop builder
- Reintroduce shield_interrupt decorator to catch CTRL-C
- Move nx import to make random generator working correctly

### Refactor

- Merge core files into public code
- Remove placement view residual usage

## 0.8.0 (2025-11-03)

This release is preserved for completeness. No grouped changelog entries were
recovered for this tagged version.

## 0.7.4 (2025-06-27)

This release is preserved for completeness. No grouped changelog entries were
recovered for this tagged version.

## 0.7.3 (2025-06-26)

This release is preserved for completeness. No grouped changelog entries were
recovered for this tagged version.

## 0.7.2 (2025-06-25)

### Fix

- Add activates_on to event decorator

## 0.7.1 (2025-06-10)

This release is preserved for completeness. No grouped changelog entries were
recovered for this tagged version.

## 0.7.0 (2025-06-10)

### Feat

- Add "strict" flag to infrastructure builders
- Add fat_tree generator
- Add Orion CEV infrastructure builder
- Remove group as default asset

### Fix

- Apply dfs_data generalisation to csv reporter
- JSON reporter now keeps callback.data structures untouched
- Remove remote node metric
- Correct default value for bandwidth asset
- Prune edge assets in sock_shop builder
- Add default values to off-the-shelf assets
- Correct merge of user-defined and default path assets aggregators
- Rename "dispatch" into "step" method, in examples

### Refactor

- Change examples according to new interface
- Use new DRIVING_EVENT constant
- Copy core utils module structure
- Remove EclypseCallback and change EclypseEvent management
- Redefine imports in examples after package structure changes
- Copy same core import structure for communication package
- Rewrite examples removing node group
- Rename report and step parameters to avoid pylint warning
- Merge echo example notebooks into a single one
