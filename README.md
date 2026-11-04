# 🎵 Music Recommender Simulation

## Project Summary

TasteRadar 1.0 is a small content-based music recommender. It scores every song
in a 20-song catalog against a listener's favorite genre, favorite mood and target
energy, then returns the top five with the points awarded for each pick spelled
out.

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

**The catalog:** 20 songs across 16 genres in `data/songs.csv`. The ten starter
rows were extended with ten more that cover gaps in the original file: j-pop,
anime rock, classical, cinematic, dream pop, edm, R&B and mandopop were missing,
and the original ten had no track between 0.45 and 0.75 energy. The numeric
columns (energy, valence, danceability, acousticness) are hand-assigned estimates
of how each track feels rather than measurements from an audio API, so they are
internally consistent but only approximate.

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

**Known weakness in this design:** a genre match alone is worth 2.0, enough to
outvote a completely wrong mood and even a wildly wrong energy level. Ask for
`classical / euphoric / energy 0.90` and the top result is still Gymnopédie No.1,
a calm piano piece sitting at energy 0.12, because its genre tag alone carries
2.0. The catalog is also uneven: 13 of the 16 genres appear exactly once while
lofi alone accounts for 3 songs, and energy is still barbell-shaped, with 10
songs below 0.45, only 4 between 0.45 and 0.75, and 6 above.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

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

Run `python -m src.main` to print all five profiles in one go. Output for the
high-energy pop profile on the 20-song catalog:

```
Loaded songs: 20

========================================================================
High-Energy Pop: genre=pop, mood=happy, energy=0.85
========================================================================
1. Sunrise City - Neon Echo  (3.97/4.00)
   because: genre match: pop (+2.0) | mood match: happy (+1.0) | energy 0.82 vs target 0.85 (gap 0.03, +0.97)
2. Gym Hero - Max Pulse  (2.92/4.00)
   because: genre match: pop (+2.0) | mood mismatch: intense vs happy (+0.0) | energy 0.93 vs target 0.85 (gap 0.08, +0.92)
3. Rooftop Lights - Indigo Parade  (1.91/4.00)
   because: genre mismatch: indie pop vs pop (+0.0) | mood match: happy (+1.0) | energy 0.76 vs target 0.85 (gap 0.09, +0.91)
4. 火炎 - QUEEN BEE  (1.00/4.00)
   because: genre mismatch: anime rock vs pop (+0.0) | mood mismatch: passionate vs happy (+0.0) | energy 0.85 vs target 0.85 (gap 0.00, +1.00)
5. Storm Runner - Voltline  (0.94/4.00)
   because: genre mismatch: rock vs pop (+0.0) | mood mismatch: intense vs happy (+0.0) | energy 0.91 vs target 0.85 (gap 0.06, +0.94)
```

---

## Experiments You Tried

### Experiment 1: five profiles side by side

`python -m src.main` runs five profiles: High-Energy Pop, Chill Lofi, Intense
Rock, J-Pop Calm, and one deliberately impossible profile
(`classical / euphoric / 0.90`). Top five for each, title and score:

```
High-Energy Pop        (pop / happy / 0.85)
  Sunrise City 3.97 | Gym Hero 2.92 | Rooftop Lights 1.91 | 火炎 1.00 | Storm Runner 0.94

Chill Lofi             (lofi / chill / 0.30)
  Library Rain 3.95 | Midnight Coding 3.88 | Focus Flow 2.90 | Spacewalk Thoughts 1.98 | Cornfield Chase 1.00

Intense Rock           (rock / intense / 0.90)
  Storm Runner 3.99 | Gym Hero 1.97 | Piscina spedup 0.95 | 火炎 0.95 | Sunrise City 0.92

J-Pop, Calm            (j-pop / calm / 0.40)
  晩餐歌 2.78 | 打上花火 2.68 | Gymnopédie No.1 1.72 | Focus Flow 1.00 | Midnight Coding 0.98

Impossible             (classical / euphoric / 0.90)
  Gymnopédie No.1 2.22 | Storm Runner 0.99 | Gym Hero 0.97 | Piscina spedup 0.95 | 火炎 0.95
```

