# COBOL Structure Generator from JSON

This script converts a JSON structure into a COBOL data structure. It reads the JSON data from an input file, processes it according to predefined rules and abbreviations, and outputs the corresponding COBOL structure.

## Features

- **Abbreviation Management**: Uses a CSV file to map full words to their abbreviations for generating COBOL structure names.
- **Camel Case Splitting**: Parses camel case words in the JSON keys and abbreviates them accordingly.
- **COBOL Data Type Mapping**: Determines the appropriate COBOL PIC clause based on the data type and value in the JSON.

## Requirements

- Python 3.x
- No external Python libraries are required.

## Usage

1. Place your JSON data in a file named `input.json`.
2. If you have custom abbreviations, add them to `siglas.csv`. The format is `full_word,abbreviation`.
3. Run the script:
   ```
   python script_name.py
   ```
4. The COBOL structure will be saved in `output.txt`.

## Configuration

To adjust configurations like indentation, PIC clause lengths, etc., modify the values in the `Config` class within the script.
