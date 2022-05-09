import random
import json
#import google_trans_new
import googletrans
import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
#from google_trans_new  import google_translator
from googletrans import Translator

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r',encoding='utf-8') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()
# translator = google_translator()
translator = Translator()

bot_name = "Smart Boarding"

def get_response(msg):
    translated_sentence = translator.translate(msg, lang_src='ja', lang_tgt='en')
    sentence = tokenize(translated_sentence.text)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])
    
    return "分かりません"

if __name__ == "__main__":
    print("初めまして! ('Q' を入力すると終了される)")
    # print(googletrans.LANGUAGES)
    while True:
        sentence = input("あなた: ")
        if sentence == "Q":
            break

        resp = get_response(sentence)
        print(resp)
        # sentence = tokenize(translated_sentence.text)
        # X = bag_of_words(sentence, all_words)
        # X = X.reshape(1, X.shape[0])
        # X = torch.from_numpy(X).to(device)

        # output = model(X)
        # _, predicted = torch.max(output, dim=1)

        # tag = tags[predicted.item()]

        # probs = torch.softmax(output, dim=1)
        # prob = probs[0][predicted.item()]
        # if prob.item() > 0.75:
        #     for intent in intents['intents']:
        #         if tag == intent["tag"]:
        #             print(f"{bot_name}: {random.choice(intent['responses'])}")
        # else:
        #     print(f"{bot_name}: 分かりません")