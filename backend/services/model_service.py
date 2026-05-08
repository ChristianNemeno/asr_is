import torch
import torchaudio
from pathlib import Path
from transformers import WhisperProcessor, WhisperForConditionalGeneration


class ModelManager:
    def __init__(
        self,
        baseline_id: str = "openai/whisper-small",
        finetuned_path: str = "../train/output/whisper",
    ):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"ModelManager device: {self.device}")

        print(f"Loading baseline model: {baseline_id} ...")
        self.baseline_processor = WhisperProcessor.from_pretrained(baseline_id)
        self.baseline_model = WhisperForConditionalGeneration.from_pretrained(
            baseline_id
        ).to(self.device)
        self.baseline_model.eval()
        print("  baseline loaded.")

        print(f"Loading fine-tuned model: {finetuned_path} ...")
        self.finetuned_processor = WhisperProcessor.from_pretrained(finetuned_path)
        self.finetuned_model = WhisperForConditionalGeneration.from_pretrained(
            finetuned_path
        ).to(self.device)
        self.finetuned_model.eval()
        print("  fine-tuned loaded.")

    def transcribe(self, audio_path: str, model_type: str) -> dict:
        speech, sr = torchaudio.load(audio_path)

        if sr != 16000:
            resampler = torchaudio.transforms.Resample(sr, 16000)
            speech = resampler(speech)
            sr = 16000

        speech = speech.squeeze().numpy()

        if model_type == "baseline":
            processor = self.baseline_processor
            model = self.baseline_model
        else:
            processor = self.finetuned_processor
            model = self.finetuned_model

        inputs = processor.feature_extractor(
            speech, sampling_rate=16000, return_tensors="pt"
        ).input_features.to(self.device)

        with torch.no_grad():
            pred_ids = model.generate(inputs)

        text = processor.tokenizer.batch_decode(
            pred_ids, skip_special_tokens=True
        )[0]

        return {"text": text, "model_type": model_type}


_model_manager: ModelManager | None = None


def get_model_manager() -> ModelManager:
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
