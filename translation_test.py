from googletrans import Translator

translator = Translator()
text = """I understand you're struggling with your mental health, and it's important to seek help.  As a refugee, you have access to many resources in the United States. 

Here are some things you can do:

* **Contact a mental health professional:** You can find therapists and counselors who specialize in working with refugees. 
* **Reach out to organizations that support refugees:** Many organizations provide mental health services specifically for refugees. They can help you find resources and connect you with support groups. 
* **Talk to your doctor:** Your doctor can refer you to mental health professionals and help you navigate the healthcare system.

It's important to know that you're not alone. Many refugees experience mental health challenges due to the trauma they have faced. Seeking help is a sign of strength, and it can make a big difference in your well-being. 

Would you like me to help you find some resources in your area? I can help you find mental health professionals, refugee support organizations, and other resources that can provide support. 
"""

print(translator.translate(text, dest='ur').text)