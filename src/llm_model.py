import os
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
import sys
sys.path.append('config')
from config_extraction import ConfigExtraction

class TextSummarizerModel:
    def __init__(self, api_key='', model='gpt-3.5-turbo-1106', temperature=0.1):
        os.environ["OPENAI_API_KEY"] = ConfigExtraction().OPENAI_API_KEY
        self.llm = ChatOpenAI(temperature=temperature, model=model)
        self.chain = load_summarize_chain(self.llm, chain_type="stuff")

    def summarize_text(self, text_path):
        loader = TextLoader(text_path)
        docs = loader.load()
        return self.chain.invoke(docs, return_only_outputs=True)["output_text"]

if __name__ == "__main__":
    summarizer = TextSummarizerModel()
    summary = summarizer.summarize_text("transcribed_text_files/sample_audio.txt")
    print(summary)