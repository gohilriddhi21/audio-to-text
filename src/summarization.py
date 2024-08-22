"""Summarizes the transcribed text using an LLM model."""
import os
import logging
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class TextSummarizerModel:
    """Model Class for Text Summarization."""
    def __init__(self, model='gpt-3.5-turbo-1106', temperature=0.1):
        self.llm = ChatOpenAI(temperature=temperature, model=model)
        self.chain = load_summarize_chain(self.llm, chain_type="stuff")

    def summarize_text(self, text_path):
        """Summarizes the text in the specified file."""
        loader = TextLoader(text_path)
        docs = loader.load()
        return self.chain.invoke(docs, return_only_outputs=True)["output_text"]

    def save_summarization_to_file(self, file_name, summary):
        """Saves the summarization to the specified file."""
        with open(file_name, "a", encoding="utf-8") as f:
            f.write("\n\nSummarization: \n")
            f.write(summary)



def process_files_in_directory(directory):
    """Processes all transcribed text files in the specified directory."""
    summarizer = TextSummarizerModel()
    for file in os.listdir(directory):
        if file.endswith('.txt'):
            file_path = os.path.join(directory, file)
            logger.info("Processing file %s", file_path)

            summary = summarizer.summarize_text(file_path)
            logger.info("Summary: %s", summary)

            summarizer.save_summarization_to_file(file_path, summary)
            logger.info("Successfully saved summarization to file.")



if __name__ == "__main__":
    TRANSCRIBED_FILES_DIR = "transcribed_text_files"
    process_files_in_directory(TRANSCRIBED_FILES_DIR)
