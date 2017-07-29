FROM ubuntu

LABEL authors="Yasyf Mohamedali <yasyfm@gmail.com>"

CMD ["/bin/bash"]

RUN dnf groupinstall -y "Development Tools"; \
  dnf install -y cmake \
      SDL-devel \
      python-devel \
      lapack-devel \
      libsndfile-devel \
      fftw-devel \
        clang \
        clang-devel \
        swig \
        gcc-c++

RUN git clone https://github.com/aalto-speech/AaltoASR.git; \
    cd AaltoASR; \
    mkdir build; \
    cd build; \
    cmake .. ; \
    make; \
    make install

RUN git clone https://github.com/aalto-speech/speaker-diarization.git; \
    cd /speaker-diarization; \
    ln -s ../AaltoASR ./ ; \
    ln -s ../AaltoASR/build ./ ; \
    ln -s ../AaltoASR/build/aku/feacat ./ ; \
    pip install numpy scipy docopt lxml

RUN apt-get install -y python python-dev python-pip build-essential swig git libpulse-dev; \
    pip install pocketsphinx;
