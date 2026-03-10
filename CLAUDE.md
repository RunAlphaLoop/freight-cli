# CLAUDE.md

## Directives

### Ask before coding
- Always ask before implementing major changes. Explain the plan first, get approval, then code.
- When asked "is there a way" or "what's possible", answer the question — don't implement solutions.

### Don't over-engineer
- New features default to ON. If you build it, it should be running. Don't hide behind flags that default to off.
- Keep it simple. Don't add features, refactor, or "improve" beyond what was asked.

### Carry metadata with data
- Always carry metadata with data. Include context needed to interpret values correctly (metric name, units, source) so downstream code never misinterprets what it received.

### Function arguments
- Prefer keyword arguments over positional, especially cross-module calls. Positional args silently break when decorators/wrappers extract by name.

### Logging discipline
- Only use `logger.warning()` for actual warnings — conditions that are wrong or unexpected. Diagnostic/telemetry data is `debug()` or `info()`. Don't abuse warning level just for visibility.

### Imports
- Never import in the middle of a file or function unless there's a damn good reason (circular dependency). All imports at the top.

### Tables / display-width correctness
- Never hand-build tables with manual f-string padding or hardcoded borders. Use a proper formatter that handles Unicode/emoji display widths. Python's `len()` and f-string width specs use character count, not display width — emoji and CJK break all manual padding.

### Train/val splits
- Always use stratified splits for classification. Never use `random.shuffle()` + index slicing, `.head()`/`.tail()`, plain `KFold`, or bare `train_test_split()` without `stratify=`. Non-stratified splits on imbalanced data corrupt metrics.

### Version files
- Don't manually modify version files. Let automation (git hooks, CI) handle versioning.

### Git hygiene
- Don't commit editor config, scratch notebooks, or build artifacts. Only source and intentionally-published outputs.
