from __future__ import annotations
import math, os, struct, subprocess, sys
from pathlib import Path

# Pure python wav read and strike extractor using c_dsp
AUDIO_EXTRACTOR = "./c_dsp/v3_4stage_extractor"
print(f"Extractor exists: {os.path.exists(AUDIO_EXTRACTOR)}")
