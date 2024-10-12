import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from pydub import AudioSegment
import os

# Load pretrained Wav2Vec2.0 model and processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

audio_path = "GW_AE_L2_CD1_Track 59.mp3"

if not audio_path.endswith(".wav"):
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    wav_path = "converted_audio.wav"
    audio.export(wav_path, format="wav")
    audio_path = wav_path


waveform, sample_rate = torchaudio.load(audio_path)

if sample_rate != 16000:
    waveform = torchaudio.transforms.Resample(sample_rate, 16000)(waveform)

input_values = processor(waveform.squeeze().numpy(), return_tensors="pt", sampling_rate=16000).input_values
with torch.no_grad():
    logits = model(input_values).logits

predicted_ids = torch.argmax(logits, dim=-1)
transcription = processor.decode(predicted_ids[0])

if audio_path == "converted_audio.wav":
    os.remove(audio_path)

print("Transcription:", transcription)
