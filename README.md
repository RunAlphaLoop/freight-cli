# AlphaLoops Freight CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/alphaloops-freight-cli)](https://pypi.org/project/alphaloops-freight-cli/)

Command-line interface for the [AlphaLoops FMCSA API](https://runalphaloops.com/fmcsa-api/docs). Look up carriers, fleet data, inspections, crashes, and contacts from your terminal.

Built on the [AlphaLoops Freight SDK](https://github.com/RunAlphaLoop/freight-sdk).

## Installation

```bash
pip install alphaloops-freight-cli
```

## Authentication

```bash
# Option 1: Save your key
loopsh login ak_your_key_here

# Option 2: Environment variable
export ALPHALOOPS_API_KEY=ak_your_key_here

# Option 3: Pass it directly
loopsh --api-key ak_... carriers get 2247505
```

Get your API key at [runalphaloops.com](https://runalphaloops.com/).

## Usage

### Carrier Profiles

```bash
# Look up by DOT number
loopsh carriers get 2247505

# Look up by MC number
loopsh carriers mc 624748

# Field projection
loopsh carriers get 2247505 --fields legal_name,total_trucks,total_drivers

# Fuzzy search
loopsh carriers search "Swift Transportation"
loopsh carriers search "JB Hunt" --state AR --limit 5

# Authority history
loopsh carriers authority 2247505

# News
loopsh carriers news 2247505 --start-date 2025-01-01
```

### Fleet Data

```bash
loopsh fleet trucks 2247505
loopsh fleet trucks 2247505 --limit 200
loopsh fleet trailers 2247505
```

### Inspections

```bash
loopsh inspections list 2247505
loopsh inspections violations INS-12345
```

### Crashes

```bash
loopsh crashes list 2247505
loopsh crashes list 2247505 --severity FATAL --start-date 2024-01-01
```

### Contacts

```bash
# Search for people
loopsh contacts search --dot 2247505
loopsh contacts search --company "Swift" --levels c_suite,vp

# Enrich a contact (1 credit)
loopsh contacts enrich contact_id_here
```

## JSON Output

Every command supports `--json` for machine-readable output:

```bash
loopsh --json carriers get 2247505
loopsh --json carriers search "Swift" | jq '.results[].legal_name'
loopsh --json fleet trucks 2247505 | jq '.results | length'
```

This makes the CLI agent-friendly — pipe to `jq`, feed into scripts, or use from AI agents.

## Examples

```bash
# Find a carrier and get their fleet size
loopsh carriers search "Werner Enterprises" --limit 1
loopsh carriers get 2247505 --fields legal_name,total_trucks,total_drivers

# Get all fatal crashes for a carrier
loopsh --json crashes list 2247505 --severity FATAL | jq '.results[]'

# Find C-suite contacts and enrich them
loopsh --json contacts search --dot 2247505 --levels c_suite | jq '.results[].name'
loopsh contacts enrich abc123

# Pipeline: search → get details → get fleet
DOT=$(loopsh --json carriers search "Swift" | jq -r '.results[0].dot_number')
loopsh carriers get "$DOT"
loopsh fleet trucks "$DOT"
```

## All Commands

| Command | Description |
|---------|-------------|
| `loopsh login <key>` | Save API key to `~/.alphaloops` |
| `loopsh carriers get <dot>` | Carrier profile by DOT number |
| `loopsh carriers mc <mc>` | Carrier profile by MC number |
| `loopsh carriers search <name>` | Fuzzy search carriers |
| `loopsh carriers authority <dot>` | Authority history |
| `loopsh carriers news <dot>` | News and press mentions |
| `loopsh fleet trucks <dot>` | Registered trucks |
| `loopsh fleet trailers <dot>` | Registered trailers |
| `loopsh inspections list <dot>` | Roadside inspections |
| `loopsh inspections violations <id>` | Violations for an inspection |
| `loopsh crashes list <dot>` | Crash history |
| `loopsh contacts search` | Find contacts at a carrier |
| `loopsh contacts enrich <id>` | Enrich a contact (email, phone) |

## API Documentation

Full API reference: [runalphaloops.com/fmcsa-api/docs](https://runalphaloops.com/fmcsa-api/docs)

## License

MIT — see [LICENSE](LICENSE) for details.
