# Homebrew App Migrator

[![PyPI version](https://img.shields.io/pypi/v/brew-migrator.svg)](https://pypi.org/project/brew-migrator/)
[![Python versions](https://img.shields.io/pypi/pyversions/brew-migrator.svg)](https://pypi.org/project/brew-migrator/)
[![License](https://img.shields.io/github/license/chriszimbizi/brew-migrator.svg)](https://github.com/chriszimbizi/brew-migrator/blob/main/LICENSE)

A retro-styled CLI tool to migrate manually installed macOS applications from `/Applications` to Homebrew Casks.

## Why this tool?

If you've ever bought a new Mac and spent hours manually downloading `.dmg` files, dragging them to `/Applications`, and trying to remember everything you had installed, this tool is for you.

**Homebrew** is the gold standard for managing software on macOS, but it only works if your apps are installed as "Casks." Most people have a mix of apps they downloaded from websites and apps installed via Homebrew.

### The Power of the Brewfile

Once your apps are migrated to Homebrew Casks using this tool, you can run:

```bash
brew bundle dump
```

This generates a `Brewfile` (like [this example](examples/example_brewfile.rb)). This single file is like a "save game" for your entire Mac setup. On a new machine, you just run `brew bundle` and **every single app** is automatically installed for you in minutes.

## Features

- **Retro UI**: A terminal-based interface that feels like an old-school computer system.
- **Progress Bar**: Visual feedback during Homebrew operations with a custom pulsing activity bar.
- **App Ignoring**: Permanently exclude system apps or non-caskable software from future scans.
- **Multi-Column Layout**: High-density grid-style listing for auditing large application histories.
- **Intelligent Search**: Automatically finds the correct Homebrew Cask for your installed apps.
- **Dry Run Mode**: Safe simulation mode to see what would happen without making any changes.
- **Migration History**: Remembers what you've already migrated, skipped, or failed.
- **Batch Mode**: Quick-install the best matches for all your apps at once.
- **Paginated Results**: Easily browse through multiple search results.

## Installation

### Via PyPI (Recommended)

Install the latest stable version directly from PyPI:

```bash
pip install brew-migrator
```

### From Source (Development)

1. Clone the repository:

   ```bash
   git clone https://github.com/chriszimbizi/brew-migrator.git
   cd brew-migrator
   ```

2. Install in editable mode:

   ```bash
   pip install -e .
   ```

## Usage

After installation, you can run the tool using the `brew-migrator` command:

```bash
brew-migrator [OPTIONS]
```

### Options

- `--dry-run`: **(Highly Recommended)** Simulate the migration without making any changes.
- `--list-apps`: List all applications found in your `/Applications` folder.
- `--list-installed`: List all applications successfully migrated to Homebrew.
- `--list-skipped`: List all applications currently in the skipped history.
- `--list-ignored`: List all applications explicitly marked as ignored.
- `--app "AppName"`: Process a specific application by name.
- `--batch`: Run in batch mode (automatically install the top match).
- `--retry-skipped`: Retry apps that were previously skipped.
- `--retry-ignored`: Re-process apps that were previously marked as ignored.
- `--reset-history`: Clear the migration history file.

### Examples

**Safe Simulation:**

```bash
brew-migrator --dry-run
```

**List all apps:**

```bash
brew-migrator --list-apps
```

**Run in batch mode:**

```bash
brew-migrator --batch
```

## How it Works

1. **Scan**: The tool looks at everything in your `/Applications` folder.
2. **Search**: It asks Homebrew if there's a corresponding "Cask" for each app.
3. **Selection**: You choose the correct match from a list (or let Batch Mode handle it).
4. **Log**: The tool records the migration in a JSON history file to prevent double-work.

## Project Structure

```text
.
├── LICENSE
├── README.md
├── pyproject.toml
└── src
    └── brew_migrator
        ├── cli.py
        ├── core
        │   ├── brew.py
        │   └── history.py
        └── ui
            └── console.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
