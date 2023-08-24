import json
import csv
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    # Indentation Configurations
    INDENTATION_STEP = 1  # Amount of indentation for inner fields from objects
    PIC_INDENTATION = 46  # Amount of indentation for "PIC" snippets

    # Field Length Configurations
    PIC_STRING_LENGTH = 100  # Length for string fields
    PIC_NUMBER_LENGTH = 10  # Length for number fields with more than 2 digits
    PIC_SMALL_NUMBER_LENGTH = 2  # Length for number fields with 2 or less digits

class AbbreviationManager:
    def __init__(self, csv_path):
        self.abbreviations = self._load_abbreviations_from_csv(csv_path)
        self.special_abbreviations = {
            "nm": "NM",
            "nr": "NR",
            "tp": "TIP",
            "id": "IDFR",
            "in": "IN",
            "pc": "PC"
        }

    @staticmethod
    def _load_abbreviations_from_csv(csv_path):
        abbreviations = {}
        with open(csv_path, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                full_word, abbreviation = row
                abbreviations[full_word.lower()] = abbreviation.upper()
        return abbreviations

    def get_abbreviation(self, word):
        return self.special_abbreviations.get(word.lower(), self.abbreviations.get(word.lower(), word))

    @staticmethod
    def split_camel_case(word):
        """Split a camelCase word into individual words."""
        return re.findall(r'(?:^|[A-Z])[a-z]*', word)

    def camel_case_to_abbreviation(self, word):
        individual_words = self.split_camel_case(word)
        return '-'.join([self.get_abbreviation(w) for w in individual_words])

class CobolLineFactory:
    @staticmethod
    def determine_pic_type(value):
        if isinstance(value, str):
            return f"PIC X({Config.PIC_STRING_LENGTH})."
        elif isinstance(value, (int, float)):
            if len(str(abs(value))) > 2:  # If the value has more than 2 digits
                return f"PIC 9({Config.PIC_NUMBER_LENGTH}) COMP-3."
            else:
                return f"PIC 9({Config.PIC_SMALL_NUMBER_LENGTH})."
        else:
            return None

    @staticmethod
    def create_cobol_line(lev, key, pic_type, ind=0):
        line_without_pic = " " * ind + f"{lev:02} {key}"
        spaces_needed = Config.PIC_INDENTATION - len(line_without_pic)
        line = line_without_pic + " " * spaces_needed + pic_type.split(" COMP-3.")[0]
        if "COMP-3." in pic_type:
            return [line, " " * Config.PIC_INDENTATION + "COMP-3."]
        return [line]

    @staticmethod
    def create_cobol_list_line(lev, key, ind=0):
        return [
            *CobolLineFactory.create_cobol_line(lev, f"QT-{key}", f"PIC 9({Config.PIC_SMALL_NUMBER_LENGTH}).", ind),
            " " * ind + f"{lev:02} LS-{key} OCCURS 0 TO 10 TIMES DEPENDING ON QT-{key}"
        ]

def json_to_cobol(data, abbrev_manager, lev=3, ind=0):
    cobol_structure = []
    prev_line = None

    def add_to_cobol_structure(line):
        nonlocal prev_line
        if line != prev_line:
            cobol_structure.append(line)
            prev_line = line

    for key, value in data.items():
        abbreviated_key = abbrev_manager.camel_case_to_abbreviation(key)
        
        if "lista" in key.lower():
            abbreviated_key = abbreviated_key.replace("LS-", "", 1)

        if isinstance(value, dict):
            add_to_cobol_structure(" " * ind + f"{lev:02} {abbreviated_key}.")
            cobol_structure.extend(json_to_cobol(value, abbrev_manager, lev + 2, ind + Config.INDENTATION_STEP))
        elif isinstance(value, list):
            for line in CobolLineFactory.create_cobol_list_line(lev, abbreviated_key, ind):
                add_to_cobol_structure(line)

            if value and isinstance(value[0], dict):
                cobol_structure.extend(json_to_cobol(value[0], abbrev_manager, lev + 2, ind + Config.INDENTATION_STEP))
            else:
                pic_type = CobolLineFactory.determine_pic_type(value[0]) if value else f"PIC X({Config.PIC_STRING_LENGTH})."
                for line in CobolLineFactory.create_cobol_line(lev + 2, f"{abbreviated_key}-ITEM", pic_type, ind + Config.INDENTATION_STEP):
                    add_to_cobol_structure(line)
        else:
            pic_type = CobolLineFactory.determine_pic_type(value)
            for line in CobolLineFactory.create_cobol_line(lev, abbreviated_key, pic_type, ind):
                add_to_cobol_structure(line)

    return cobol_structure

def main():
    try:
        with open("input.json", "r") as file:
            json_data = json.load(file)
        
        abbrev_manager = AbbreviationManager("siglas.csv")
        cobol_output = json_to_cobol(json_data, abbrev_manager)
        
        with open("output.txt", "w") as out_file:
            for line in cobol_output:
                out_file.write(line + "\n")
        logger.info("Conversion completed successfully.")
    except Exception as e:
        logger.error(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
