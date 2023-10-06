from transformers import pipeline
import ffmpeg
import argostranslate.translate


import gc
import subprocess
from pathlib import Path
#from IPython.display import Audio, display
import auditok
import soundfile
import re
import torch
import datetime
import os
# from testwhisper import log_sender

from flask import Flask, render_template, request
from flask_dropzone import Dropzone

audio_directory = './temp_audio/'
download_directory = './downloads/'
upload_directory = './uploads/'

video = "not changed"
log_file = "log.txt"
with open(log_file, "w") as log:
        log.write("\n")
with open(log_file, "a") as log:
        log.write("inside functions\n")
global temp_str
temp_str  =""

#  extract the audio track from the video and save it as a `.wav` file.

# video = "./video.mkv"
# import subprocess
# from pathlib import Path

# audio_directory = './temp_audio/'
#TODO changin the extract_audio function to use internal ffmpeg-python
def extract_audio(input_file):
    Path(audio_directory).mkdir(parents=True, exist_ok=True)
    audio_file = audio_directory+'/temp.wav'
    with open(log_file, "a") as log:
        log.writelines("extracting audio\n")
#   command = ["ffmpeg", "-i", input_file, "-ac", "1", "-ar", "16000","-vn", "-f", "wav", audio_file]
#   subprocess.run(command)
    stream=ffmpeg.input(input_file)
    ffmpeg.output(stream, audio_file, ar=16000,ac=1, f='wav').run()




#useing the `auditok` library to segement the audio based on the silences in the video.
#This is useful for subtitling as we then have splits by the segments for each subtitle caption to be shown. 
#We also ensure that the max duration of each audio segment is not too long (less than 8s),
#so that the subtitle for each segment is readable.
# We `display` the first segement as an audio player in the notebook to listen.

# import auditok
def segment_audio(audio_name):
  # TODO problem with creating subtitle when using my settings
  audio_regions = auditok.split(audio_name,
    # min_dur=0.1,       # minimum duration of a valid audio in seconds
    # max_dur=8,       # maximum duration of an audio segment
    # max_silence=7.99, # maximum duration of tolerated continuous silence within an event
    # energy_threshold=35, # threshold of detection
    # sampling_rate=16000
    # min_dur=0.1,       # minimum duration of a valid audio in seconds
    # max_dur=8,       # maximum duration of an audio segment
    # max_silence=7.2, # maximum duration of tolerated continuous silence within an event
    # energy_threshold=53, # threshold of detection
    # sampling_rate=16000
    min_dur=0.1,       # minimum duration of a valid audio in seconds
    max_dur=7,       # maximum duration of an audio segment
    max_silence=6.9, # maximum duration of tolerated continuous silence within an event
    energy_threshold=30, # threshold of detection
    sampling_rate=16000
  )
  with open(log_file, "a") as log:
        log.writelines("segmentainon of audio\n")

  for i, r in enumerate(audio_regions):
    filename = r.save(audio_name[:-4]+f'_{r.meta.start:08.3f}-{r.meta.end:08.3f}.wav')
    with open(log_file, "a") as log:
        log.writelines(f"a-> {r.meta.start:08.3f} b-> {r.meta.end:08.3f}\n")




# Now we download  and setup the model weights of the pre-trained model from the huggingface hub using the `transformers` library.
# 
# We download and load the [OpenAI Whisper Base](https://huggingface.co/openai/whisper-base) model using the convenience pipeline function in the library.

#TODO making a function to choose between small and base inference model

# from transformers import pipeline

# pipe = pipeline("automatic-speech-recognition", model="openai/whisper-base")

def model_select(model_name):
    """
    if you want to add your own openai model from hugginface 
    you need to make sure of the name of folder and add it in another else(elif) 
    statment
    """
    if(model_name == 'small'):
        with open(log_file, "a") as log:
            log.write("using small model\n")
        return   pipeline("automatic-speech-recognition", model="openai/whisper-small")
    elif(model_name=='base'):
        with open(log_file, "a") as log:
            log.write("using base model\n")
        return   pipeline("automatic-speech-recognition", model="openai/whisper-base")


