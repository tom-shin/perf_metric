from lib.chatbot_eveluator import ChatbotEvaluator
from lib.testset_generator import TestGenerator
from lib.data_loader import DataLoader

import pandas

models = [
# "tinyllama:latest",
# "phi3:3.8b",
# "llama2:latest",
# "llama3:latest",
# "gemma2:latest",
"OpenAI",
]

for m in models:
    for i in range(1):
        chatbot_eval = ChatbotEvaluator()
        chatbot_eval.load_data("/workspace/cli_library/test/RAGAS_doc_only.json")

        chatbot_eval.set_ragas(
            llm_model = m if m != "OpenAI" else None, 
            temperature = 0
        )
        chatbot_eval.evaluate_all(None, ["Ragas"])
        chatbot_eval.export_data(f"./test/result_{m}_{i:02d}.json")


# data = DataLoader.load_markdown("/workspace/cli_library/test/README.md")

# test_generator = TestGenerator()
# testset = test_generator.generate(data)

# data = [{
#     "question": row["question"],
#     "contexts": row["contexts"],
#     "ground_truth": row["ground_truth"],
#     "evolution_type": row["evolution_type"],
#     "metadata": row["metadata"],
# } for index, row in testset.iterrows()]

# DataLoader.dump_json(data, "./test/testset.json")