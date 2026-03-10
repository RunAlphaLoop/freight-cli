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
al login ak_your_key_here

# Option 2: Environment variable
export ALPHALOOPS_API_KEY=ak_your_key_here

# Option 3: Pass it directly
al --api-key ak_... carriers get 2247505
```

Get your API key at [runalphaloops.com](https://runalphaloops.com/).

## Usage

### Carrier Profiles

```bash
# Look up by DOT number
al carriers get 2247505

# Look up by MC number
al carriers mc 624748

# Field projection
al carriers get 2247505 --fields legal_name,total_trucks,total_drivers

# Fuzzy search
al carriers search "Swift Transportation"
al carriers search "JB Hunt" --state AR --limit 5

# Authority history
al carriers authority 2247505

# News
al carriers news 2247505 --start-date 2025-01-01
```

### Fleet Data

```bash
al fleet trucks 2247505
al fleet trucks 2247505 --limit 200
al fleet trailers 2247505
```

### Inspections

```bash
al inspections list 2247505
al inspections violations INS-12345
```

### Crashes

```bash
al crashes list 2247505
al crashes list 2247505 --severity FATAL --start-date 2024-01-01
```

### Contacts

```bash
# Search for people
al contacts search --dot 2247505
al contacts search --company "Swift" --levels c_suite,vp

# Enrich a contact (1 credit)
al contacts enrich contact_id_here
```

## JSON Output

Every command supports `--json` for machine-readable output:

```bash
al --json carriers get 2247505
al --json carriers search "Swift" | jq '.results[].legal_name'
al --json fleet trucks 2247505 | jq '.results | length'
```

This makes the CLI agent-friendly — pipe to `jq`, feed into scripts, or use from AI agents.

## Examples

```bash
# Find a carrier and get their fleet size
al carriers search "Werner Enterprises" --limit 1
al carriers get 2247505 --fields legal_name,total_trucks,total_drivers

# Get all fatal crashes for a carrier
al --json crashes list 2247505 --severity FATAL | jq '.results[]'

# Find C-suite contacts and enrich them
al --json contacts search --dot 2247505 --levels c_suite | jq '.results[].name'
al contacts enrich abc123

# Pipeline: search → get details → get fleet
DOT=$(al --json carriers search "Swift" | jq -r '.results[0].dot_number')
al carriers get "$DOT"
al fleet trucks "$DOT"
```

## All Commands

| Command | Description |
|---------|-------------|
| `al login <key>` | Save API key to `~/.alphaloops` |
| `al carriers get <dot>` | Carrier profile by DOT number |
| `al carriers mc <mc>` | Carrier profile by MC number |
| `al carriers search <name>` | Fuzzy search carriers |
| `al carriers authority <dot>` | Authority history |
| `al carriers news <dot>` | News and press mentions |
| `al fleet trucks <dot>` | Registered trucks |
| `al fleet trailers <dot>` | Registered trailers |
| `al inspections list <dot>` | Roadside inspections |
| `al inspections violations <id>` | Violations for an inspection |
| `al crashes list <dot>` | Crash history |
| `al contacts search` | Find contacts at a carrier |
| `al contacts enrich <id>` | Enrich a contact (email, phone) |

## API Documentation

Full API reference: [runalphaloops.com/fmcsa-api/docs](https://runalphaloops.com/fmcsa-api/docs)

## License

MIT — see [LICENSE](LICENSE) for details.