# base model is the SMALL one in the modeks
pipe = model_select(model_name='base')

# * `clean_text` - This is just a simple post-processing function to clean the output text from the ASR model with some simple regex.
# * `get_srt_line` - This function helps return a `.srt` format set of lines from an inferred text segment. This will include the start and ending time so the video player knows when to start and end the showing of the subtitle.
# * `get_subs` - Our main function. This function will run each of the audio segment through the tokenizer and ASR model and save the inferred text output as a line in the subtitle file. The `output_file` is the `.srt` file of the transcribed audio. During the process, we also print out the inferred text for each segment. Here you can see it is pretty accurate.
# 

# import soundfile
# import re
# import torch
# import datetime

def clean_text(text):
  clean_text = re.sub(r'  ', ' ', text)
  clean_text = re.sub(r'\bi\s', 'I ', clean_text)
  clean_text = re.sub(r'\si$', ' I', clean_text)
  clean_text = re.sub(r'i\'', 'I\'', clean_text)
  return clean_text



def get_srt_line(inferred_text, line_count, limits):
  """
  sample srt line:
    0 
    00:00:00,05 --> 00:00:07,05
    Igor, hat Sie den Körper bekommen? Ja, Master. Sie wissen, was zu tun ist.
  """
  with open(log_file, "a") as log:
    log.writelines("creating the srt lines\n")
  sep = ','   
  #getting d with the values like 0:00:00.050000   
  d = str(datetime.timedelta(seconds=float(limits[0])))

  with open(log_file, "a") as log:
        log.writelines(f"limits[0]-> {limits[0]}\n")

        log.writelines(f"limits -> {d}\n")
        #i.e. limits -> 0:00:00.300000

  
  try:
      from_dur = '0' + str(d.split(".")[0]) + sep + str(d.split(".")[-1][:2])
      # --->>>    0    0:00:00                 ,           05
      #00:00:00,05
  except:
      from_dur = '0' + str(d) + sep + '00'
      
  d = str(datetime.timedelta(seconds=float(limits[1])))
  try:
      to_dur = '0' + str(d.split(".")[0]) + sep + str(d.split(".")[-1][:2])
  except:
      to_dur = '0' + str(d) + sep + '00'
  return f'{str(line_count)}\n{from_dur} --> {to_dur}\n{inferred_text}\n\n'

def get_subs(audio_directory, output_file):
  segments = sorted([f for f in Path(audio_directory).glob(f'temp_*.wav')])
  line_count = 0
  global temp_str 
  with open(log_file, "a") as log:
        log.write("getting english subs \n")
  with open(output_file, 'w', encoding="utf-8") as out_file:
    
    for audio_file in segments:
      # Run OpenAI Whisper inference on each segemented audio file.
      speech, rate = soundfile.read(audio_file) 
      output_json = pipe(speech)
      inferred_text = output_json['text']

      if len(inferred_text) > 0:
        inferred_text = clean_text(inferred_text)
        with open(log_file, "a") as log:
            log.write(f"{inferred_text} \n")
        # log_sender(f"{inferred_text} {line_count}")
        print(inferred_text)
      else:
        inferred_text = ''

      limits = audio_file.name[:-4].split("_")[-1].split("-")
      limits = [float(limit) for limit in limits]
      with open(log_file, "a") as log:
        log.write(f"{limits} \n")
      out_file.write(get_srt_line(inferred_text, line_count, limits))
      out_file.flush()
      line_count += 1
      


