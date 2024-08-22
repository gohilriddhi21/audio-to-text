import os
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class TextSummarizerModel:
    def __init__(self, api_key='', model='gpt-3.5-turbo-1106', temperature=0.1):
        self.llm = ChatOpenAI(temperature=temperature, model=model)
        self.chain = load_summarize_chain(self.llm, chain_type="stuff")

    def summarize_text(self, text_path):
        loader = TextLoader(text_path)
        docs = loader.load()
        return self.chain.invoke(docs, return_only_outputs=True)["output_text"]
    
    def save_summarization_to_file(self, file_name, summary):
        with open(file_name, "a") as f:
            f.write("\n\nSummarization: \n")
            f.write(summary)

def process_files_in_directory(transcribed_files_dir):
    summarizer = TextSummarizerModel()
    for file in os.listdir(transcribed_files_dir):
        if file.endswith('.txt'):
            file_name = os.path.join(transcribed_files_dir, file)
            logger.info(f"Processing File {file_name}")
            
            summary = summarizer.summarize_text(file_name)
            logger.info(f"Summary: {summary}")
            
            summarizer.save_summarization_to_file(file_name, summary)
            logger.info("Successfully saved summarization to file.")

if __name__ == "__main__":
    transcribed_files_dir = "transcribed_text_files"
    process_files_in_directory(transcribed_files_dir)
          