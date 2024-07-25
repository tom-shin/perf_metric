import os

from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context

from langchain_openai import ChatOpenAI, OpenAIEmbeddings


class TestGenerator:
    default_distributions = {
                simple: 0.5,
                multi_context: 0.4,
                reasoning: 0.1
            }
    
    def __init__(self):
        self.generator_llm = ChatOpenAI(model="gpt-4o-mini")
        self.critic_llm = ChatOpenAI(model="gpt-4")
        # self.critic_llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
        self.embeddings = OpenAIEmbeddings()
        
        self.generator = TestsetGenerator.from_langchain(
            self.generator_llm,
            self.critic_llm,
            self.embeddings
        )

        
    
    def generate(
            self, 
            documents, 
            distributions = default_distributions,
            n = 10
            ):

        testset = self.generator.generate_with_langchain_docs(
            documents,
            n,
            distributions
        )

        return testset.to_pandas()