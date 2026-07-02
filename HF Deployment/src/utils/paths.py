"""Resolve project paths so the app works no matter the current working directory
(local `streamlit run` or Hugging Face Spaces)."""
import os

# this file is <root>/src/utils/paths.py -> go up 3 levels to the project root
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARTIFACTS = os.path.join(ROOT, "artifacts")
LEXICON = os.path.join(ROOT, "colloquial-indonesian-lexicon.csv")
LOGO = os.path.join(ROOT, "Topic Pulse.png")  # drop the logo PNG in the repo root
