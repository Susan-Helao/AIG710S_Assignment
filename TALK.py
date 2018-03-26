'''
Developper: Vaakura
Last modified: 26/03/2018
'''
import webrtcvad
import collections
import sys
import signal
import pyaudio

from array import array
from struct import pack
import wave
import time
from subprocess import Popen, PIPE
from chatterbot import ChatBot
import os


def speakBrain(spoken_data, __ACTION_TODO):
	actionTodo = 'Conversation'
	#----directions
	response = str(responseThread.get_response(spoken_data))

	if __ACTION_TODO:
		#Translation
		actionTodo = 'Translation'
		print('\nAction to do : {}\n\n'.format(actionTodo))
		print('\nEnglish -> Oshiwambo processing : {}\n\n'.format(response))
		responseFile = str(response) + '.mp3';
		os.system('play -q user-talks/oshiwambo-prescripts/' + responseFile);
		closeListening()
	elif '[TRANSLATION-ID]' in response:
		#Translation
		actionTodo = 'Translation'
		response = response.replace('[TRANSLATION-ID]', '')
		print('\nAction to do : {}\n\n'.format(actionTodo))
		print('\nEnglish -> Oshiwambo processing : {}\n\n'.format(response))
		#---After asking
		os.system('pico2wave --wave /tmp/sample.wav -l en-GB "' + str(response) + '" && play -qV0 /tmp/sample.wav')
		return True
	else:
		#Conversation
		if ('[' in response):
			print('\nEnglish -> Text processing : {}\n\n'.format(spoken_data))
			os.system('pico2wave --wave /tmp/sample.wav -l en-GB "I don\'t understand. Come again." && play -qV0 /tmp/sample.wav')
		else:
			print('\nEnglish -> Text processing : {}\n\n'.format(spoken_data))
			os.system('pico2wave --wave /tmp/sample.wav -l en-GB "' + str(response) + '" && play -qV0 /tmp/sample.wav')
			os.system('rm db.sqlite3');


#---Action todo master
#True: Tranaslation
#False: Default - Conversation
WAVESTYLE = pyaudio.paInt16
WAVE_APLITUDE_TIME_MS = 1500
DUALAUDIOPATHS = 1
WAVELENGTH = 16000
WAVE_LENGTH_TIME_MS = 30
WAVE_SLIDE_MAGNITUDE = int(WAVELENGTH * WAVE_LENGTH_TIME_MS / 1000)
WAVE_SLIDE_MAGNITUDE_BINARY = WAVE_SLIDE_MAGNITUDE * 2
WAVE_SLIDE_AMPLITUDE_NUMBER = int(WAVE_APLITUDE_TIME_MS / WAVE_LENGTH_TIME_MS)
WAVE_AMPLITUDE_NUMBER = int(1200 / WAVE_LENGTH_TIME_MS)
WAVE_AMPLITUDE_NUMBER_MAX = WAVE_AMPLITUDE_NUMBER * 2

BEGIN_LISTENING_POINT = int(WAVE_AMPLITUDE_NUMBER * WAVE_LENGTH_TIME_MS * 0.5 * WAVELENGTH)

_VAD_POINT = webrtcvad.Vad(1)

_PA_POINT = pyaudio.PyAudio()
STREAM_PATH = _PA_POINT.open(format=WAVESTYLE,
                 channels=DUALAUDIOPATHS,
                 rate=WAVELENGTH,
                 input=True,
                 start=False,
                 # input_device_index=2,
                 frames_per_buffer=WAVE_SLIDE_MAGNITUDE)


got_a_sentence = False
leave = False

#------Answer route
responseThread = ChatBot(
    'Bot Thread',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
)
responseThread.train("chatterbot.corpus.english.englishProto")

#--------Back-end developpers only!!!
def closeListening():
    sys.exit(0)



def handle_int(sig, chunk):
    global leave, got_a_sentence
    leave = True
    got_a_sentence = True

#Probabilistic voice processing command yield
def commandYield(command):
    process = Popen(command, stdout=PIPE, shell=True)
    while True:
        line = process.stdout.readline().rstrip()
        if not line:
            break
        yield line


def record_to_file(path, data, sample_width):
    "Records from the microphone and outputs the resulting data to 'path'"
    # sample_width, data = record()
    data = pack('<' + ('h' * len(data)), *data)
    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(WAVELENGTH)
    wf.writeframes(data)
    wf.close()


