import json

file_path = './finetune-training-data.jsonl'  # Replace with the actual file path
with open(file_path, 'r') as f:
    for i, line in enumerate(f, 1):
        try:
            json.loads(line.strip())
        except json.JSONDecodeError as e:
            print(f"Error on line {i}: {e}")
