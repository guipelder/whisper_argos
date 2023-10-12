# Introduction
this project is about transcribing the english video files  
and creating english subtitile and the translating and  
adding other subtitles in other languages as subtitle
to the video file. the supported languages are:  
- English
- Spanish
- French
- German
- Russian
- Chinese
- Japanese
- Persian


# Installation
1.run the command below:  
`pip install -r requirements.txt`  
for installing the requirements  

2.run the command below:  
`python3 argos_setup.py`   
for installing the offline argos_translate packages  
(note: either this or you can install the packages online)
the packages that are used originally are as following:


  
- translate-en_fa-1_5.argosmodel  
- en_fr.argosmodel  
- en_es.argosmodel  
- translate-en_zh-1_1.argosmodel  
- translate-en_de-1_5.argosmodel  
- translate-en_ru-1_7.argosmodel  
- translate-en_ja-1_1.argosmodel
  
and their link are as follows:  

- https://pub-dbae765fb25a4114aac1c88b90e94178.r2.dev/v1/translate-en_fa-1_5.argosmodel  
- https://pub-dbae765fb25a4114aac1c88b90e94178.r2.dev/v1/translate-en_fr-1_0.argosmodel  
- https://pub-dbae765fb25a4114aac1c88b90e94178.r2.dev/v1/translate-en_es-1_0.argosmodel  
- https://pub-dbae765fb25a4114aac1c88b90e94178.r2.dev/v1/translate-en_zh-1_7.argosmodel  
- https://pub-dbae765fb25a4114aac1c88b90e94178.r2.dev/v1/translate-en_de-1_0.argosmodel  
- https://pub-dbae765fb25a4114aac1c88b90e94178.r2.dev/v1/translate-en_ru-1_7.argosmodel  
- https://pub-dbae765fb25a4114aac1c88b90e94178.r2.dev/v1/translate-en_ja-1_1.argosmodel  
  
links to all packages:  
- https://www.argosopentech.com/argospm/index/  
- https://drive.google.com/drive/folders/11wxM3Ze7NCgOk_tdtRjwet10DmtvFu3i

## after downloading models

do consider that file names could change according to there versioning, 
if you got diffrent version's from above either you need to change   
the `argos_setup.py` file or install them manually. 
you need to put the files inside the `argos_packages_offline`
directory like the following structure:   

argos_packages_offline/
├── en_ar.argosmodel
├── en_es.argosmodel
├── en_fr.argosmodel
├── translate-en_de-1_5.argosmodel
├── translate-en_fa-1_5.argosmodel
├── translate-en_ja-1_1.argosmodel
├── translate-en_ru-1_7.argosmodel
└── translate-en_zh-1_1.argosmodel

# Note
after installation the one of the whisper models should  
be downloaded(multiple models could exist in `./openai/` directory)  
in the following directory example:  
  
openai/  
├── whisper-base  
│   ├── added_tokens.json  
│   ├── config.json  
│   ├── flax_model.msgpack  
│   ├── generation_config.json  
│   ├── merges.txt  
│   ├── normalizer.json  
│   ├── preprocessor_config.json  
│   ├── pytorch_model.bin  
│   ├── README.md  
│   ├── special_tokens_map.json  
│   ├── tf_model.h5  
│   ├── tokenizer_config.json  
│   ├── tokenizer.json  
│   └── vocab.json  
└── whisper-small  
    ├── added_tokens.json  
    ├── config.json  
    ├── flax_model.msgpack  
    ├── generation_config.json  
    ├── merges.txt  
    ├── normalizer.json  
    ├── preprocessor_config.json  
    ├── pytorch_model.bin  
    ├── README.md  
    ├── special_tokens_map.json  
    ├── tf_model.h5  
    ├── tokenizer_config.json  
    ├── tokenizer.json  
    └── vocab.json  
 
`tiny` whisper model is the smallest pretrained model.    
you can download other ones and put them inside `./openai/`  
folder if you one to use another one, and also   
select the model in model_select function in functions.py  
and the put it in the line after `model_select` function as follow:
      
`
	#i.e if you downloaded the small model
	def model_select(model_name):
		.
		.
		.
	 	if(model_name == 'small'):
        		with open(log_file, "a") as log:
            		log.write("using small model\n")
        		return   pipeline("automatic-speech-recognition", model="openai/whisper-small")
`
  	`pipe = model_select(model_name='small')`  
i.e the small model link is https://huggingface.co/openai/whisper-small

