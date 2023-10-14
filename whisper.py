from flask import send_file, send_from_directory
from flask import jsonify
from functions import *

import asyncio
import threading

import os
from flask import Flask, render_template, request
from flask_dropzone import Dropzone
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = False
log_file = 'log.txt'



download_directory = './downloads/'
audio_directory = './temp_audio/'
video = "not changed"
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'uploads'),
    # Flask-Dropzone config:
    DROPZONE_MAX_FILE_SIZE=4096,  # set max size limit to a large number, here is 1024 MB
    # set upload timeout to a large number, here is 5 minutes
    DROPZONE_TIMEOUT=20 * 60 * 1000,
    
    DROPZONE_MAX_FILES=1,
    DROPZONE_ALLOWED_FILE_CUSTOM=True,
    DROPZONE_ALLOWED_FILE_TYPE='audio/* , video/*, .mp4 , .mkv , .mp3, .wav'

)

dropzone = Dropzone(app)
socketio = SocketIO(app,cors_allowed_origins="*", async_mode='threading')
done = False

def read_log():
    with open("log.txt", "r") as f:
        file_lines = f.readlines()
    return file_lines



initial = read_log()


@socketio.on('connect')
def connect():
    print('Client connected')
    with open(log_file, "a") as log:
        log.write("clinet connected\n")


@app.route('/done', methods=['GET', 'POST'])
def done_check():
    # with open(log_file, "w") as log:
    #     log.write("\n")
    dic = {"isdone": done}
    # TODO NOt necessary to use jsonify
    with open(log_file, "a") as log:
        log.write("the operation is done and files are ready\n")
    return jsonify(dic)


@app.route('/mkv_en')  # this is a job for GET, not POST
def mkv_en():
    # with open(log_file, "a") as log:
    #     log.write(f"preparing mkv_en for download  \n")


    return send_from_directory(
        directory=download_directory,
        path=f"video_subbed_en.mkv",
        as_attachment=True)


@app.route('/mkv_en_encoded')  # this is a job for GET, not POST
def mkv_en_encoded():

    return send_from_directory(
        directory=download_directory,
        path=f"video_en_hard_encoded.mkv",
        as_attachment=True)


@app.route('/mkv_en_fa')  # this is a job for GET, not POST
def mkv_en_fa():

    return send_from_directory(
        directory=download_directory,
        path=f"video_subbed_en_fa.mkv",
        as_attachment=True)

@app.route('/mkv_all')  # this is a job for GET, not POST
def mkv_all():

    return send_from_directory(
        directory=download_directory,
        path=f"video_all_subs.mkv",
        as_attachment=True)



@app.route('/srt_en')  # this is a job for GET, not POST
def srt_en():

    return send_from_directory(
        directory=download_directory,
        path=f"video_en.srt",
        as_attachment=True)


@app.route('/srt_fa')  # this is a job for GET, not POST
def srt_fa():

    return send_from_directory(
        directory=download_directory,
        path=f"video_fa.srt",
        as_attachment=True)

@app.route('/srt_fr')  # this is a job for GET, not POST
def srt_fr():

    return send_from_directory(
        directory=download_directory,
        path=f"video_fr.srt",
        as_attachment=True)
        
@app.route('/srt_es')  # this is a job for GET, not POST
def srt_es():

    return send_from_directory(
        directory=download_directory,
        path=f"video_es.srt",
        as_attachment=True)

        
@app.route('/srt_de')  # this is a job for GET, not POST
def srt_de():

    return send_from_directory(
        directory=download_directory,
        path=f"video_de.srt",
        as_attachment=True)

        
@app.route('/srt_ru')  # this is a job for GET, not POST
def srt_ru():

    return send_from_directory(
        directory=download_directory,
        path=f"video_ru.srt",
        as_attachment=True)

        
@app.route('/srt_ja')  # this is a job for GET, not POST
def srt_ja():

    return send_from_directory(
        directory=download_directory,
        path=f"video_ja.srt",
        as_attachment=True)
                
