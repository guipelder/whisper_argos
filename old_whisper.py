import webbrowser
from transformers import pipeline
import ffmpeg
import argostranslate.translate

import subprocess
from pathlib import Path

import auditok
import soundfile
import re
import torch
import datetime
import os

from flask import Flask, render_template, request
from flask_dropzone import Dropzone


#  extract the audio track from the video and save it as a `.wav` file.
# video = "./video.mkv"
# import subprocess
# from pathlib import Path

# audio_directory = './temp_audio/'
#TODO changin the extract_audio function to use internal ffmpeg-python
def extract_audio(input_file):
    Path(audio_directory).mkdir(parents=True, exist_ok=True)
    audio_file = audio_directory+'/temp.wav'
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
  audio_regions = auditok.split(audio_name,
    min_dur=0.1,       # minimum duration of a valid audio in seconds
    max_dur=8.0,       # maximum duration of an audio segment
    max_silence=7.99, # maximum duration of tolerated continuous silence within an event
    energy_threshold=20, # threshold of detection
    sampling_rate=16000
  )
  for i, r in enumerate(audio_regions):
    filename = r.save(audio_name[:-4]+f'_{r.meta.start:08.3f}-{r.meta.end:08.3f}.wav')



# Now we download  and setup the model weights of the pre-trained model from the huggingface hub using the `transformers` library.
# We download and load the [OpenAI Whisper Base](https://huggingface.co/openai/whisper-base) model using the convenience pipeline function in the library.
#TODO making a function to choose between small and base inference model
# from transformers import pipeline
# pipe = pipeline("automatic-speech-recognition", model="openai/whisper-base")

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



# import argostranslate.translate

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




#import argostranslate.translate

def get_subs_fa_en_optimized(audio_directory, output_file1 ,output_file2):
    segments = sorted([f for f in Path(audio_directory).glob(f'temp_*.wav')])
    line_count = 0
    from_code = "en"
    to_code = "fa"
    with open(output_file1, 'w', encoding="utf-8") as out_file1:
        with open(output_file2,'w',encoding="utf-8") as out_file2:
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
                out_file1.write(get_srt_line(translatedText, line_count, limits))
                out_file1.flush()
                out_file2.write(get_srt_line(inferred_text , line_count, limits))
                out_file2.flush()
                line_count += 1



def combine_subtitles(input_file,  subtitle_file, output_file):

    i = ffmpeg.input(input_file)
    # subtitile = ffmpeg.compile(subtitle_file)
    o = ffmpeg.output(i,output_file, **{'vf': f'subtitles={subtitle_file}'})
    o = ffmpeg.overwrite_output(o)
    ffmpeg.run(o)
    
    """
    (
   ...:     ffmpeg
   ...:     .input('video.mp4')
   ...:     .filter_('subtitles', 'video_en.srt')
   ...:     .output('output.mkv')
   ...:     .overwrite_output()
   ...:     .run()
   ...: )

    """
    # (
    #     ffmpeg
    #     .input(input_file)
    #     .output(output_file, **{'vf': f'subtitles={subtitle_file}'})
    #     .overwrite_output()
    #     .run()
    # )

   
    

    # command = ["ffmpeg", "-i", input_file, "-vf", f"subtitles={subtitle_file}", output_file]
    # subprocess.run(command)



# import ffmpeg
#TODO fix for mp3 file 
#Stream map '0:v' matches no streams. To ignore this, add a trailing '?' to the map.

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

def combine_subtitles_mkv_fa(input_file,  subtitle_file1 , subtitle_file2 , output_file):
    l1="en"
    t1="English"
    #sub2="subs/fr/fr_srt_sub.srt"
    l2="fa"
    t2="Farsi"
    output_file=output_file

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
    
    for i in segments:
        os.remove(i)

def downloads_cleaner():
    segments = [f for f in Path(download_directory).glob(f'*.*')]
    
    for i in segments:
        os.remove(i)

pipe = model_select(model_name='base')
audio_directory = './temp_audio/'
download_directory = './downloads/'
video = "not changed"
temp_str=""

#from flask import Flask, render_template, request
#from flask_dropzone import Dropzone
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'uploads'),
    # Flask-Dropzone config:
    DROPZONE_MAX_FILE_SIZE=4096,  # set max size limit to a large number, here is 1024 MB
    DROPZONE_TIMEOUT=20 * 60 * 1000 , # set upload timeout to a large number, here is 5 minutes
    DROPZONE_MAX_FILES=1,
    DROPZONE_ALLOWED_FILE_CUSTOM=True,
    DROPZONE_ALLOWED_FILE_TYPE='audio/* , video/*, .mp4 , .mkv , .mp3, .wav'
    

)

dropzone = Dropzone(app)


#global done value
from flask import jsonify
done = False
@app.route('/done',methods=['GET','POST'])
def done_check():
    dic = {"isdone":done}
    #TODO NOt necessary to use jsonify 
    return jsonify(dic)


from flask import send_file , send_from_directory
@app.route('/mkv_en') # this is a job for GET, not POST
def mkv_en():

    return send_from_directory(
        directory=download_directory,
        path=f"video_subbed_en.mkv",
        as_attachment=True)

