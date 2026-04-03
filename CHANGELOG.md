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
