# Installation
1.run the command below:  
`pip install -r requirements.txt`  
for installing the requirements  

2.run the command below:  
`python3 argos_setup.py`   
for installing the offline argos_translate packages  
(note: either this or you can install the packages online)

# Note
after installation the one of the whisper models should  
be downloaded(multiple models could exist in `./openai/` directory)  
in the following directory example:  
`  
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
`  
`tiny` whisper model is the smallest pretrained model.    
you can download other ones and put them inside `./openai/`  
folder if you one to use another one and also   
( select the model in model_select function in functions.py  
  and the put it in the line after `model_select` function as follow:
      
	`def model_select(model_name):
		.
		.
		.
	 	if(model_name == 'small'):
        		with open(log_file, "a") as log:
            		log.write("using small model\n")
        		return   pipeline("automatic-speech-recognition", model="openai/whisper-small")
  	`
  	`pipe = model_select(model_name='small')`  
  if you downloaded the small model  
)  
i.e the small model link is https://huggingface.co/openai/whisper-small

