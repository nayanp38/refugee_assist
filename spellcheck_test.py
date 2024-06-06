from spellchecker import SpellChecker

spell = SpellChecker()
spell.word_frequency.load_text_file('my_free_text_doc.txt')

print(spell.word_frequency.load_words(['microsoft', 'apple', 'google']))
print(spell.known(['microsoft', 'google']))