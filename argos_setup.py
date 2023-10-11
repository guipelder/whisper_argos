
import argostranslate.package
import argostranslate.translate
 
from_code = "en"
to_code = "fa"

try:
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)
except:
    #install farsi
    print("installing the offline model")
    argostranslate.package.install_from_path('./argos_packages_offline/translate-en_fa-1_5.argosmodel')
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)

    # Translate
    # '¡سلام دنیا!'

to_code = "fr"



try:
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)
except:
    #install french
    print("installing the offline model")
    argostranslate.package.install_from_path('./argos_packages_offline/en_fr.argosmodel')
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)

    


to_code = "es"


try:
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)
except:
    #install espaniol
    print("installing the offline model")
    argostranslate.package.install_from_path('./argos_packages_offline/en_es.argosmodel')
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)

    


to_code = "zh"


try:
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)
except:
    #install chinease
    print("installing the offline model")
    argostranslate.package.install_from_path('./argos_packages_offline/translate-en_zh-1_1.argosmodel')
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)

    



#install german
to_code = "de"

try:
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)
except:
    #install german
    print("installing the offline model")
    argostranslate.package.install_from_path('./argos_packages_offline/translate-en_de-1_5.argosmodel')
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)



#install russian
to_code = "ru"


try:
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)
except:
    #install russian
    print("installing the offline model")
    argostranslate.package.install_from_path('./argos_packages_offline/translate-en_ru-1_7.argosmodel')
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)

    


#install japenease
to_code = "ja"

try:
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)
except:
    #install japenease
    print("installing the offline model")
    argostranslate.package.install_from_path('./argos_packages_offline/translate-en_ja-1_1.argosmodel')
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)




