
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

from flask import Flask, render_template, request
from flask_dropzone import Dropzone





# # Using the Model (Running Inference)

# First we extract the audio track from the video and save it as a `.wav` file.
# 
# We use the `ffmpeg` application to do this extraction. On colab, `ffmpeg` is already pre-installed in the environment. So we just use Python's `subprocess` to call ffmpeg to extract the audio.
# 
# We then `display` an audio player in the notebook to listen to the extracted audio.



# video = "./video.mkv"
# import subprocess
# from pathlib import Path

# audio_directory = './temp_audio/'
def extract_audio(input_file):
  Path(audio_directory).mkdir(parents=True, exist_ok=True)
  audio_file = audio_directory+'/temp.wav'
  command = ["ffmpeg", "-i", input_file, "-ac", "1", "-ar", "16000","-vn", "-f", "wav", audio_file]
  subprocess.run(command)



# Next we use the `auditok` library to segement the audio based on the silences in the video. This is useful for subtitling as we then have splits by the segments for each subtitle caption to be shown. We also ensure that the max duration of each audio segment is not too long (less than 8s), so that the subtitle for each segment is readable.
# 
# We `display` the first segement as an audio player in the notebook to listen.
# import auditok
def segment_audio(audio_name):
    audio_regions = auditok.split(audio_name,
    #min_dur=0.1,       # minimum duration of a valid audio in seconds
    #max_dur=8,       # maximum duration of an audio segment
    #max_silence=7.99, # maximum duration of tolerated continuous silence within an event
    #energy_threshold=20, # threshold of detection
    #sampling_rate=16000

    #min_dur=1,       # minimum duration of a valid audio in seconds

    #max_dur=8,       # maximum duration of an audio segment
    #max_silence=0.8, # maximum duration of tolerated continuous silence within an event
    #energy_threshold=55, # threshold of detection
    #sampling_rate=16000
    min_dur=0.1,       # minimum duration of a valid audio in seconds
    max_dur=7,       # maximum duration of an audio segment
    max_silence=6.9, # maximum duration of tolerated continuous silence within an event
    energy_threshold=30, # threshold of detection
    sampling_rate=16000
  )
    for i, r in enumerate(audio_regions):
        filename = r.save(audio_name[:-4]+f'_{r.meta.start:08.3f}-{r.meta.end:08.3f}.wav')



# Now we download  and setup the model weights of the pre-trained model from the huggingface hub using the `transformers` library.
# 
# We download and load the [OpenAI Whisper Base](https://huggingface.co/openai/whisper-base) model using the convenience pipeline function in the library.

# making a function to choose between small and base inference model  or other models

# from transformers import pipeline


def model_select(model_name):
    if(model_name == 'small'):
        return   pipeline("automatic-speech-recognition", model="openai/whisper-small")
    elif(model_name=='base'):
        return   pipeline("automatic-speech-recognition", model="openai/whisper-base")


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
  sep = ','   
  d = str(datetime.timedelta(seconds=float(limits[0])))
  try:
      from_dur = '0' + str(d.split(".")[0]) + sep + str(d.split(".")[-1][:2])
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

  with open(output_file, 'w', encoding="utf-8") as out_file:
    for audio_file in segments:
      # Run OpenAI Whisper inference on each segemented audio file.
      speech, rate = soundfile.read(audio_file) 
      output_json = pipe(speech)
      inferred_text = output_json['text']

      if len(inferred_text) > 0:
        inferred_text = clean_text(inferred_text)
        print(inferred_text)
      else:
        inferred_text = ''

      limits = audio_file.name[:-4].split("_")[-1].split("-")
      limits = [float(limit) for limit in limits]
      out_file.write(get_srt_line(inferred_text, line_count, limits))
      out_file.flush()
      line_count += 1



def translate_srt_fa( input_file ,output_file):
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
                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()


#TODO trying to translate from srt_en directly
def translate_srt_fr( input_file ,output_file):
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
                    # print(in_file.read())
                    for line in temp:
                        print(f"line is: {line}")
                        if ((line_count % 4) == 0 or (line_count % 4) == 1 or (line_count % 4) == 2):
                            translatedText = line
                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()

def translate_srt_es( input_file ,output_file):
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
                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()

def translate_srt_de( input_file ,output_file):
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
                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()


def translate_srt_zh( input_file ,output_file):
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
                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()

def translate_srt_ru( input_file ,output_file):
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
                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()

def translate_srt_ja( input_file ,output_file):
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
                        elif (line_count % 4 == 3):
                            inferred_text = line
                            print(inferred_text)
                            translatedText = half_list[int((line_count)/4 ) ]
                            print(f"traslated text from english {translatedText}")
                        else:
                            translatedText = ''
                        line_count += 1
                        
                        out_file.write(translatedText)
                        out_file.flush()



# Next we want to use the `ffmpeg` application again to render the subtitle text on the video itself so we can preview it. We use the `subprocess` library again to do so.
#ENCODER



def combine_subtitles(input_file,  subtitle_file, output_file):
  command = ["ffmpeg", "-i", input_file, "-vf", f"subtitles={subtitle_file}", output_file]
  subprocess.run(command)



# import ffmpeg
def combine_subtitles_mkv(input_file,  subtitle_file, output_file):
    l1="en"
    t1="English"
    output_file=output_file

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

    # Do it! transcode!
    ffmpeg.run(output_ffmpeg)



#a helper function for deletion of temp audios every time
# import os 
def temp_cleaner():
    segments = [f for f in Path(audio_directory).glob(f'temp*.wav')]
    
    for i in segments:
        os.remove(i)

pipe = model_select(model_name='base')
audio_directory = './temp_audio'
video = "not changed"
temp_str=""


video = f"./video.mkv"
# video = "./video.mp4"
print(os.getcwd())

temp_cleaner()
extract_audio(video)
segment_audio(audio_directory+'/temp.wav')

segments = [f for f in Path(audio_directory).glob(f'temp_*.wav')]
#pipe would be used to extract the infered text
#pipe = model_select(model_name='base')
get_subs(audio_directory, './video_en.srt')
translate_srt_fa( './video_en.srt', './video_fa.srt')
translate_srt_fr( './video_en.srt', './video_fr.srt')
translate_srt_es( './video_en.srt', './video_es.srt')
translate_srt_de( './video_en.srt', './video_de.srt')
translate_srt_ru( './video_en.srt', './video_ru.srt')
translate_srt_zh( './video_en.srt', './video_zh.srt')
translate_srt_ja( './video_en.srt', './video_ja.srt')
temp_cleaner()
combine_subtitles_mkv(video, "./video_en.srt", './video_subbed_en.mkv')
combine_subtitles_mkv_all(video,"./video_en.srt",'./video_fa.srt',
                          "./video_fr.srt",'./video_de.srt',
                          "./video_es.srt",'./video_ru.srt',
                          "./video_zh.srt",'./video_ja.srt',
                          './video_subbed_en_fa.mkv')