@app.route('/mkv_en_encoded') # this is a job for GET, not POST
def mkv_en_encoded():

    return send_from_directory(
        directory=download_directory,
        path=f"video_en_hard_encoded.mkv",
        as_attachment=True)

@app.route('/mkv_en_fa') # this is a job for GET, not POST
def mkv_en_fa():

    return send_from_directory(
        directory=download_directory,
        path=f"video_subbed_en_fa.mkv",
        as_attachment=True)

@app.route('/srt_en') # this is a job for GET, not POST
def srt_en():

    return send_from_directory(
        directory=download_directory,
        path=f"video_en.srt",
        as_attachment=True)

@app.route('/srt_fa') # this is a job for GET, not POST
def srt_fa():

    return send_from_directory(
        directory=download_directory,
        path=f"video_fa.srt",
        as_attachment=True)



@app.route('/', methods=['POST', 'GET'])
def upload():
    
    global done 
    if request.method == 'POST':
        print(f"done ={done}")
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
        temp_str=str(f.filename)
        print(f"\n{temp_str}\n")
        video=f"./uploads/{temp_str}"
        print(f"\n./uploads/{temp_str}\n")
        print(f"\n{video}\n")
        
        print(os.getcwd())
        print(f"done ={done}")
        temp_cleaner()
        # downloads_cleaner()
        extract_audio(video)
        segment_audio(audio_directory+'/temp.wav')

        segments = [f for f in Path(audio_directory).glob(f'temp_*.wav')]
        
        get_subs_fa_en_optimized(audio_directory, f'{download_directory}video_fa.srt', f'{download_directory}video_en.srt')

        combine_subtitles(video, f"{download_directory}video_en.srt", f'{download_directory}video_en_hard_encoded.mkv')
        combine_subtitles_mkv(video, f"{download_directory}video_en.srt", f'{download_directory}video_subbed_en.mkv')
        combine_subtitles_mkv_fa(video,f"{download_directory}video_en.srt",f'{download_directory}video_fa.srt',f'{download_directory}video_subbed_en_fa.mkv')

        done = True
        
    # probably should work without sending value with render_template
    return render_template('index.html', Done=done)



if __name__ == '__main__':

    # import webbrowser   
    webbrowser.open("http://127.0.0.1:5000/")    
    app.run(debug = True)
    
    


# ======================================================================
# ======================================================================
# ======================================================================
# ======================================================================
# ======================================================================
# ======================================================================
# ======================================================================


# exit()  
#os.chdir("..")
#with open('./uploads/{temp_str}','r') as f:

# print(f"\n./uploads/{temp_str}\n")
# print(f"\n{video}\n")
# #video = f"./uploads/{temp_str}"
# #os.chdir("..")
# print(os.getcwd())
# audio_directory = './temp_audio/'

# temp_cleaner()
# extract_audio(video)
# segment_audio(audio_directory+'/temp.wav')

# segments = [f for f in Path(audio_directory).glob(f'temp_*.wav')]
# #pipe would be used to extract the infered text
# pipe = model_select(model_name='base')
# #get_subs(audio_directory, './video_en.srt')
# #get_subs_fa(audio_directory, './video_fa.srt')
# get_subs_fa_en_optimized(audio_directory, './video_fa.srt', './video_en.srt')
# #temp_cleaner()
# combine_subtitles_mkv(video, "./video_en.srt", './video_subbed_en.mkv')
# combine_subtitles_mkv_fa(video,"./video_en.srt",'./video_fa.srt','./video_subbed_en_fa.mkv')

















"""
#Define vars
video="input.mp4"
sub1="subs/en/en_srt_sub.srt"
l1="en"
t1="English"
sub2="subs/fr/fr_srt_sub.srt"
l2="fr"
t2="French"
output_file="output.mkv"

#Define input values
input_ffmpeg = ffmpeg.input(video)
input_ffmpeg_sub1 = ffmpeg.input(sub1)
input_ffmpeg_sub2 = ffmpeg.input(sub2)

#Define output file
input_video = input_ffmpeg['v']
input_audio = input_ffmpeg['a']
input_subtitles1 = input_ffmpeg_sub1['s']
input_subtitles2 = input_ffmpeg_sub['s']
output_ffmpeg = ffmpeg.output(
    input_video, input_audio, input_subtitles1, input_subtitles2, output_file,
    vcodec='copy', acodec='copy', 
    **{'metadata:s:s:0': "language="+l1, 'metadata:s:s:0': "title="+t1, 'metadata:s:s:1': "language="+l2, 'metadata:s:s:1': "title="+t2 }
)

# If the destination file already exists, overwrite it.
output_ffmpeg = ffmpeg.overwrite_output(output_ffmpeg)

# Print the equivalent ffmpeg command we could run to perform the same action as above.
print(ffmpeg.compile(output_ffmpeg))

# Do it! transcode!
ffmpeg.run(output_ffmpeg)
"""



"""
import argostranslate.package
import argostranslate.translate

from_code = "en"
to_code = "es"

# Download and install Argos Translate package
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(
    filter(
        lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
    )
)
argostranslate.package.install_from_path(package_to_install.download())

# Translate
translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
print(translatedText)
# '¡Hola Mundo!'
"""


