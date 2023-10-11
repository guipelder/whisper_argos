# Installation
1.run the command below:  
`pip install -r requirements.txt`  
for installing the requirements  

2.run the command below:  
`python3 argos_setup.py`   
for installing the offline argos_translate packages  
(note: either this or you can install the packages online)

# note  
only `base` whisper model been downloaded (smallest)  
you can download other ones and put them inside `./openai/`  
folder if you one to use another one and also   
(
    select the model in model_select function in functions.py  
    and the put it in the line after model_select function as follow:  
    `$ pipe = model_select(model_name='small')`  
    if you downloaded the small model  
)  
i.e the small model link is https://huggingface.co/openai/whisper-small

