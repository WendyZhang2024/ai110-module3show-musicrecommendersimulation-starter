"""
Core logic for the Music Recommender Simulation.

Scoring recipe (documented in README):
    +2.0  genre matches the user's favorite genre
    +1.0  mood matches the user's favorite mood
    +1.0 * (1 - |song energy - target energy|)   energy similarity
Maximum score is 4.0.
"""

import csv
from dataclasses import dataclass
from typing import Dict, List, Tuple

GENRE_POINTS = 2.0
MOOD_POINTS = 1.0
ENERGY_POINTS = 1.0
MAX_SCORE = GENRE_POINTS + MOOD_POINTS + ENERGY_POINTS

NUMERIC_FIELDS = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """Score one Song object against a UserProfile using the same recipe."""
        total = 0.0
        if song.genre == user.favorite_genre:
            total += GENRE_POINTS
        if song.mood == user.favorite_mood:
            total += MOOD_POINTS
        total += ENERGY_POINTS * (1 - abs(song.energy - user.target_energy))
        return round(total, 2)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs, highest score first."""
        ranked = sorted(
            self.songs,
            key=lambda song: (
                -self._score(user, song),
                abs(song.energy - user.target_energy),
                song.id,
            ),
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain in plain language why this song scored what it scored."""
        parts = []
        if song.genre == user.favorite_genre:
            parts.append(f"genre match: {song.genre} (+{GENRE_POINTS})")
        else:
            parts.append(f"genre mismatch: {song.genre} vs {user.favorite_genre} (+0.0)")

        if song.mood == user.favorite_mood:
            parts.append(f"mood match: {song.mood} (+{MOOD_POINTS})")
        else:
            parts.append(f"mood mismatch: {song.mood} vs {user.favorite_mood} (+0.0)")

        gap = abs(song.energy - user.target_energy)
        points = ENERGY_POINTS * (1 - gap)
        parts.append(
            f"energy {song.energy:.2f} vs target {user.target_energy:.2f} "
            f"(gap {gap:.2f}, +{points:.2f})"
        )
        return " | ".join(parts)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Load the catalog from a CSV file and convert numeric columns to floats.
    Required by src/main.py
    """
    songs: List[Dict] = []
    # encoding="utf-8" is required: the file contains Japanese and Chinese titles
    # and Windows would otherwise fall back to GBK and fail.
    with open(csv_path, "r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            song = dict(row)
            song["id"] = int(song["id"])
            for field in NUMERIC_FIELDS:
                song[field] = float(song[field])
            songs.append(song)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs.get("genre"):
        score += GENRE_POINTS
        reasons.append(f"genre match: {song['genre']} (+{GENRE_POINTS})")
    else:
        reasons.append(
            f"genre mismatch: {song['genre']} vs {user_prefs.get('genre')} (+0.0)"
        )

    if song["mood"] == user_prefs.get("mood"):
        score += MOOD_POINTS
        reasons.append(f"mood match: {song['mood']} (+{MOOD_POINTS})")
    else:
        reasons.append(
            f"mood mismatch: {song['mood']} vs {user_prefs.get('mood')} (+0.0)"
        )

    target_energy = float(user_prefs.get("energy", 0.5))
    gap = abs(song["energy"] - target_energy)
    energy_points = ENERGY_POINTS * (1 - gap)
    score += energy_points
    reasons.append(
        f"energy {song['energy']:.2f} vs target {target_energy:.2f} "
        f"(gap {gap:.2f}, +{energy_points:.2f})"
    )

    return round(score, 2), reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Score every song, rank them, and return the top k as (song, score, explanation).
    Required by src/main.py
    """
    target_energy = float(user_prefs.get("energy", 0.5))

    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, reasons))

    # Rank by score descending. Ties go to the closer energy match, then to the
    # lower id, so the output is deterministic and reproducible.
    scored.sort(
        key=lambda item: (
            -item[1],
            abs(item[0]["energy"] - target_energy),
            item[0]["id"],
        )
    )

    return [(song, score, " | ".join(reasons)) for song, score, reasons in scored[:k]]
