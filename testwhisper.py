from flask import send_file, send_from_directory
from flask import jsonify
from functions import *
# combine_subtitles('./video.mp4', './video_en.srt', './video_subbed_en.mp4')
# combine_subtitles('./video.mp4', './video_fa.srt', './video_subbed_en_fa.mp4')

import os
from flask import Flask, render_template, request
from flask_dropzone import Dropzone
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
from functions import temp_str


download_directory = './downloads/'
audio_directory = './temp_audio/'
video = "not changed"
# temp_str = ""
# from flask import Flask, render_template, request
# from flask_dropzone import Dropzone
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
socketio = SocketIO(app,cors_allowed_origins="*")

# global done value
done = False

@socketio.on('connect')
def connect():
    print('Client connected')



def get_subs_fa_en_optimized(audio_directory, output_file1 ,output_file2):
    global temp_str
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
                    temp_str += inferred_text + "\n"
                    
                    print(inferred_text)
                    translatedText = argostranslate.translate.translate(inferred_text, from_code, to_code)
                    temp_str += translatedText + "\n"
                    print(translatedText)
                else:
                    inferred_text = ''
                    translatedText= ''
                    temp_str += '.' + '\n'

                log_sender(temp_str)
                limits = audio_file.name[:-4].split("_")[-1].split("-")
                log_sender(limits)
                # temp_0002.000-0010.000
                limits = [float(limit) for limit in limits]
                out_file1.write(get_srt_line(translatedText, line_count, limits))
                out_file1.flush()
                out_file2.write(get_srt_line(inferred_text , line_count, limits))
                out_file2.flush()
                line_count += 1
                # yield temp_str


@app.route('/done', methods=['GET', 'POST'])
def done_check():
    dic = {"isdone": done}
    # TODO NOt necessary to use jsonify
    return jsonify(dic)


@app.route('/mkv_en')  # this is a job for GET, not POST
def mkv_en():

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
        # get_subs_fa_en_optimized(audio_directory, f'{download_directory}video_fa.srt', f'{download_directory}video_en.srt')
        # print(log)
        # log_sender(temp_str)

        combine_subtitles(video, f"{download_directory}video_en.srt", f'{download_directory}video_en_hard_encoded.mkv')
        combine_subtitles_mkv(video, f"{download_directory}video_en.srt", f'{download_directory}video_subbed_en.mkv')
        combine_subtitles_mkv_fa(video,f"{download_directory}video_en.srt",f'{download_directory}video_fa.srt',f'{download_directory}video_subbed_en_fa.mkv')

        done = True
        isdone_sender(done)
    return render_template('index.html')

def isdone_sender(data):
    
    # socketio.emit('log', {'log': temp_str })
    socketio.emit('isdone', {'isdone': data})
    # socketio.emit('log', ":somthing")

# def log_sender():
#     global temp_str
#     socketio.emit('log',{'log':temp_str})

def log_sender(data):
    socketio.emit('log',{'log':data})



if __name__ == '__main__':
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")
    # app.run(debug=True)
    socketio.run(app)

