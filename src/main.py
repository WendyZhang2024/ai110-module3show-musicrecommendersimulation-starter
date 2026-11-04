"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main            # run every profile
    python -m src.main "Chill Lofi"   # run one profile by name
"""

import os
import sys
from typing import Dict, List

try:  # `python -m src.main`
    from src.recommender import load_songs, recommend_songs
except ModuleNotFoundError:  # `python src/main.py`
    from recommender import load_songs, recommend_songs

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "songs.csv")

# Four everyday taste profiles plus one that the catalog cannot satisfy, used to
# see where the scoring breaks down.
PROFILES: Dict[str, Dict] = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.85},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.30},
    "Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.90},
    "J-Pop, Calm": {"genre": "j-pop", "mood": "calm", "energy": 0.40},
    "Impossible: Classical + Euphoric": {
        "genre": "classical",
        "mood": "euphoric",
        "energy": 0.90,
    },
}


def show_recommendations(
    profile_name: str, user_prefs: Dict, songs: List[Dict], k: int = 5
) -> None:
    """Print the top k songs for one user profile."""
    print("=" * 72)
    print(
        f"{profile_name}: genre={user_prefs['genre']}, "
        f"mood={user_prefs['mood']}, energy={user_prefs['energy']}"
    )
    print("=" * 72)
    for rank, (song, score, explanation) in enumerate(
        recommend_songs(user_prefs, songs, k=k), start=1
    ):
        print(f"{rank}. {song['title']} - {song['artist']}  ({score:.2f}/4.00)")
        print(f"   because: {explanation}")
    print()


def main() -> None:
    songs = load_songs(DATA_PATH)
    print(f"Loaded songs: {len(songs)}")
    print()

    requested = sys.argv[1] if len(sys.argv) > 1 else None
    for profile_name, user_prefs in PROFILES.items():
        if requested and requested.lower() not in profile_name.lower():
            continue
        show_recommendations(profile_name, user_prefs, songs)


if __name__ == "__main__":
    main()
