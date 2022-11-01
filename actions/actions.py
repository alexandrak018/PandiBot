# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import random
import re
import time
from typing import Any, Text, Dict, List
import torch
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import transformers
from transformers import BartTokenizer, BartForConditionalGeneration

#CUDA
device = "cuda" if torch.cuda.is_available() else "cpu"

#PEGASUS
from transformers import PegasusForConditionalGeneration, PegasusTokenizerFast
tokenizer = PegasusTokenizerFast.from_pretrained("tuner007/pegasus_paraphrase")
model = PegasusForConditionalGeneration.from_pretrained("tuner007/pegasus_paraphrase").to(device)

rls = ["I see that you think that ", "You feel that ", "So you feel that ", "I understood, ", "I see that ", "So what I’m hearing is that ",
       "It sounds like ", "You’ve been trying to tell me that ", "Some of what I heard you say is that ",
       "If I heard you correctly, this is what I think you are saying: "]

#HUGGINGFACE SUMMARIZER
from transformers import T5Tokenizer, T5ForConditionalGeneration
tokenizer2 = T5Tokenizer.from_pretrained('t5-small')
model2 = T5ForConditionalGeneration.from_pretrained('t5-small').to(device)

#LIST PRO CONS MULTI
pro_list = []
cons_list = []
multiple_list = []

#SPOONS QUESTIONS
spoons = ""

class ActionSummarizePro(Action):

    def name(self) -> Text:
        return "action_summarize_pro"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any], message_list=[]) -> List[Dict[Text, Any]]:

        print(pro_list)

        new = ' '.join(pro_list)

        print(pro_list)

        def summarize(text):
            inputs = tokenizer2.batch_encode_plus(["summarize: " + text], max_length=720, return_tensors="pt", pad_to_max_length=True).to(device)
            outputs = model2.generate(inputs['input_ids'], num_beams=100, max_length=500, min_length = 5, early_stopping=True)
            summary = tokenizer2.batch_decode(outputs, skip_special_tokens=True, clean_up_tokenization_spaces=False)
            return summary

        summary = summarize(new)
        bot_msg = ' '.join(summary)
        bot_msg2 = '. '.join(map(lambda s: s.strip().capitalize(), bot_msg.split('.')))
        dispatcher.utter_message("So, from what you have said, sugar is good because: " + bot_msg2)

        return []


class ActionSummarizeCons(Action):

    def name(self) -> Text:
        return "action_summarize_cons"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any], message_list=[]) -> List[Dict[Text, Any]]:

        new = ' '.join(cons_list)

        def summarize(text):
            inputs = tokenizer2.batch_encode_plus(["summarize: " + text], max_length=720, return_tensors="pt", pad_to_max_length=True).to(device)
            outputs = model2.generate(inputs['input_ids'], num_beams=100, max_length=500, min_length = 5, early_stopping=True)
            summary = tokenizer2.batch_decode(outputs, skip_special_tokens=True, clean_up_tokenization_spaces=False)
            return summary

        summary = summarize(new)
        bot_msg = ' '.join(summary)
        bot_msg2 = '. '.join(map(lambda s: s.strip().capitalize(), bot_msg.split('.')))
        dispatcher.utter_message("And consuming sugar is bad because: " + bot_msg2)

        return []

class ActionSummarize(Action):


    def name(self) -> Text:
        return "action_summarize"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any], message_list=[]) -> List[Dict[Text, Any]]:

        new = ' '.join(multiple_list)
        def summarize(text):
            inputs = tokenizer2.batch_encode_plus(["summarize: " + text], max_length=720,
                                                  return_tensors="pt", pad_to_max_length=True).to(device)
            outputs = model2.generate(inputs['input_ids'], num_beams=100, max_length=500,
                                      min_length = 5, early_stopping=True)
            summary = tokenizer2.batch_decode(outputs, skip_special_tokens=True,
                                              clean_up_tokenization_spaces=False)
            return summary

        summary = summarize(new)
        bot_msg = ' '.join(summary)
        bot_msg2 = '. '.join(map(lambda s: s.strip().capitalize(), bot_msg.split('.')))
        dispatcher.utter_message(bot_msg2)

        return []

