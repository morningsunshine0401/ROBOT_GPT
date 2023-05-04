import io
from pydub import AudioSegment
import speech_recognition as sr
import whisper
import queue
import tempfile
import os
import threading
import click
import torch
import numpy as np

class VoiceRecognizer:
    def __init__(self, model="base", english=False, verbose=False, energy=300, pause=0.8, dynamic_energy=False, save_file=False):
        self.model = model
        self.english = english
        self.verbose = verbose
        self.energy = energy
        self.pause = pause
        self.dynamic_energy = dynamic_energy
        self.save_file = save_file
        self.temp_dir = tempfile.mkdtemp() if self.save_file else None

    def main(self):
        if self.model != "large" and self.english:
            self.model = self.model + ".en"
        self.audio_model = whisper.load_model(self.model)
        self.audio_queue = queue.Queue()
        self.result_queue = queue.Queue()
        threading.Thread(target=self.record_audio).start()
        threading.Thread(target=self.transcribe_forever).start()

        while True:
            message = self.result_queue.get()
            print(message)
            return message

    def record_audio(self):
        r = sr.Recognizer()
        r.energy_threshold = self.energy
        r.pause_threshold = self.pause
        r.dynamic_energy_threshold = self.dynamic_energy

        with sr.Microphone(sample_rate=16000) as source:
            print("Say something!")
            i = 0
            while True:
                audio = r.listen(source)
                if self.save_file:
                    data = io.BytesIO(audio.get_wav_data())
                    audio_clip = AudioSegment.from_file(data)
                    filename = os.path.join(self.temp_dir, f"temp{i}.wav")
                    audio_clip.export(filename, format="wav")
                    audio_data = filename
                else:
                    torch_audio = torch.from_numpy(np.frombuffer(audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0)
                    audio_data = torch_audio

                self.audio_queue.put_nowait(audio_data)
                i += 1

    def transcribe_forever(self):
        while True:
            audio_data = self.audio_queue.get()
            if self.english:
                result = self.audio_model.transcribe(audio_data, language='english')
            else:
                result = self.audio_model.transcribe(audio_data)

            if not self.verbose:
                predicted_text = result["text"]
                self.result_queue.put_nowait("You said: " + predicted_text)
            else:
                self.result_queue.put_nowait(result)

            if self.save_file:
                os.remove(audio_data)

if __name__ == "__main__":
    recognizer = VoiceRecognizer()
    recognizer.main()
