from spellchecker import SpellChecker
import re
spell = SpellChecker()

# Helper functions for API only

def get_OU(user_dn: str) -> str:
    """Extract the organizational unit from the user's distinguished name."""
    ou_pattern = re.compile(r'OU=([^,]+)')
    ou_matches = ou_pattern.findall(user_dn)
    return ou_matches if ou_matches else ""

def get_CN(user_dn: str) -> str:
    """Extract the common name from the user's distinguished name."""
    cn_pattern = re.compile(r'CN=([^,]+)')
    cn_matches = cn_pattern.findall(user_dn)
    return cn_matches[0] if cn_matches else ""

def replace_spaces(text: str) -> str:
    """Replace spaces with underscores in the text."""
    return text.replace(" ", "_")

# Helper functions for both API and Streamlit App

def fetch_line_from_file(file_path, line_number):
    """Fetches a specific line from a text file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        for _ in range(line_number - 1):
            file.readline()
        return file.readline().strip()

def handle_misspell(query):
    """
    Corrects misspelled words in a query. Returns a flag indicating the status of correction along with the corrected query.
    Flag values: 1 - No misspelled words, 2 - Misspelled words corrected, 3 - Misspelled words not corrected
    """
    misspelled = spell.unknown(query.split())
    flag = 1 # No misspelled words
    if misspelled:
        try:
            flag = 2 # Misspelled words corrected
            for word in misspelled:
                query = query.replace(word, spell.correction(word))
        except:
            flag = 3 # Misspelled words not corrected
    return flag, query