import argparse

from lib.chatbot_eveluator import ChatbotEvaluator

def is_different(value1, value2):
    return abs(value1 - value2) > 0.0001

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Chatbot')
    parser.add_argument('tests', metavar='TEST_NAME', nargs='+', help='a test to run')
    parser.add_argument('-m', '--model_dir', required=True, help='the location of test models')
    parser.add_argument('-d', '--data_dir', required=True, help='the location of test data')
    args = parser.parse_args()

    chatbot_eval = ChatbotEvaluator()
    chatbot_eval.load_data(args.data_dir)

    chatbot_eval.evaluate_all(args.model_dir, args.tests)
    chatbot_eval.set_ragas()
    # chatbot_eval.print_scores()

    chatbot_eval.export_data()

