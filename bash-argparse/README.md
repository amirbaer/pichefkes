# bashargparse

A simple bash implementation of Python's argparse library, focusing on the 80/20 of core features.

**Requires bash 4.2+** (for `declare -g` support). macOS ships with bash 3.2 - install a newer version via: `brew install bash`

## Quick Start

```bash
#!/usr/bin/env bash
source bashargparse.sh

argparse_init 'myprogram' 'A tool that does something useful'

add_argument -s v -l verbose -a store_true -h 'Enable verbose output'
add_argument -s o -l output -d 'out.txt' -h 'Output file'
add_argument -p filename -h 'Input file to process'

argparse_parse "$@"

echo "Verbose: $ARG_VERBOSE"
echo "Output: $ARG_OUTPUT"
echo "Input: $ARG_FILENAME"
```

Run with `--help` for auto-generated help:

```
usage: myprogram [options] filename

A tool that does something useful

positional arguments:
  filename                     Input file to process

options:
  -h, --help                   show this help message and exit
  -v, --verbose                Enable verbose output
  -o, --output VALUE           Output file (default: out.txt)
```

## Installation

Copy `bashargparse.sh` to your project and source it:

```bash
source /path/to/bashargparse.sh
```

Or source it relative to your script:

```bash
source "$(dirname "${BASH_SOURCE[0]}")/bashargparse.sh"
```

## API Reference

### argparse_init

Initialize the argument parser.

```bash
argparse_init [program_name] [description]
```

- `program_name` - Name shown in help/errors (default: script name)
- `description` - Description shown in help (default: empty)

### add_argument

Define an argument. Returns 1 on validation errors.

```bash
add_argument [options]
```

| Option | Description |
|--------|-------------|
| `-s, --short FLAG` | Short flag without dash (e.g., `v` for `-v`) |
| `-l, --long FLAG` | Long flag without dashes (e.g., `verbose` for `--verbose`) |
| `-p, --positional NAME` | Positional argument name |
| `-h, --help TEXT` | Help text for this argument |
| `-d, --default VALUE` | Default value |
| `-r, --required` | Mark argument as required |
| `-t, --type TYPE` | Type validation: `string` (default) or `int` |
| `-c, --choices LIST` | Comma-separated list of valid choices |
| `-a, --action ACTION` | Action: `store` (default), `store_true`, or `count` |
| `-n, --nargs VALUE` | Number of args: `+` (one or more), `*` (zero or more), or a number |

### argparse_parse

Parse command line arguments and set result variables.

```bash
argparse_parse "$@"
```

Result variables are named `ARG_<NAME>` where NAME is derived from the argument:
- `--verbose` → `$ARG_VERBOSE`
- `--output-dir` → `$ARG_OUTPUT_DIR`
- `-p filename` → `$ARG_FILENAME`

## Examples

### Boolean Flags

```bash
add_argument -s v -l verbose -a store_true -h 'Enable verbose mode'
add_argument -l debug -a store_true -h 'Enable debug mode'
```

After parsing, `$ARG_VERBOSE` and `$ARG_DEBUG` are `0` (not present) or `1` (present).

### Value Flags with Defaults

```bash
add_argument -s o -l output -d '/tmp/out.txt' -h 'Output file'
add_argument -l config -h 'Config file'  # default is empty string
```

### Required Arguments

```bash
add_argument -l api-key -r -h 'API key (required)'
add_argument -p input -r -h 'Input file (required)'
```

If missing, the parser prints an error and exits:
```
usage: prog [options] input
prog: error: the following argument is required: --api-key
```

### Integer Type Validation

```bash
add_argument -l port -t int -d '8080' -h 'Port number'
add_argument -l retries -t int -h 'Number of retries'
```

Accepts positive/negative integers. Rejects non-integers:
```
prog: error: argument --port: invalid int value: 'abc'
```

### Choices Validation

```bash
add_argument -l level -c 'debug,info,warn,error' -d 'info' -h 'Log level'
```

