"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

import os
from typing import Dict, List

try:  # `python -m src.main`
    from src.recommender import load_songs, recommend_songs
except ModuleNotFoundError:  # `python src/main.py`
    from recommender import load_songs, recommend_songs

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "songs.csv")


def show_recommendations(
    profile_name: str, user_prefs: Dict, songs: List[Dict], k: int = 5
) -> None:
    """Print the top k songs for one user profile."""
    print("=" * 64)
    print(
        f"{profile_name}: genre={user_prefs['genre']}, "
        f"mood={user_prefs['mood']}, energy={user_prefs['energy']}"
    )
    print("=" * 64)
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

    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    show_recommendations("Starter profile", user_prefs, songs)


if __name__ == "__main__":
    main()
