from collections import defaultdict
from pandas import DataFrame
from openai import AuthenticationError
import random
import json
import time
from . import (
    openai_client as client,
    CONFIG,
    GPT_INSTRUCTIONS,
    tg_model,
    error_invalidkey,
)


def ft_errorcheck(json_data: list) -> bool:
    format_errors = defaultdict(int)

    for ex in json_data:
        if not isinstance(ex, dict):
            format_errors["data_type"] += 1
            continue

        messages = ex.get("messages", None)
        if not messages:
            format_errors["missing_messages_list"] += 1
            continue

        for message in messages:
            if "role" not in message or "content" not in message:
                format_errors["message_missing_key"] += 1

            if any(
                k not in ("role", "content", "name", "function_call") for k in message
            ):
                format_errors["message_unrecognized_key"] += 1

            if message.get("role", None) not in (
                "system",
                "user",
                "assistant",
                "function",
            ):
                format_errors["unrecognized_role"] += 1

            content = message.get("content", None)
            function_call = message.get("function_call", None)

            if (not content and not function_call) or not isinstance(content, str):
                format_errors["missing_content"] += 1

        if not any(message.get("role", None) == "assistant" for message in messages):
            format_errors["example_missing_assistant_message"] += 1

    if format_errors:
        print("Found errors:")
        for k, v in format_errors.items():
            print(f"{k}: {v}")
        return False
    return True


def generate_model(model: str, json_list: list) -> str | None:
    # Load model parameters
    """
    training_parameters = {
        'prompt': 'Write a story about...',
        'max_tokens': 1024,
        'temperature': 0.7,
        'n_epochs': 3,
        'batch_size': 16
    }
    """
    # Split data to training vs validation
    random_selection = random.sample(
        range(len(json_list)), int(len(json_list) * CONFIG["FINE_TUNING"]["RATIO"])
    )
    print(
        f"{len(random_selection)}/{len(json_list)} validation data selected: {random_selection}"
    )
    with open(CONFIG["FINE_TUNING"]["TRAIN_PATH"], "w") as f:
        for i in range(len(json_list)):
            if i not in random_selection:
                json.dump(json_list[i], f)
                f.write("\n")
    with open(CONFIG["FINE_TUNING"]["VALID_PATH"], "w") as f:
        for i in random_selection:
            json.dump(json_list[i], f)
            f.write("\n")

    # Generate fine tuned model
    with open(CONFIG["FINE_TUNING"]["TRAIN_PATH"], "rb") as f:
        training_file = client.files.create(file=f, purpose="fine-tune")
    with open(CONFIG["FINE_TUNING"]["VALID_PATH"], "rb") as f:
        validation_file = client.files.create(file=f, purpose="fine-tune")
    tuning_job = client.fine_tuning.jobs.create(
        training_file=training_file.id,
        validation_file=validation_file.id,
        model=model,
    )

    # Wait for job completion
    event_count = 0
    while tuning_job.status not in ("succeeded", "failed", "cancelled"):
        time.sleep(1)
        tuning_job = client.fine_tuning.jobs.retrieve(tuning_job.id)
        events = client.fine_tuning.jobs.list_events(tuning_job.id).data
        while len(events) > event_count:
            print(events[len(events) - event_count - 1].message)
            event_count += 1

    # Delete files
    client.files.delete(training_file.id)
    client.files.delete(validation_file.id)

    print("The fine tuning job has " + tuning_job.status)
    if tuning_job.status == "succeeded":
        return tuning_job.fine_tuned_model
    return None


def process_ft_input(ft_df: DataFrame) -> list[dict]:
    """
    Convert ['Question', 'Content', 'Answer'] pair into list of JSONs, then check for valid format
    """
    print("Received fine tuning training data.")
    json_list = []
    for i in ft_df.index:
        json_list.append(
            {
                "messages": [
                    {
                        "role": "system",
                        "content": GPT_INSTRUCTIONS,
                    },
                    {
                        "role": "system",
                        "name": "context_provider",
                        "content": ft_df["Content"][i].replace("\n", "\\n"),
                    },
                    {
                        "role": "user",
                        "content": ft_df["Question"][i],
                    },
                    {
                        "role": "assistant",
                        "content": ft_df["Answer"][i],
                    },
                ]
            }
        )
    if not ft_errorcheck(json_list):
        print("Fine tuning training data validation failed.")
        return []
    return json_list


def generate_ft_model(json_data=list[dict]):
    "Start OpenAI fine tuning job using TUNING_DATA_JSON, save ID to tg_model"
    if not ft_errorcheck(json_data):
        return
    try:
        model_id = generate_model(tg_model.base_model, json_data)
    except AuthenticationError:
        error_invalidkey()
        return
    tg_model.set_model(model_id)
