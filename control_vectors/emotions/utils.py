import json
import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from repeng import ControlVector, ControlModel, DatasetEntry
model_name = "mistralai/Mistral-7B-Instruct-v0.1"

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token_id = 0

model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)
model = model.to("cuda:0" if torch.cuda.is_available() else "mps:0" if torch.backends.mps.is_available() else "cpu")
model = ControlModel(model, list(range(-5, -18, -1)))

# process data in a similar way as RepE does it 
template_str = 'Consider the {emotion} of the following scenario:\nScenario: {scenario}'
emotions = ["happiness", "sadness", "anger", "fear", "disgust", "surprise"]
emotion_opposites = {
    "happiness": "sadness",
    "sadness": "happiness",
    "anger": "fear",
    "fear": "anger",
    "disgust": "happiness",
    "surprise": "fear"
}
raw_data = {}
formatted_data = {}
dataset = []
num_samples = 20  # number of samples per emotion

data_dir = './dataset/'
# Train and export a vector for each emotion
for emotion in emotions:
    with open(os.path.join(data_dir, f'{emotion}.json')) as file:
        raw_data[emotion] = list(set(json.load(file)))[:200]
    print(f"\nTraining control vector for {emotion}")
    
    # Filter dataset for current emotion
    emotion_dataset = []
    for scenario in raw_data[emotion]:
        positive = template_str.format(emotion=emotion, scenario=scenario)
        negative_emotion = emotion_opposites[emotion]
        negative = template_str.format(emotion=negative_emotion, scenario=scenario)
        
        emotion_dataset.append(
            DatasetEntry(
                positive=tokenizer.apply_chat_template(conversation=[
                    {
                        "role": "user",
                        "content": positive
                    },
                ],
                tokenize=False,
                padding=True),
                negative=tokenizer.apply_chat_template(conversation=[
                    {
                        "role": "user",
                        "content": negative
                    },
                ],
                tokenize=False,
                ),
            )
        )
    print(f"Loaded {len(emotion_dataset)} samples for {emotion}", emotion_dataset[:5][0].positive)
    # Train vector for this emotion
    vector = ControlVector.train(model, tokenizer, emotion_dataset)
    
    # Test the vector
    device = "cuda:0" if torch.cuda.is_available() else "mps:0" if torch.backends.mps.is_available() else "cpu"
    
    print(f"\nTesting {emotion} vector:")
    for strength in (-2.2, 1, 2.2):
        print(f"strength={strength}")
        model.set_control(vector, strength)
        inputs = tokenizer(
            f"[INST] Give me a one-sentence pitch for a TV show. [/INST]",
            return_tensors="pt"
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        out = model.generate(
            **inputs,
            do_sample=False,
            max_new_tokens=128,
            repetition_penalty=1.1,
        )
        print(tokenizer.decode(out.squeeze()).strip())
        print()
    
    # Export vector as GGUF
    vector.export_gguf(f"{emotion}.gguf")
    print(f"Exported {emotion}.gguf")
    model.reset()