# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**TasteRadar 1.0**

The name is literal. The model sweeps a small catalog and reports whatever sits
closest to where the listener points it. It does not learn, remember, or adapt: it
sweeps once and returns a ranked list.

---

## 2. Intended Use

The project is framed around a question a startup music platform would ask: how do
apps like Spotify or TikTok decide what a user will love next, and can the smallest
honest version of that idea be rebuilt and inspected? TasteRadar 1.0 is that
prototype. It turns a song catalog plus a listener's stated taste profile into a
ranked list of five suggestions, and it records the reason for every pick, so the
whole path from data to prediction can be followed by hand.

It simulates the shape of a real recommender for classroom exploration, not for
production. It assumes the listener can name their taste precisely — one genre,
one mood, one energy target — and that those three do not contradict each other.
Real platforms never get that convenience: they infer taste from behavior instead
of asking for it, which is the larger problem this simulation deliberately skips.

What it is for:

- Showing how raw song attributes turn into a score and then into a ranking.
- Comparing the same ranking across different kinds of listeners.
- Making the failure cases visible, since the bias discussion lives there.

What it is not for:

- Not for real users or production traffic. Returning 5 of 20 songs spends a
  quarter of the catalog on one request.
- Not for inferring taste from behavior. No history, skips, repeats or likes are
  read.
- Not for vague or mixed requests. "Something chill but not too sad" cannot be
  expressed in three numbers.
- Not for discovery. It only ever surfaces what already resembles the target, so
  it cannot introduce a listener to a genre they have not named.

---

## 3. How the Model Works

Three pieces, kept separate on purpose.

**Input features.** Every song in the catalog carries attributes. Only three are
scored: genre (a label), mood (a label) and energy (a number from 0 to 1). Tempo,
valence, danceability and acousticness are loaded too, but they never affect a
score.

**User preferences.** A taste profile restates the same three things from the
listener's side: favorite genre, favorite mood, target energy.

**Scoring rule.** A judge with a short checklist walks each song past the profile.
Genre match earns 2 points, mood match earns 1, and energy earns up to 1 more
depending on how close it sits to the target. An exact energy match gets the full
point, a song at the opposite end of the scale gets almost nothing, and direction
does not matter: a target of 0.2 with a track at 0.25 scores the same as a target
of 0.8 with a track at 0.85. The ceiling is 4 points.

Genre is worth the most because it is the hardest boundary. Someone who wants
quiet music is not served by a metal track no matter how well the energy lines up,
while mood separates two songs that are equally energetic but feel nothing alike.

**Ranking rule.** Scoring happens one song at a time, with no knowledge of the
others. Ranking is the second step: all twenty scores get sorted and the top five
are returned. A number like 2.87 means very little until it sits next to the rest
of the list, which is why the two steps stay apart. This ordering is the prediction
the whole system produces; there is nothing else.

The starter code returned the first five rows of the CSV with no scoring at all.
The finished version scores every song, records the points awarded for each pick,
and ranks the results.

---

## 4. Data

The catalog holds 20 songs across 16 genres and 15 moods.

Ten rows came with the course starter file. I added ten more because the original
set had two clear holes: nothing between 0.45 and 0.75 energy, and no j-pop, anime
rock, classical, cinematic, dream pop, edm, R&B or mandopop at all. All ten
additions came from my own playlist, which is mostly j-pop, piano and soundtrack
music, so the catalog now leans toward my own taste.

The energy, valence, danceability and acousticness values are hand-assigned
estimates of how each track feels, not measurements from an audio API. They are
consistent with each other, but they are my judgement rather than data.

What the dataset does not contain:

- Lyrics, language, era, or release year
- Popularity, or how often a song gets skipped
- Artist as a scored feature (the artist name is stored but never used)
- Independence between features: most calm songs are also low energy, so genre,
  mood and energy partly measure the same thing

---

## 5. Strengths

- **Extreme targets behave correctly.** Because energy is scored by distance
  rather than height, a listener who wants calm gets the quietest tracks and a
  listener who wants intensity gets the loudest ones. A "higher is better" rule
  would have failed half the users.