class ActionCollectProAnswers(Action):

    def name(self) -> Text:
        return "action_collect_pro_answers"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any], message_list=[]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message["text"]
        line = re.sub(r'\b[i|I]\b', 'you', message)
        line = re.sub(r'\b[m|M]e\b', 'you', line)
        line = re.sub(r'\b[m|M]y\b', 'your', line)
        line = re.sub(r'\b[m|M]ine\b', 'yours', line)
        line = re.sub(r'\b[m|M]yself\b', 'yourself', line)
        line = re.sub(r'\bam\b', 'are', line)
        line = re.sub(r'\b[i|i]\'*m\b', 'you are', line)
        message = line.capitalize()
        if not message.endswith('.'):
            message += '.'
        pro_list.append(message)
        print(pro_list)

        return []

class ActionCollectConsAnswers(Action):

    def name(self) -> Text:
        return "action_collect_cons_answers"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any], message_list=[]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message["text"]
        line = re.sub(r'\b[i|I]\b', 'you', message)
        line = re.sub(r'\b[m|M]e\b', 'you', line)
        line = re.sub(r'\b[m|M]y\b', 'your', line)
        line = re.sub(r'\b[m|M]ine\b', 'yours', line)
        line = re.sub(r'\b[m|M]yself\b', 'yourself', line)
        line = re.sub(r'\bam\b', 'are', line)
        line = re.sub(r'\b[i|i]\'*m\b', 'you are', line)
        message = line.capitalize()
        if not message.endswith('.'):
            message += '.'
        cons_list.append(message)
        print(cons_list)

        return []

class ActionCollectAnswers(Action):

    def name(self) -> Text:
        return "action_collect_answers"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any], message_list=[]) -> List[Dict[Text, Any]]:
        message = tracker.latest_message["text"]

        line = re.sub(r'\b[i|I]\b', 'you', message)
        line = re.sub(r'\b[m|M]e\b', 'you', line)
        line = re.sub(r'\b[m|M]y\b', 'your', line)
        line = re.sub(r'\b[m|M]ine\b', 'yours', line)
        line = re.sub(r'\b[m|M]yself\b', 'yourself', line)
        line = re.sub(r'\bam\b', 'are', line)
        line = re.sub(r'\b[i|i]\'*m\b', 'you are', line)
        message = line.capitalize()
        if not message.endswith('.'):
            message += '.'
        multiple_list.append(message)
        print(multiple_list)

        return []

class ActionParaphrase(Action):

    def name(self) -> Text:
        return "action_paraphrase"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message["text"].lower()
        if not message.endswith('.'):
            message += '.'

        line = re.sub(r'\b[i|I]\b', 'you', message)
        line = re.sub(r'\b[m|M]e\b', 'you', line)
        line = re.sub(r'\b[m|M]y\b', 'your', line)
        line = re.sub(r'\b[m|M]ine\b', 'yours', line)
        line = re.sub(r'\b[m|M]yself\b', 'yourself', line)
        line = re.sub(r'\bam\b', 'are', line)
        line = re.sub(r'\b[i|i]\'*m\b', 'you are', line)

        match = re.search(r'\b[i|I]t\b', line)

        if (not match):
            inputs = tokenizer([line], truncation=True, padding="longest", return_tensors="pt").to(device)
            outputs = model.generate(
                **inputs,
                num_beams=100,
                num_return_sequences=10,
                min_length = 5
            )
            mes = tokenizer.batch_decode(outputs, skip_special_tokens=True)

            dispatcher.utter_message(random.choice(rls) + str(mes[9]).lower())
        return []

