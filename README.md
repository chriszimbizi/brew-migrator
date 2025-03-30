# Homebrew App Migrator

A utility tool that helps migrate macOS applications to be managed by Homebrew Casks, simplifying application management and updates.

## Inspiration

This project was inspired by the challenge of managing applications from multiple sources (App Store, direct downloads, etc.). Having Homebrew manage applications offers significant advantages:

- **Centralized Updates**: Update all applications with a single `brew upgrade` command
- **Consistent Management**: One tool to install, update, and remove applications
- **Version Control**: Track what's installed across systems
- **Automation**: Generate a Brewfile using `brew bundle dump` that can be used to quickly set up new development machines with identical software

## Features

- Scans your /Applications folder to find installed applications
- Searches for matching Homebrew casks
- Interactive selection interface with pagination
- Tracks migration progress with detailed history
- Provides reports on successfully migrated, failed, and skipped applications

## Prerequisites

- Python 3.6+
- Homebrew installed on your macOS system

## Installation

```shell
# Clone the repository
git clone https://github.com/chriszimbizi/homebrew-app-migrator.git
cd homebrew-app-migrator

# Make the script executable
chmod +x brew_migrator.py
```

## Usage

### Basic Usage

```shell
./brew_migrator.py
```

This will scan your /Applications folder and guide you through migrating each application to Homebrew casks.

### Command-line Options

- `--list-apps`: List all applications found in /Applications
- `--app [APP_NAME]`: Process a specific application by name
- `--reset-history`: Clear the migration history file
- `--batch`: Run in batch mode, automatically install top match
- `--retry-skipped`: Retry apps previously skipped

### Examples

```shell
# List all applications in /Applications
./brew_migrator.py --list-apps

# Migrate a specific application
./brew_migrator.py --app "Firefox"

# Clear migration history
./brew_migrator.py --reset-history
```

## Creating and Using a Brewfile

After migrating your applications, create a Brewfile to capture your environment:

```bash
brew bundle dump
```

This generates a Brewfile containing all your Homebrew-managed packages, casks, and taps.

### Setting Up a New Machine

1. Install Homebrew on the new device
2. Copy your Brewfile to the new machine
3. Run `brew bundle`

This will install all applications and packages listed in your Brewfile, effectively replicating your setup.

## Migration History

The script maintains a history file at `~/.brew_migrator_history` tracking your migration progress.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