- **Clear matches are found and ranked sensibly.** For the Chill Lofi profile the
  top three are the three lofi tracks (3.95, 3.88, 2.90), in the order I would
  have picked by hand. For Intense Rock the top pick scores 3.99 of 4.00.
- **Every result can be explained.** Each score reads back as a short list of
  points awarded ("genre +2.0, mood +0.0, energy +0.98"). There is no moment where
  a song appears for no stated reason.
- **The same recipe runs in two places.** The class version and the function
  version share the weights, so the CLI output and the tests agree on how a song
  is scored.
- **The weights are adjustable in one place.** The comparison experiments in the
  README only needed the three weight values changed, with no rewrite of the logic.

---

## 6. Limitations and Bias

The clearest weakness is that a genre match is worth 2.0 and nothing else comes
close: a user who asks for euphoric 0.90-energy classical music is handed
Gymnopédie No.1, a calm piano piece at energy 0.12, purely because its genre tag
matches. On the other side of the same problem, a user who is not in the catalog
at all gets a list ordered almost entirely by energy, which is why Intense Rock
falls back to pop and edm tracks rather than saying "I have nothing like this".
The dataset makes this worse, because 13 of the 16 genres appear exactly once,
lofi alone accounts for 3 songs, and half the catalog sits below 0.45 energy.
Some moods are tied to a single genre, so `calm` only exists on a classical track
and `energetic` only on j-pop, which means a calm j-pop listener can never be
matched and is served energetic songs instead. Finally, the system has no notion
of diversity or repetition: the same lofi tracks win every quiet request, and
nothing prevents five near-duplicates from filling the whole list.

---

## 7. Evaluation

I tested five profiles: High-Energy Pop (`pop / happy / 0.85`), Chill Lofi
(`lofi / chill / 0.30`), Intense Rock (`rock / intense / 0.90`), J-Pop Calm
(`j-pop / calm / 0.40`), and one impossible combination
(`classical / euphoric / 0.90`) built on purpose to be unsatisfiable.

For each one I checked four things: whether the top result was the song I would
have picked by hand, whether every score could be traced back to the rules, whether
songs from outside the target genre appeared for a reason, and whether the energy
ordering moved in the right direction when I changed the target.

What surprised me most was the impossible profile. I expected a weak answer and
got Gymnopédie No.1 at 2.22, ahead of every other song in the catalog, including
the ones that matched the energy request. The second surprise was J-Pop Calm: it
returned two energetic j-pop songs before reaching a genuinely calm track, because
both j-pop entries are tagged `energetic`. That is a data gap that looks exactly
like a scoring bug from the outside.

I ran two comparisons. Halving genre to 1.0 and doubling energy to 2.0 kept the
ranking order but collapsed the gaps, with Rooftop Lights rising from 1.91 to 2.82
and almost catching Gym Hero at 2.84. Removing the mood term entirely dropped
Rooftop Lights from rank 3 to rank 5 while leaving Gym Hero untouched, which showed
that the mood points only matter for songs whose genre is already wrong.

---

## 8. Future Work

- **Diversity penalty.** If an artist or genre already appears in the top five,
  subtract points from later entries. Quiet requests currently return the same
  three lofi tracks every time.
- **A way to refuse.** When the best score falls below a threshold, return fewer
  songs or say "nothing here matches that" instead of five weak answers. The
  impossible profile is the case this would fix.
- **A feedback loop.** Let a listener reject a song and nudge the weights, instead
  of typing three numbers up front and never touching them again.
- **Use the data that is already there.** Valence, tempo, danceability and
  acousticness are loaded into every song but never scored. Acousticness alone
  would separate the electronic and orchestral tracks that currently tie.
- **Replace the estimate with a measurement.** Pull real audio features from an
  API so the scores rest on data rather than my own judgement of each track.

---

## 9. Personal Reflection

What I did not expect: cutting the genre weight in half barely moved the ranking
order, it just squeezed the gaps, while deleting the mood term dropped one song
four places. A weight I assumed was structural turned out to matter less than a
weight I thought was decoration. And a genre tag worth 2.0 is enough to outvote a
wrong mood and a wrong energy at the same time, which explains how easy it is to
end up cycling the same few songs.

If I kept going, I would make the system able to return nothing. Right now it
always answers, and a recommender that always answers is claiming more confidence
than it has.
