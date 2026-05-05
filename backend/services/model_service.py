import torch
import torchaudio
from pathlib import Path
from typing import Optional


class ModelService:
    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_type = None  # "whisper" or "wav2vec2"

    def load(self):
        if (self.model_dir / "config.json").exists():
            cfg = self._read_config()
        else:
            raise FileNotFoundError(f"No config.json in {self.model_dir}")

        if "Whisper" in str(cfg.get("architectures", "")):
            self._load_whisper()
        elif "Wav2Vec2" in str(cfg.get("architectures", "")):
            self._load_wav2vec2()
        else:
            raise ValueError(f"Unknown model architecture: {cfg.get('architectures')}")

    def _read_config(self):
        import json
        with open(self.model_dir / "config.json") as f:
            return json.load(f)

    def _load_whisper(self):
        from transformers import WhisperProcessor, WhisperForConditionalGeneration

        model_path = str(self.model_dir)
        self.processor = WhisperProcessor.from_pretrained(model_path)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        self.model_type = "whisper"

    def _load_wav2vec2(self):
        from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

        model_path = str(self.model_dir)
        self.processor = Wav2Vec2Processor.from_pretrained(model_path)
        self.model = Wav2Vec2ForCTC.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        self.model_type = "wav2vec2"

    def transcribe(self, audio_path: str) -> dict:
        speech, sr = torchaudio.load(audio_path)

        if sr != 16000:
            resampler = torchaudio.transforms.Resample(sr, 16000)
            speech = resampler(speech)
            sr = 16000

        speech = speech.squeeze().numpy()

        if self.model_type == "whisper":
            return self._transcribe_whisper(speech)
        else:
            return self._transcribe_wav2vec2(speech)

    def _transcribe_whisper(self, speech) -> dict:
        inputs = self.processor.feature_extractor(
            speech, sampling_rate=16000, return_tensors="pt"
        ).input_features.to(self.device)

        with torch.no_grad():
            pred_ids = self.model.generate(inputs)

        text = self.processor.tokenizer.batch_decode(
            pred_ids, skip_special_tokens=True
        )[0]

        return {"text": text, "model_type": self.model_type}

    def _transcribe_wav2vec2(self, speech) -> dict:
        inputs = self.processor(
            speech, sampling_rate=16000, return_tensors="pt", padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            logits = self.model(**inputs).logits

        pred_ids = torch.argmax(logits, dim=-1)[0]
        text = self.processor.decode(pred_ids)

        return {"text": text, "model_type": self.model_type}


model_service: Optional[ModelService] = None


def get_model_service(model_dir: str = "models/whisper-small-cebuano") -> ModelService:
    global model_service
    if model_service is None:
        model_service = ModelService(model_dir)
        model_service.load()
    return model_service
