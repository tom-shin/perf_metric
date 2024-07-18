from lib.chatbot_eveluator import ChatbotEvaluator

models = [
"gemma2:latest",
"phi3:3.8b",
"mistral:latest",
"gemma:latest",
"llama3:latest",
"llama2-uncensored:latest"
]

for m in models:
    for i in range(30):
        chatbot_eval = ChatbotEvaluator()
        chatbot_eval.load_data("/workspace/cli_library/test/scenarios.json")

        chatbot_eval.set_ragas(
            llm_model = m, 
            embedding_model = "mxbai-embed-large:latest",
            temperature = 0
        )
        chatbot_eval.evaluate_all(None, ["Ragas"])
        chatbot_eval.export_data(f"./test/result_{m}_{i:02d}.json")