def translate_srt_fa( input_file ,output_file):
            # there are 4 line is srt file and we only need to translate the third line
            with open(log_file, "a") as log:
                log.write(f"translating from english to  farsi subs ... \n")
            line_count = 1
            from_code = "en"
            to_code = "fa"
            translatedText = ''
            with open(input_file, 'r', encoding="utf-8") as in_file:
                with open(output_file,'w',encoding="utf-8") as out_file:

                    t = argostranslate
                    temp  = in_file.readlines()
                    temp_string = ''
                    i = 1
                    for s in temp:
                        if i % 4 == 3:
                            temp_string += s
                        i += 1
                    print(temp_string)
                    half_translate = t.translate.translate(temp_string, from_code, to_code)

                    del t
                    n = gc.collect()
                    print("Number of unreachable objects collected by GC:", n)
         
              
                    half_list = half_translate.split('\n')
                    # print(in_file.read())
                    for line in temp:
                        print(f"line is: {line}")
                        if ((line_count % 4) == 0 or (line_count % 4) == 1 or (line_count % 4) == 2):
                            translatedText = line
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()


#TODO trying to translate from srt_en directly
def translate_srt_fr( input_file ,output_file):
            with open(log_file, "a") as log:
                log.write(f"translating from english to  french subs ... \n")
            line_count = 1
            from_code = "en"
            to_code = "fr"
            translatedText = ''
            with open(input_file, 'r', encoding="utf-8") as in_file:
                with open(output_file,'w',encoding="utf-8") as out_file:

                    t = argostranslate
                    temp  = in_file.readlines()
                    temp_string = ''
                    i = 1
                    for s in temp:
                        if i % 4 == 3:
                            temp_string += s
                        i += 1
                    print(temp_string)
                    half_translate = t.translate.translate(temp_string, from_code, to_code)

                    del t
                    n = gc.collect()
                    print("Number of unreachable objects collected by GC:", n)
         
              
                    half_list = half_translate.split('\n')
                    
                    # temp is the filelines()
                    for line in temp:
                        print(f"line is: {line}")
                        if ((line_count % 4) == 0 or (line_count % 4) == 1 or (line_count % 4) == 2):
                            translatedText = line
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()

#TODO trying to translate from srt_en directly
def translate_srt_es( input_file ,output_file):
            with open(log_file, "a") as log:
                log.write(f"translating from english to  spanish subs ... \n")
            line_count = 1
            from_code = "en"
            to_code = "es"
            translatedText = ''
            with open(input_file, 'r', encoding="utf-8") as in_file:
                with open(output_file,'w',encoding="utf-8") as out_file:

                    t = argostranslate
                    temp  = in_file.readlines()
                    temp_string = ''
                    i = 1
                    for s in temp:
                        if i % 4 == 3:
                            temp_string += s
                        i += 1
                    print(temp_string)
                    half_translate = t.translate.translate(temp_string, from_code, to_code)

                    del t
                    n = gc.collect()
                    print("Number of unreachable objects collected by GC:", n)
         
              
                    half_list = half_translate.split('\n')
                    # print(in_file.read())
                    for line in temp:
                        print(f"line is: {line}")
                        if ((line_count % 4) == 0 or (line_count % 4) == 1 or (line_count % 4) == 2):
                            translatedText = line
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()

#TODO trying to translate from srt_en directly
def translate_srt_de( input_file ,output_file):
            with open(log_file, "a") as log:
                log.write(f"translating from english to  german subs ... \n")
            line_count = 1
            from_code = "en"
            to_code = "de"
            translatedText = ''
            with open(input_file, 'r', encoding="utf-8") as in_file:
                with open(output_file,'w',encoding="utf-8") as out_file:

                    t = argostranslate
                    temp  = in_file.readlines()
                    temp_string = ''
                    i = 1
                    for s in temp:
                        if i % 4 == 3:
                            temp_string += s
                        i += 1
                    print(temp_string)
                    half_translate = t.translate.translate(temp_string, from_code, to_code)

                    del t
                    n = gc.collect()
                    print("Number of unreachable objects collected by GC:", n)
         
              
                    half_list = half_translate.split('\n')
                    # print(in_file.read())
                    for line in temp:
                        print(f"line is: {line}")
                        if ((line_count % 4) == 0 or (line_count % 4) == 1 or (line_count % 4) == 2):
                            translatedText = line
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()


