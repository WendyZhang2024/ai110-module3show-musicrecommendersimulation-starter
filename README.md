# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

### How real recommenders work

Large platforms mix two strategies. Collaborative filtering looks at **people**:
it finds users whose listening history overlaps with yours and recommends what
they loved. Content-based filtering looks at **songs**: it compares a track's
attributes (genre, mood, energy, tempo) against what you already play. Spotify
leans on collaborative filtering through playlist co-occurrence, then enriches it
with audio features and text mined from playlist titles. TikTok runs mostly on
implicit signals such as watch-through rate, replays, and how fast you swipe, and
updates almost immediately. Each has a known failure mode. Collaborative
filtering cannot handle cold start, because a new user or a brand-new song has no
history to compare. Content-based filtering creates a filter bubble, because it
can only ever surface more of what you already like.

### How this simulation simplifies it

This project is a deliberately small content-based recommender. It ignores other
users completely and scores every song against a single user's stated taste.

**What each `Song` stores:** `id`, `title`, `artist`, `genre`, `mood`, `energy`
(0.0–1.0), `tempo_bpm`, `valence`, `danceability`, `acousticness`. Only genre,
mood and energy drive the score right now. The rest are loaded and left available
for later experiments.

**What `UserProfile` stores:** `favorite_genre`, `favorite_mood`,
`target_energy`, `likes_acoustic`.

**Scoring rule (one song at a time):**

| Rule | Points |
| --- | --- |
| Genre matches `favorite_genre` | +2.0 |
| Mood matches `favorite_mood` | +1.0 |
| Energy similarity | +1.0 × (1 − \|song.energy − target_energy\|) |

Genre carries the heaviest weight because it is the hardest boundary. A listener
who wants quiet music is not served by a metal track no matter how well the
energy lines up. Mood separates songs inside the same genre. Energy is scored by
distance rather than height: a song is rewarded for being close to the target, so
a 0.93 track scores badly for someone whose target is 0.2. Maximum score is 4.0.

**Ranking rule (the whole catalog at once):** score every song in the CSV with
the rule above, sort from highest to lowest, and return the top k (default 5). A
single score means little without the rest of the list to compare it against,
which is why scoring and ranking stay separate steps.

**Known weakness in this design:** a genre match alone is worth 2.0, which is
enough to outvote a completely wrong mood. Run the default pop / happy / energy
0.8 profile and the aggressive "Gym Hero" lands second, purely on its pop tag.
The catalog is also small and skewed: 3 of the 10 songs are lofi, and energy
clusters at the extremes with nothing between 0.42 and 0.75, so a user targeting
the middle of the range gets weak matches.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



