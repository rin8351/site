from googletrans import Translator

def translate_to_slavic(text: str) -> str:
    """
    Translates given text to Ukrainian, Russian and Belorussian languages.
    Returns concatenated translations separated by comma.
    
    Args:
        text (str): Text to translate
        
    Returns:
        str: Comma-separated translations
    """
    translator = Translator()
    
    # Target language codes
    target_languages = ['uk', 'ru', 'be']  # Ukrainian, Russian, Belorussian
    translations = []
    
    for lang in target_languages:
        result = translator.translate(text, dest=lang)
        translations.append(result.text)
    
    return ', '.join(translations)

def main():
    print(translate_to_slavic("Hello, world!"))

if __name__ == "__main__":
    main()