Rejects values not in the list:
```
prog: error: argument --level: invalid choice: 'trace' (choose from: debug,info,warn,error)
```

### Count Action

```bash
add_argument -s v -l verbose -a count -h 'Increase verbosity'
```

Increments each time the flag appears. Supports combined form:
- `-v` → `ARG_VERBOSE=1`
- `-v -v -v` → `ARG_VERBOSE=3`
- `-vvv` → `ARG_VERBOSE=3`

### Multiple Values (nargs)

```bash
# One or more values (at least one required)
add_argument -l files -n '+' -h 'Files to process'

# Zero or more values (optional)
add_argument -l tags -n '*' -h 'Optional tags'

# Exactly N values
add_argument -l coords -n 3 -t int -h 'X Y Z coordinates'
```

Values are stored as space-separated strings:
```bash
# Iterate over values:
for file in $ARG_FILES; do
    echo "Processing: $file"
done
```

### Positional Arguments

```bash
add_argument -p source -h 'Source file'
add_argument -p destination -h 'Destination file'
```

Positional arguments are assigned in order of definition.

## Complete Example

See [examples/demo.sh](examples/demo.sh) for a comprehensive demonstration of all features, or [examples/simple.sh](examples/simple.sh) for a minimal example.

```bash
#!/usr/bin/env bash
set -euo pipefail

source bashargparse.sh

argparse_init 'deploy' 'Deploy application to server'

# Boolean flags
add_argument -l dry-run -a store_true -h 'Show what would be done'

# Count for verbosity
add_argument -s v -l verbose -a count -h 'Increase verbosity (-vvv for max)'

# Value flags
add_argument -s e -l env -c 'dev,staging,prod' -d 'dev' -h 'Target environment'
add_argument -l port -t int -d '8080' -h 'Port number'

# Required flag
add_argument -l config -r -h 'Path to config file'

# Positional
add_argument -p version -h 'Version to deploy'

argparse_parse "$@"

# Use parsed values
if [[ $ARG_DRY_RUN -eq 1 ]]; then
    echo "[DRY RUN] Would deploy version $ARG_VERSION to $ARG_ENV"
    exit 0
fi

[[ $ARG_VERBOSE -ge 1 ]] && echo "Deploying version $ARG_VERSION..."
[[ $ARG_VERBOSE -ge 2 ]] && echo "Environment: $ARG_ENV, Port: $ARG_PORT"
[[ $ARG_VERBOSE -ge 3 ]] && echo "Config: $ARG_CONFIG"

echo "Deployment complete!"
```

## Limitations vs Python argparse

bashargparse implements the 80/20 of core argparse features. The following are **not supported**:

| Feature | Python | bashargparse Alternative |
|---------|--------|-------------------------|
| Subcommands | `add_subparsers()` | Use separate scripts or case statements |
| Argument groups | `add_argument_group()` | Not supported |
| Mutually exclusive | `add_mutually_exclusive_group()` | Validate manually after parsing |
| store_false | `action='store_false'` | Use store_true and invert logic |
| append/extend | `action='append'` | Use nargs `+` |
| Custom types | `type=custom_func` | Only `int` supported; validate manually |
| metavar | `metavar='FILE'` | Always shows `VALUE` |
| dest | `dest='custom'` | Derived from flag name |
| nargs `?` | Optional value with const | Use separate boolean flag |
| Abbreviation | `--verb` matches `--verbose` | Exact match required |

### Key Differences

| Aspect | Python | bashargparse |
|--------|--------|-------------|
| Results | `args.verbose` | `$ARG_VERBOSE` |
| nargs values | `['a', 'b']` list | `'a b'` space-separated string |
| Booleans | `True`/`False` | `1`/`0` |
| Help flag | Can be disabled | Always reserved |

### Bash-Specific Notes

- **Requires bash 4.2+** for `declare -g` (macOS default is 3.2)
- Whitespace in values works for single-value args; nargs values are space-separated
- Combined short flags (`-vvv`) only work for count/store_true actions

## License

MIT