#TODO trying to translate from srt_en directly
def translate_srt_zh( input_file ,output_file):
            with open(log_file, "a") as log:
                log.write(f"translating from english to  chinese subs ... \n")
            line_count = 1
            from_code = "en"
            to_code = "zh"
            translatedText = ''
            with open(input_file, 'r', encoding="utf-8") as in_file:
                with open(output_file,'w',encoding="utf-8") as out_file:

                    t = argostranslate
                    temp  = in_file.readlines()
                    temp_string = ''
                    i = 1
                    for s in temp:
                        if i % 4 == 3:
                            temp_string += s
                        i += 1
                    print(temp_string)
                    half_translate = t.translate.translate(temp_string, from_code, to_code)

                    del t
                    n = gc.collect()
                    print("Number of unreachable objects collected by GC:", n)
         
              
                    half_list = half_translate.split('\n')
                    # print(in_file.read())
                    for line in temp:
                        print(f"line is: {line}")
                        if ((line_count % 4) == 0 or (line_count % 4) == 1 or (line_count % 4) == 2):
                            translatedText = line
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()

#TODO trying to translate from srt_en directly
def translate_srt_ru( input_file ,output_file):
            with open(log_file, "a") as log:
                log.write(f"translating from english to  russian subs ... \n")
            line_count = 1
            from_code = "en"
            to_code = "ru"
            translatedText = ''
            with open(input_file, 'r', encoding="utf-8") as in_file:
                with open(output_file,'w',encoding="utf-8") as out_file:

                    t = argostranslate
                    temp  = in_file.readlines()
                    temp_string = ''
                    i = 1
                    for s in temp:
                        if i % 4 == 3:
                            temp_string += s
                        i += 1
                    print(temp_string)
                    half_translate = t.translate.translate(temp_string, from_code, to_code)

                    del t
                    n = gc.collect()
                    print("Number of unreachable objects collected by GC:", n)
         
              
                    half_list = half_translate.split('\n')
                    # print(in_file.read())
                    for line in temp:
                        print(f"line is: {line}")
                        if ((line_count % 4) == 0 or (line_count % 4) == 1 or (line_count % 4) == 2):
                            translatedText = line
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()

#TODO trying to translate from srt_en directly
def translate_srt_ja( input_file ,output_file):
            with open(log_file, "a") as log:
                log.write(f"translating from english to  japenease subs ... \n")
            line_count = 1
            from_code = "en"
            to_code = "ja"
            translatedText = ''
            with open(input_file, 'r', encoding="utf-8") as in_file:
                with open(output_file,'w',encoding="utf-8") as out_file:

                    t = argostranslate
                    temp  = in_file.readlines()
                    temp_string = ''
                    i = 1
                    for s in temp:
                        if i % 4 == 3:
                            temp_string += s
                        i += 1
                    print(temp_string)
                    half_translate = t.translate.translate(temp_string, from_code, to_code)

                    del t
                    n = gc.collect()
                    print("Number of unreachable objects collected by GC:", n)
         
              
                    half_list = half_translate.split('\n')
                    # print(in_file.read())
                    for line in temp:
                        print(f"line is: {line}")
                        if ((line_count % 4) == 0 or (line_count % 4) == 1 or (line_count % 4) == 2):
                            translatedText = line
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                            with open(log_file, "a") as log:
                                log.write(f"{translatedText} \n")

                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()

