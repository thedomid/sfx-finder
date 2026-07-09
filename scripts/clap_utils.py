"""Shared CLAP model loading + embedding helpers for sfx-finder."""
import sys

import numpy as np

import config

_INSTALL_MSG = (
    "Missing dependencies. Install with:\n"
    "  pip install torch --index-url https://download.pytorch.org/whl/cpu\n"
    "  pip install transformers librosa soundfile\n"
    "(CPU torch is fine — CLAP inference is fast enough without a GPU.)"
)

_model = None
_processor = None


def load_model():
    """Load CLAP model + processor once. Downloads ~600MB on first ever run."""
    global _model, _processor
    if _model is not None:
        return _model, _processor
    try:
        import torch  # noqa: F401
        from transformers import ClapModel, ClapProcessor
    except ImportError:
        print(_INSTALL_MSG, file=sys.stderr)
        sys.exit(1)

    _model = ClapModel.from_pretrained(config.CLAP_MODEL)
    _model.eval()
    _processor = ClapProcessor.from_pretrained(config.CLAP_MODEL)
    return _model, _processor


def load_audio(path):
    """Load an audio file as 48kHz mono float32, truncated to MAX_SECONDS."""
    try:
        import librosa
    except ImportError:
        print(_INSTALL_MSG, file=sys.stderr)
        sys.exit(1)
    y, _ = librosa.load(
        str(path),
        sr=config.SAMPLE_RATE,
        mono=True,
        duration=config.MAX_SECONDS,
    )
    return y


def embed_audio_batch(waveforms):
    """Embed a list of waveforms -> (N, D) L2-normalized numpy array."""
    import torch

    model, processor = load_model()
    inputs = processor(
        audio=waveforms, sampling_rate=config.SAMPLE_RATE, return_tensors="pt", padding=True
    )
    with torch.no_grad():
        emb = model.get_audio_features(**inputs).pooler_output
    emb = emb.cpu().numpy().astype(np.float32)
    return _l2norm(emb)


def embed_text(text):
    """Embed a text query -> (D,) L2-normalized numpy vector."""
    import torch

    model, processor = load_model()
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    with torch.no_grad():
        emb = model.get_text_features(**inputs).pooler_output
    emb = emb.cpu().numpy().astype(np.float32)
    return _l2norm(emb)[0]


def _l2norm(x):
    norms = np.linalg.norm(x, axis=-1, keepdims=True)
    norms[norms == 0] = 1.0
    return x / norms