@app.route('/srt_zh')  # this is a job for GET, not POST
def srt_zh():

    return send_from_directory(
        directory=download_directory,
        path=f"video_zh.srt",
        as_attachment=True)



@app.route('/', methods=['POST', 'GET'])
def upload():

    global done 
    if request.method == 'POST':

        

            
        isdone_sender(done)
        print(f"done ={done}")
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
        file_name_str=str(f.filename)
        print(f"\n{file_name_str}\n")
        video=f"./uploads/{file_name_str}"
        print(f"\n./uploads/{file_name_str}\n")
        print(f"\n{video}\n")
        
        print(os.getcwd())
        print(f"done ={done}")
        temp_cleaner()
        downloads_cleaner()
        extract_audio(video)
        segment_audio(audio_directory+'/temp.wav')

        segments = [f for f in Path(audio_directory).glob(f'temp_*.wav')]
        
        get_subs(audio_directory, f'{download_directory}video_en.srt')
        translate_srt_fa(f'{download_directory}video_en.srt', f'{download_directory}video_fa.srt')
        translate_srt_fr(f'{download_directory}video_en.srt', f'{download_directory}video_fr.srt')
        translate_srt_es(f'{download_directory}video_en.srt', f'{download_directory}video_es.srt')
        translate_srt_de(f'{download_directory}video_en.srt', f'{download_directory}video_de.srt')
        translate_srt_ru(f'{download_directory}video_en.srt', f'{download_directory}video_ru.srt')
        translate_srt_ja(f'{download_directory}video_en.srt', f'{download_directory}video_ja.srt')
        translate_srt_zh(f'{download_directory}video_en.srt', f'{download_directory}video_zh.srt')
        # print(log)

        combine_subtitles(video, f"{download_directory}video_en.srt", f'{download_directory}video_en_hard_encoded.mkv')
        combine_subtitles_mkv(video, f"{download_directory}video_en.srt", f'{download_directory}video_subbed_en.mkv')
        combine_subtitles_mkv_fa(video,f"{download_directory}video_en.srt",f'{download_directory}video_fa.srt',f'{download_directory}video_subbed_en_fa.mkv')
        combine_subtitles_mkv_all(video, 
                                  f"{download_directory}video_en.srt", 
                                  f'{download_directory}video_fa.srt',
                                  f"{download_directory}video_fr.srt", 
                                  f'{download_directory}video_de.srt',
                                  f"{download_directory}video_es.srt", 
                                  f'{download_directory}video_ru.srt',
                                  f"{download_directory}video_zh.srt", 
                                  f'{download_directory}video_ja.srt',
                                  f'{download_directory}video_all_subs.mkv')


        with open(log_file, "r") as log:
            temp_str_list =   [ l for l in log.readlines()]
            temp_str = "\n".join(temp_str_list)
            log_sender(temp_str)
        done = True
        isdone_sender(done)
        uploads_cleaner()
        
        
             
    return render_template('index.html')

def isdone_sender(data):
    
    socketio.emit('isdone', {'isdone': data})
    with open(log_file, "a") as log:
        log.write("the operation is done.\n")

def log_sender(data):
    socketio.emit('log',{'log':data})




async def on_log_change():
    while True:
        current = read_log()
        global initial
        if initial != current:
            for line in current:
                if line not in initial:
                    print(f"change in log->  {line}")
                    log_sender(line)
            initial = current
        await asyncio.sleep(1)

def on_log_change_sync():
    print("inside on_log_change_sync")
    while True:
        current = read_log()
        global initial
        if initial != current:
            for line in current:
                if line not in initial:
                    print(f"change in log->  {line}")
                    log_sender(line)
            initial = current

def stop():
    task.cancel()

def read_log():

        with open("log.txt", "r") as f:
            line_list = f.readlines()
        return line_list
    




if __name__ == '__main__':

    import webbrowser
    # webbrowser.open("http://127.0.0.1:5000")
    a= socketio.start_background_task(webbrowser.open("http://127.0.0.1:5000"))
    a.join()
    # a.cancel()

    socketio.start_background_task(on_log_change_sync)
    socketio.start_background_task(socketio.run(app)).join()



