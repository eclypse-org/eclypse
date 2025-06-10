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

## 0.6.16 (2024-11-25)

### Feat

- Include default metric for service step result

### Fix

- Add missing return in Report class

### Refactor

- Change default gml metrics name
- Add Report class, remove html report

## 0.6.12 (2024-11-21)

## 0.6.10 (2024-11-16)

### Fix

- Add missing await in SockShop mpi CatalogService
- Move report class to eclypse-core

### Refactor

- Adjust imports from core
- Add wrapper for SimulationConfig core class