def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 32767  # 16384
    times = float(MAXIMUM) / max(abs(i) for i in snd_data)
    r = array('h')
    for i in snd_data:
        r.append(int(i * times))
    return r

signal.signal(signal.SIGINT, handle_int)


def listen(got_a_sentence, leave):
    #got_a_sentence = got_a_sentence
    #leave = leave
    __ACTION_TODO = False

    while not leave:
        #Break the process
        signal.signal(signal.SIGINT, closeListening) 
        #-----------------
        
        ring_buffer = collections.deque(maxlen=WAVE_SLIDE_AMPLITUDE_NUMBER)
        triggered = False
        voiced_frames = []
        ring_buffer_flags = [0] * WAVE_AMPLITUDE_NUMBER
        ring_buffer_index = 0

        ring_buffer_flags_end = [0] * WAVE_AMPLITUDE_NUMBER_MAX
        ring_buffer_index_end = 0
        buffer_in = ''
        # WangS
        raw_data = array('h')
        index = 0
        start_point = 0
        StartTime = time.time()
        print("\n+ Computer is listening: ")
        STREAM_PATH.start_stream()

        while not got_a_sentence and not leave:
            chunk = STREAM_PATH.read(WAVE_SLIDE_MAGNITUDE)
            # add WangS
            raw_data.extend(array('h', chunk))
            index += WAVE_SLIDE_MAGNITUDE
            TimeUse = time.time() - StartTime

            active = _VAD_POINT.is_speech(chunk, WAVELENGTH)

            sys.stdout.write('+' if active else '#')
            ring_buffer_flags[ring_buffer_index] = 1 if active else 0
            ring_buffer_index += 1
            ring_buffer_index %= WAVE_AMPLITUDE_NUMBER

            ring_buffer_flags_end[ring_buffer_index_end] = 1 if active else 0
            ring_buffer_index_end += 1
            ring_buffer_index_end %= WAVE_AMPLITUDE_NUMBER_MAX

            # start point detection
            if not triggered:
                #__WAITING__VAR1 = time.time()
                #----------------------------
                ring_buffer.append(chunk)
                num_voiced = sum(ring_buffer_flags)
                if num_voiced > 0.25 * WAVE_AMPLITUDE_NUMBER:
                    sys.stdout.write(' Open ')
                    triggered = True
                    start_point = index - WAVE_SLIDE_MAGNITUDE * 20  # start point
                    # voiced_frames.extend(ring_buffer)
                    ring_buffer.clear()
            # end point detection
            else:
                #__WAITING__VAR1 = time.time()
                # voiced_frames.append(chunk)
                ring_buffer.append(chunk)
                num_unvoiced = WAVE_AMPLITUDE_NUMBER_MAX - sum(ring_buffer_flags_end)
                if num_unvoiced > 0.95 * WAVE_AMPLITUDE_NUMBER_MAX or TimeUse > 80:
                    sys.stdout.write(' Close ')
                    triggered = False
                    got_a_sentence = True

            sys.stdout.flush()



        sys.stdout.write('\n')

        STREAM_PATH.stop_stream()
        print("* Thinking")
        got_a_sentence = False

        # write to file
        raw_data.reverse()
        for index in range(start_point):
            raw_data.pop()
        raw_data.reverse()
        raw_data = normalize(raw_data)
        #----
        speech_path = 'user-talks/speech_' + str(round(time.time())) + '.wav'
        record_to_file(speech_path, raw_data, 2)
        leave = True

        os.system('clear')

        #---Voice probbabilistics processing - voice to text
        for path in commandYield("/home/vaakura/Desktop/project-oshiwambo/DeepSpeech/native_client/bin/deepspeech /home/vaakura/Desktop/project-oshiwambo/DeepSpeech/native_client/models/output_graph.pb " + speech_path + " /home/vaakura/Desktop/project-oshiwambo/DeepSpeech/native_client/models/alphabet.txt"):
            spoken_data = str(path.decode('utf-8'))

            #Clear speech datas
            os.system('rm ' + speech_path)

            response = str(responseThread.get_response(spoken_data))

            if '[TRANSLATION-ID]' in response:
            	got_a_sentence = False
            	leave = False

            if ('[' in response) and (__ACTION_TODO == False):
            	got_a_sentence = False
            	leave = False

            #----------Speak brain
            __ACTION_TODO = speakBrain(spoken_data, __ACTION_TODO)

listen(False, False)