def combine_subtitles_mkv_all(input_file,  subtitle_file1 ,
                              subtitle_file2, subtitle_file3,
                              subtitle_file4, subtitle_file5,
                              subtitle_file6, subtitle_file7 ,
                              subtitle_file8, output_file):
    l1="en"
    t1="English"

    l2="fa"
    t2="Farsi"
    
    l3 = "fr"
    t3 = "French"

    l4 = "de"
    t4 = "German"
    
    l5= "es"
    t5= "Spanish"
    
    l6= "ru"
    t6= "Russian"
    
    l7= "zh"
    t7= "Chinease"

    l8= "ja"
    t8= "japenese"


    output_file=output_file

    #Define input values
    input_ffmpeg = ffmpeg.input(input_file)
    input_ffmpeg_sub1 = ffmpeg.input(subtitle_file1)
    input_ffmpeg_sub2 = ffmpeg.input(subtitle_file2)
    input_ffmpeg_sub3 = ffmpeg.input(subtitle_file3)
    input_ffmpeg_sub4 = ffmpeg.input(subtitle_file4)
    input_ffmpeg_sub5 = ffmpeg.input(subtitle_file5)
    input_ffmpeg_sub6 = ffmpeg.input(subtitle_file6)

    input_ffmpeg_sub7 = ffmpeg.input(subtitle_file7)
    input_ffmpeg_sub8 = ffmpeg.input(subtitle_file8)




    #Define output file
    input_video = input_ffmpeg['v']
    input_audio = input_ffmpeg['a']
    input_subtitles1 = input_ffmpeg_sub1['s']
    input_subtitles2 = input_ffmpeg_sub2['s']
    input_subtitles3 = input_ffmpeg_sub3['s']
    input_subtitles4 = input_ffmpeg_sub4['s']
    input_subtitles5 = input_ffmpeg_sub5['s']
    input_subtitles6 = input_ffmpeg_sub6['s']
    input_subtitles7 = input_ffmpeg_sub7['s']
    input_subtitles8 = input_ffmpeg_sub8['s']



    output_ffmpeg = ffmpeg.output(

        input_video, input_audio, input_subtitles1,input_subtitles2, 
        input_subtitles3,input_subtitles4, 
        input_subtitles5,input_subtitles6,
        input_subtitles7,input_subtitles8, 
        output_file,
        vcodec='copy', acodec='copy', 
        **{'metadata:s:s:0': "language="+l1,
           'metadata:s:s:0': "title="+t1,
           'metadata:s:s:1': "language="+l2,
           'metadata:s:s:1': "title="+t2,
           'metadata:s:s:2': "language="+l3,
           'metadata:s:s:2': "title="+t3,
           'metadata:s:s:3': "language="+l4,
           'metadata:s:s:3': "title="+t4,
           'metadata:s:s:4': "language="+l5,
           'metadata:s:s:4': "title="+t5,
           'metadata:s:s:5': "language="+l6,
           'metadata:s:s:5': "title="+t6,
           'metadata:s:s:6': "language="+l7,
           'metadata:s:s:6': "title="+t7,
           'metadata:s:s:7': "language="+l8,
           'metadata:s:s:7': "title="+t8
          }
    )

    # If the destination file already exists, overwrite it.
    output_ffmpeg = ffmpeg.overwrite_output(output_ffmpeg)

    # Print the equivalent ffmpeg command we could run to perform the same action as above.
    print(ffmpeg.compile(output_ffmpeg))
    with open(log_file, "a") as log:
        log.write(f"combining all subtitles \n")


    # Do it! transcode!
    ffmpeg.run(output_ffmpeg)




# import argostranslate.translate
# not used in project (replaced)
def get_subs_fa(audio_directory, output_file):
  segments = sorted([f for f in Path(audio_directory).glob(f'temp_*.wav')])
  line_count = 0
  from_code = "en"
  to_code = "fa"
  with open(output_file, 'w', encoding="utf-8") as out_file:
    for audio_file in segments:
      # Run OpenAI Whisper inference on each segemented audio file.
      speech, rate = soundfile.read(audio_file) 
      output_json = pipe(speech)
      inferred_text = output_json['text']

      if len(inferred_text) > 0:
        inferred_text = clean_text(inferred_text)
        print(inferred_text)
        translatedText = argostranslate.translate.translate(inferred_text, from_code, to_code)
        print(translatedText)
      else:
        inferred_text = ''
        translatedText= ''

      limits = audio_file.name[:-4].split("_")[-1].split("-")
      limits = [float(limit) for limit in limits]
      out_file.write(get_srt_line(translatedText, line_count, limits))
      out_file.flush()
      line_count += 1











