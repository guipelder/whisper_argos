import argostranslate.package
import argostranslate.translate
 
from_code = "en"
to_code = "fa"

#install arabic
argostranslate.package.install_from_path('./argos_packages_offline/translate-en_fa-1_5.argosmodel')

# Translate
translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
print(translatedText)
# '¡سلام دنیا!'

to_code = "fr"

#install  french
argostranslate.package.install_from_path('./argos_packages_offline/en_fr.argosmodel')

# Translate
translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
print(translatedText)


to_code = "es"

#install espaniol
argostranslate.package.install_from_path('./argos_packages_offline/en_es.argosmodel')

# Translate
translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
print(translatedText)

to_code = "zh"

#install chinease
argostranslate.package.install_from_path('./argos_packages_offline/translate-en_zh-1_1.argosmodel')



# Translate
translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
print(translatedText)


#install german
to_code = "de"

argostranslate.package.install_from_path('./argos_packages_offline/translate-en_de-1_5.argosmodel')
# Translate
translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
print(translatedText)

#install russian
to_code = "ru"


argostranslate.package.install_from_path('./argos_packages_offline/translate-en_ru-1_7.argosmodel')

# Translate
translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
print(translatedText)

#install japenease
to_code = "ja"
argostranslate.package.install_from_path('./argos_packages_offline/translate-en_ja-1_1.argosmodel')

# Translate
translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
print(translatedText)



