import argostranslate.package
import argostranslate.translate
 
print("trying to install the models online")
from_code = "en"
#to_code = "es"
to_code_list = ["fa","fr","es","zh","de","ru","ja"]

# Download and install Argos Translate package online
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
for to_code in to_code_list:
    try: 
        # Translate
        translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
        print(translatedText)
    except:

        package_to_install = next(
            filter(
                lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
            )
        )
        print("downloading the package")
        argostranslate.package.install_from_path(package_to_install.download())



print("trying to install the models offline")

from_code = "en"
to_code = "fa"

try:
    print("check if translate model is installed")
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
    print("check if translate model is installed")
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)
except:
    #install french
    print("installing the offline model")
    argostranslate.package.install_from_path('./argos_packages_offline/translate-en_fr-1_0.argosmodel')
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)


to_code = "es"

try:
    print("check if translate model is installed")
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)
except:
    #install espaniol
    print("installing the offline model")
    argostranslate.package.install_from_path('./argos_packages_offline/translate-en_es-1_0.argosmodel')
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)

to_code = "zh"

try:
    print("check if translate model is installed")
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)
except:
    #install chinease
    print("installing the offline model")
    argostranslate.package.install_from_path('./argos_packages_offline/translate-en_zh-1_7.argosmodel')
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)


#install german
to_code = "de"

try:
    print("check if translate model is installed")
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)
except:
    #install german
    print("installing the offline model")
    argostranslate.package.install_from_path('./argos_packages_offline/translate-en_de-1_0.argosmodel')
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)


#install russian
to_code = "ru"


try:
    print("check if translate model is installed")
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
    print("check if translate model is installed")
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)
except:
    #install japenease
    print("installing the offline model")
    argostranslate.package.install_from_path('./argos_packages_offline/translate-en_ja-1_1.argosmodel')
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)

  

#import argostranslate.package
#import argostranslate.translate

print("Done installing")
