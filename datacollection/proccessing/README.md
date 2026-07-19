# JSON Validator

A utility for validating and cleaning up compressed JSON files collected by the scraper.

## Purpose

This tool processes the JSON files created by `ScrapeRoutes.py` to:
- Identify empty or invalid JSON responses
- Remove empty files to save disk space
- Report statistics on data quality

## Usage

```bash
python JsonValidator.py -i <input_directory>
```

### Arguments

| Argument | Description |
|----------|-------------|
| `-i, --input` | Parent directory containing JSON files (required) |
| `-dc, --decompress` | Decompress files before validation (default: True) |
| `--no_delete` | Report empty files without deleting them |

## How It Works

1. Recursively walks through all subdirectories
2. For each `.json` file:
   - Reads the file (optionally decompresses with zstandard)
   - Checks if content is empty (`None` or `"[]"`)
   - Removes the file if empty (unless `--no_delete` is set)
3. Reports total statistics at the end

## Limitations

- Not intended for use with very large JSON files (may run out of memory)
- Files are loaded entirely into RAM for validation

## Example

```bash
# Validate and clean data/raw directory
python JsonValidator.py -i data/raw

# Check for empty files without deleting
python JsonValidator.py -i data/raw --no_delete