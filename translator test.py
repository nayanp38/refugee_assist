from googletrans import Translator
import re

t = Translator()
message = 'Hello! My name is RefugeeAssist. I am a chatbot designed to help you find the information you need as a refugee. I see you.'
trans_text = t.translate(message, src='en', dest='ru').text
with_spaces = re.sub(r'(\d+\.\d+|\b[A-Z](?:\.[A-Z])*\b\.?)|([.,;:!?)])\s*', lambda x: x.group(1) or f'{x.group(2)} ', trans_text)
print(trans_text)
print(with_spaces)
