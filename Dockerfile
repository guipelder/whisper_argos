FROM python:3.11-slim

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install git -y

#RUN pip3 install --default-timeout=100 "git+https://github.com/openai/whisper.git" 
RUN apt-get install -y ffmpeg
RUN pip install sentencepiece
RUN pip3 install --default-timeout=100 torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

RUN  apt-get -y install cmake build-essential pkg-config libgoogle-perftools-dev
#RUN git clone https://github.com/google/sentencepiece.git 
##RUN cd sentencepiece
#3RUN mkdir build
#RUN cd build
##RUN cmake .. 
#RUN make install
#RUN cd ../python
#RUN python setup.py bdist_wheel
#RUN pip install dist/sentencepiece*.whl
#RUN git clone https://github.com/google/sentencepiece.git 
#RUN cd sentencepiece
#WORKDIR /python-docker/sentencepiece

#RUN mkdir build
#RUN pwd
#RUN cd sentencepiece
#WORKDIR /python-docker/sentencepiece/build
#RUN cmake -S sentencepiece -B sentencepiece/build  
#RUN cmake ..
#RUN  ls 
#RUN pwd
#RUN cd sentencepiece
#RUN cd build
#RUN  ls
#RUN make  -j $(nproc)
#3RUN  make install
#RUN  ldconfig -v

RUN git clone https://github.com/google/sentencepiece.git 
WORKDIR /python-docker/sentencepiece
RUN mkdir build
WORKDIR /python-docker/sentencepiece/build
RUN cmake .. -DSPM_ENABLE_SHARED=OFF -DCMAKE_INSTALL_PREFIX=./root
RUN make install
WORKDIR /python-docker/sentencepiece/python
RUN python setup.py bdist_wheel
RUN pip install dist/sentencepiece*.whl





RUN pip3 install sentencepiece
WORKDIR /python-docker
RUN pip3 install --default-timeout=100 -r requirements.txt
RUN ls 

COPY . .
RUN python3 argos_setup.py

EXPOSE 5000

#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
#CMD ["python3", "whisper.py"]
ENTRYPOINT ["python3", "whisper.py"]
#CMD [ "python3", "-m" , "whisper", "--host=0.0.0.0"]