The straightforward profiles behave the way I expected. Chill Lofi returns the three
lofi tracks first, and Intense Rock puts Storm Runner at 3.99 and then fills the
rest with anything loud, including pop and edm. The interesting one is the
impossible profile: it asks for euphoric 0.90-energy classical and gets
Gymnopédie No.1, a calm piano piece at energy 0.12, because the genre tag alone
is worth 2.0. **The system has no way to return nothing.** It always produces five
songs, so a request it cannot satisfy comes back looking like a normal answer.

The J-Pop Calm profile (`j-pop / calm / 0.40`) exposes a catalog problem rather
than a scoring problem: both j-pop tracks in the catalog are tagged energetic, so
a calm j-pop listener is served two energetic songs and only then reaches an
actual calm track (a classical piano piece) at rank 3.

### Experiment 2: shifting weight from genre to energy

Baseline weights are genre 2.0, mood 1.0, energy 1.0. I halved genre to 1.0 and
doubled energy to 2.0, then re-ran two profiles:

```
A. baseline (2.0 / 1.0 / 1.0)
  High-Energy Pop: Sunrise City 3.97 | Gym Hero 2.92 | Rooftop Lights 1.91 | 火炎 1.00 | Storm Runner 0.94

B. weight shift (1.0 / 1.0 / 2.0)
  High-Energy Pop: Sunrise City 3.94 | Gym Hero 2.84 | Rooftop Lights 2.82 | 火炎 2.00 | Storm Runner 1.88
```

The ranking order barely moves, but the gaps collapse. Rooftop Lights climbs from
1.91 to 2.82 and nearly ties Gym Hero at 2.84, because its correct mood and close
energy are now worth almost as much as a full genre match. With genre at 1.0 the
list stops being "pop first, everything else after" and becomes "whatever is
closest in energy". Genre still wins, but only by a hair.

### Experiment 3: removing the mood check

Setting mood points to 0.0 shows which songs depend on it:

```
A. baseline (mood = 1.0)
  High-Energy Pop: Sunrise City 3.97 | Gym Hero 2.92 | Rooftop Lights 1.91 | 火炎 1.00 | Storm Runner 0.94

C. mood removed (mood = 0.0)
  High-Energy Pop: Sunrise City 2.97 | Gym Hero 2.92 | 火炎 1.00 | Storm Runner 0.94 | Rooftop Lights 0.91
```

Rooftop Lights falls from rank 3 to rank 5 and loses a full point, because its
wrong genre was being rescued entirely by its mood match. Gym Hero, which was
never matching mood, does not change at all. So the mood term is doing real work
for cross-genre songs and almost nothing for same-genre songs.

---

## Limitations and Risks

- **Genre is nearly veto-proof.** Worth 2.0 on its own, it can outvote a wrong
  mood and a wrong energy at the same time, which is how a calm piano piece ends
  up as the top answer for someone asking for euphoric classical.
- **The catalog is thin and lopsided.** 13 of the 16 genres appear exactly once,
  and half the songs sit below 0.45 energy with another six above 0.75.
- **Some moods exist only inside one genre.** `calm` only appears on a classical
  track, `energetic` only on j-pop, so a user asking for calm j-pop can never be
  matched properly.
- **No diversity, no refusal, no memory.** The same three lofi tracks win every
  quiet request, nothing stops the system from returning five near-duplicates,
  and it cannot say "I do not have anything like that".
- **Feature values are hand-estimated**, not measured, so the scores are only as
  good as my own judgement about each track.

The full write-up is in the [Model Card](model_card.md).


---

## Reflection

I built most of the extra catalog from my own playlist, so the model already leans toward my taste before it scores anything. Changing the weights barely reordered the results, but removing the mood term moved a song four places. Arithmetic that simple can quietly favor whoever assembled the data.

The full write-up is in the [Model Card](model_card.md).


