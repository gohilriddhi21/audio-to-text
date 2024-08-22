"""Preprocessor module for text preprocessing."""
import os
import re
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Preprocessor:
    """Class for text preprocessing."""

    def _remove_prefix(self, text, prefix):
        """Remove prefix 'Transcribed Text: ' from text."""
        if text.startswith(prefix):
            return text[len(prefix):].strip()
        return text

    def preprocess(self, text):
        """Preprocess the text."""
        logging.info("Starting text preprocessing...")

        try:
            text = self._remove_prefix(text, "Transcribed Text:")
            text = text.lower()
            text = re.sub(r'\.\.\.+', ' ', text)
            text = re.sub(r'[^a-z\s]', '', text)
            text = re.sub(r'\s+', ' ', text).strip()

            logging.info("Text preprocessing completed successfully")
            return text
        except Exception as e: #pylint: disable=broad-except
            logging.error("An error occurred during text preprocessing: %s", e)
            return None

    def read_file(self, file_path):
        """Read the text file."""
        with open(file_path, 'r', encoding="utf-8") as file:
            return file.read()

    def save_preprocessed_text(self, preprocessed_text, file_path):
        """"Save the preprocessed text to the file."""
        with open(file_path, 'a', encoding="utf-8") as file:
            file.write("\n\nPreprocessed Text:\n")
            file.write(preprocessed_text)


def process_files_in_directory(transcribed_file_dir):
    """Preprocess all text files in the directory."""
    preprocessor = Preprocessor()
    for file in os.listdir(transcribed_file_dir):
        if file.endswith('.txt'):
            file_path = os.path.join(transcribed_file_dir, file)
            logging.info("Processing file %s", file_path)

            text = preprocessor.read_file(file_path)

            preprocessed_text = preprocessor.preprocess(text)
            logging.debug("Preprocessed text: %s", preprocessed_text)

            preprocessor.save_preprocessed_text(preprocessed_text, file_path)
            logging.info("Saved Preprocessed text.")


if __name__ == "__main__":
    TRANSCRIBED_FILE_DIR = "transcribed_text_files"
    process_files_in_directory(TRANSCRIBED_FILE_DIR)