# hardencode the subtitle to the video
def combine_subtitles(input_file,  subtitle_file, output_file):
  command = ["ffmpeg", "-i", input_file, "-vf", f"subtitles={subtitle_file}", output_file]
  with open(log_file, "a") as log:
        log.write(f"creating hardcoded english-subbed mkv file \n")

  subprocess.run(command)



# import ffmpeg
#TODO fix for mp3 file 
#Stream map '0:v' matches no streams. To ignore this, add a trailing '?' to the map.

def combine_subtitles_mkv(input_file,  subtitle_file, output_file):
    l1="en"
    t1="English"
    output_file=output_file
    with open(log_file, "a") as log:
        log.write(f"creating mkv file with english sub \n")


    #Define input values
    input_ffmpeg = ffmpeg.input(input_file)
    input_ffmpeg_sub1 = ffmpeg.input(subtitle_file)
    #input_ffmpeg_sub2 = ffmpeg.input(sub2)

    #Define output file
    input_video = input_ffmpeg['v']
    input_audio = input_ffmpeg['a']
    input_subtitles1 = input_ffmpeg_sub1['s']
    #input_subtitles2 = input_ffmpeg_sub['s']
    output_ffmpeg = ffmpeg.output(
        input_video, input_audio, input_subtitles1,  output_file,
        vcodec='copy', acodec='copy', 
        **{'metadata:s:s:0': "language="+l1, 'metadata:s:s:0': "title="+t1 }
    )

    # If the destination file already exists, overwrite it.
    output_ffmpeg = ffmpeg.overwrite_output(output_ffmpeg)

    # Print the equivalent ffmpeg command we could run to perform the same action as above.
    print(ffmpeg.compile(output_ffmpeg))

    # Do it! transcode!
    ffmpeg.run(output_ffmpeg)



def combine_subtitles_mkv_fa(input_file,  subtitle_file1 , subtitle_file2 , output_file):
    l1="en"
    t1="English"
    #sub2="subs/fr/fr_srt_sub.srt"
    l2="fa"
    t2="Farsi"
    output_file=output_file
    with open(log_file, "a") as log:
        log.write(f"creating mkv file with farsi sub \n")

    #Define input values
    input_ffmpeg = ffmpeg.input(input_file)
    input_ffmpeg_sub1 = ffmpeg.input(subtitle_file1)
    input_ffmpeg_sub2 = ffmpeg.input(subtitle_file2)

    #Define output file
    input_video = input_ffmpeg['v']
    input_audio = input_ffmpeg['a']
    input_subtitles1 = input_ffmpeg_sub1['s']
    input_subtitles2 = input_ffmpeg_sub2['s']
    output_ffmpeg = ffmpeg.output(
        input_video, input_audio, input_subtitles1,input_subtitles2,  output_file,
        vcodec='copy', acodec='copy', 
        **{'metadata:s:s:0': "language="+l1, 'metadata:s:s:0': "title="+t1,'metadata:s:s:1': "language="+l2, 'metadata:s:s:1': "title="+t2  }
    )

    # If the destination file already exists, overwrite it.
    output_ffmpeg = ffmpeg.overwrite_output(output_ffmpeg)

    # Print the equivalent ffmpeg command we could run to perform the same action as above.
    print(ffmpeg.compile(output_ffmpeg))

    # Do it! transcode!
    ffmpeg.run(output_ffmpeg)



#a helper function for deletion of temp audios every time
# import os 
def temp_cleaner():
    segments = [f for f in Path(audio_directory).glob(f'temp*.wav')]
    with open(log_file, "a") as log:
        log.write(f"cleaning temp \n")

    
    for i in segments:
        os.remove(i)


def downloads_cleaner():
    segments = [f for f in Path(download_directory).glob(f'*.*')]
    with open(log_file, "a") as log:
        log.write(f"cleaning download files\n")

    
    for i in segments:
        os.remove(i)
def uploads_cleaner():
    segments = [f for f in Path(upload_directory).glob(f'*.*')]
    with open(log_file, "a") as log:
        log.write(f"cleaning uploaded files\n")

    for i in segments:
        os.remove(i)




