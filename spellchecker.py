from pyaspeller import YandexSpeller

speller = YandexSpeller()

def suggest(text):
    changes = {change['word']: change['s'][0] for change in speller.spell(text)}
    for word, suggestion in changes.items():
        text = text.replace(word, suggestion)
    return text