class ActionGender(Action):

    def name(self) -> Text:
        return "action_gender_answer"

    def run(self, dispatcher: CollectingDispatcher, #CHANGE
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message_slot = tracker.slots.get("gender")
        message = tracker.latest_message["text"]
        if message == "male" or message == "Male":
            dispatcher.utter_message(text="Thank you for letting me know! The limit for men is a little higher than for women. Men should not consume more than 9 teaspoons (36 grams or 150 calories) per day.")
        elif message == "female" or message ==  "Female":
            dispatcher.utter_message(text="Thank you for telling me! The limit for women is a little lower than for men and it should be 6 teaspoons (25 grams or 100 calories) per day.")
        elif message == "other" or message == "Other":
            dispatcher.utter_message(text="Thank you for sharing. Men should not consume  more than 9 teaspoons (36 grams or 150 calories) per day while the limit for women is a little lower than for men and it should be 6 teaspoons (25 grams or 100 calories) per day.")
        elif message == "skip" or message == "Skip":
            dispatcher.utter_message(text="That is alright, you should only do things that you are comfortable with.")
        else:
            dispatcher.utter_message(text="I am a bot and my capabilities are limited. Just like a human, I also have to learn.")
        return []


class ActionNoOfSpoon(Action):

    def name(self) -> Text:
        return "action_spoons_answer"


    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = tracker.latest_message["text"]
        message2 = int(message)
        spoons2 = int(spoons)
        if message2 == spoons2:
            dispatcher.utter_message(
                text="That's understandable.")
        elif spoons2 > message2:
            dispatcher.utter_message(
                text="That's great. You don't have problems refraining from sugar.")
        elif spoons2 < message2:
            dispatcher.utter_message(
                text="So it sounds like you kinda struggle with that a little bit sometimes.")
        else:
            dispatcher.utter_message(text="I am a bot and my capabilities are limited. Just like a human, I also have to learn.")
        return []

class ActionCollectSpoons(Action):

    def name(self) -> Text:
        return "action_collect_spoons"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any], message_list=[]) -> List[Dict[Text, Any]]:

        global spoons
        spoons = tracker.latest_message["text"]
        print(spoons)
        return []


class ActionNextWeekPlan(Action):

    def name(self) -> Text:
        return "action_next_week"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = tracker.latest_message["text"]
        message2 = int(message)
        if message2 < 5:
            dispatcher.utter_message(
                text="You don't have to be 100% confident to get started, you just need enough confidence to take the first step. Give it a go!")
        elif message2 >= 5:
            dispatcher.utter_message(
                text="It sounds like something that you know and feel like you can improve on in the next week.")
        else:
            dispatcher.utter_message(text="I am a bot and my capabilities are limited. Just like a human, I also have to learn.")
        return []


class ActionImproveSugar(Action):

    def name(self) -> Text:
        return "action_improve_sugar"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = tracker.latest_message["text"]
        message2 = int(message)
        if message2 < 5:
            dispatcher.utter_message(
                text="You selected "+message+". It sounds like improving your sugar consumption is somewhat important to you. If you don't improve anymore, how do you think it will affect your life?")
        elif message2 >= 5:
            dispatcher.utter_message(
                text="You selected "+message+". It sounds like improving your sugar consumption habits has value to you. Can you give a reason why it is important to you?")
        else:
            dispatcher.utter_message(text="I am a bot and my capabilities are limited. Just like a human, I also have to learn.")
        return []


class ActionBalancedSugar(Action):

    def name(self) -> Text:
        return "action_balanced_sugar"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = tracker.latest_message["text"]
        message2 = int(message)
        if message2 > 1:
            dispatcher.utter_message(
                text="Alright. That is good. You could have chosen a lower number, but you didn't. You chose a "+message+" and not a lower number. Why is it important to you to have a balanced sugar intake?")
        elif message2 == 1:
            dispatcher.utter_message(
                text="Help me understand why did you choose a 1.")
        else:
            dispatcher.utter_message(text="I am a bot and my capabilities are limited. Just like a human, I also have to learn.")
        return []


class ActionLastScale(Action):

    def name(self) -> Text:
        return "action_last_scale"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = tracker.latest_message["text"]
        message2 = int(message)
        if message2 >= 5:
            dispatcher.utter_message(text="It sounds like you are pretty motivated.")
            dispatcher.utter_message(text="Why do you choose a "+message+" and not another number?")
        elif message2 < 5:
            dispatcher.utter_message(text="Don't worry! A lot of people who have come to use have been in the same state as you and are now doing much better.")
            dispatcher.utter_message(text="Why do you choose a " + message + " and not another number?")
        else:
            dispatcher.utter_message(
                text="I am a bot and my capabilities are limited. Just like a human, I also have to learn.")
        return []


