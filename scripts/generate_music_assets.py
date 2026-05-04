#!/usr/bin/env python3
"""Generate small looping music assets for Korea Art Clock.

The classical loops are simple synthesized interpretations of public-domain
melodies/progressions. Nature tracks are procedural noise, so the site does
not depend on third-party audio hotlinks or modern copyrighted recordings.
"""

from __future__ import annotations

import json
import math
import random
import shutil
import struct
import wave
from pathlib import Path


SAMPLE_RATE = 22050
MAX_AMP = 32767
OUT_DIR = Path("assets/music")
MANIFEST = Path("assets/music.js")

NOTE_OFFSETS = {
    "C": 0,
    "C#": 1,
    "DB": 1,
    "D": 2,
    "D#": 3,
    "EB": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "GB": 6,
    "G": 7,
    "G#": 8,
    "AB": 8,
    "A": 9,
    "A#": 10,
    "BB": 10,
    "B": 11,
}


def main() -> int:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    tracks = [
        make_ode_to_joy(),
        make_fur_elise(),
        make_bach_prelude(),
        make_pachelbel_canon(),
        make_gymnopedie(),
        make_chopin_nocturne(),
        make_evangelion_piano(),
        make_gurenge_piano(),
        make_unravel_piano(),
        make_blue_bird_piano(),
        make_butter_fly_piano(),
        make_tank_piano(),
        make_one_summers_day_piano(),
        *make_healing_anime_piano_tracks(),
        make_rain_night(),
        make_ocean_waves(),
    ]

    for track in tracks:
        path = OUT_DIR / f"{track['id']}.wav"
        write_wav(path, track.pop("_samples"))
        track["sources"] = [{"src": f"assets/music/{path.name}", "type": "audio/wav"}]

    write_manifest(tracks)
    total = sum(path.stat().st_size for path in OUT_DIR.glob("*.wav"))
    print(f"Wrote {len(tracks)} tracks, {total / 1024 / 1024:.2f} MB")
    return 0


def make_buffer(seconds: float) -> list[float]:
    return [0.0] * int(seconds * SAMPLE_RATE)


def freq(note: str) -> float:
    note = note.strip().upper()
    name = note[:-1]
    octave = int(note[-1])
    midi = 12 * (octave + 1) + NOTE_OFFSETS[name]
    return 440.0 * (2 ** ((midi - 69) / 12))


def envelope(pos: float, duration: float, attack: float = 0.018, release: float = 0.12) -> float:
    if pos < attack:
        return pos / attack
    if pos > duration - release:
        return max(0.0, (duration - pos) / release)
    return 1.0


def tone(phase: float, shape: str) -> float:
    if shape == "soft":
        return math.sin(phase) + 0.22 * math.sin(2 * phase) + 0.08 * math.sin(3 * phase)
    if shape == "bell":
        return math.sin(phase) + 0.38 * math.sin(2.01 * phase) + 0.16 * math.sin(3.99 * phase)
    if shape == "pad":
        return math.sin(phase) + 0.18 * math.sin(0.5 * phase)
    return math.sin(phase)


def add_note(
    samples: list[float],
    note: str,
    start: float,
    duration: float,
    amp: float = 0.18,
    shape: str = "soft",
) -> None:
    frequency = freq(note)
    start_i = int(start * SAMPLE_RATE)
    end_i = min(len(samples), int((start + duration) * SAMPLE_RATE))
    for i in range(start_i, end_i):
        t = (i - start_i) / SAMPLE_RATE
        samples[i] += amp * envelope(t, duration) * tone(2 * math.pi * frequency * t, shape)


def add_chord(samples: list[float], notes: list[str], start: float, duration: float, amp: float = 0.08) -> None:
    for note in notes:
        add_note(samples, note, start, duration, amp / max(1, len(notes) ** 0.5), "pad")


def add_broken_chord(
    samples: list[float],
    notes: list[str],
    start: float,
    duration: float,
    step: float = 0.24,
    amp: float = 0.09,
) -> None:
    time = start
    index = 0
    while time < start + duration:
        add_note(samples, notes[index % len(notes)], time, min(step * 1.75, start + duration - time), amp, "soft")
        time += step
        index += 1


def add_delay(samples: list[float], delay: float = 0.22, decay: float = 0.22) -> None:
    offset = int(delay * SAMPLE_RATE)
    for i in range(offset, len(samples)):
        samples[i] += samples[i - offset] * decay


def normalize(samples: list[float], peak: float = 0.88) -> list[float]:
    max_value = max(0.0001, max(abs(sample) for sample in samples))
    gain = peak / max_value
    return [max(-0.98, min(0.98, sample * gain)) for sample in samples]


def write_wav(path: Path, samples: list[float]) -> None:
    samples = normalize(samples)
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(SAMPLE_RATE)
        frames = b"".join(struct.pack("<h", int(sample * MAX_AMP)) for sample in samples)
        out.writeframes(frames)


def make_ode_to_joy() -> dict[str, object]:
    melody = [
        ("E4", 0.5), ("E4", 0.5), ("F4", 0.5), ("G4", 0.5),
        ("G4", 0.5), ("F4", 0.5), ("E4", 0.5), ("D4", 0.5),
        ("C4", 0.5), ("C4", 0.5), ("D4", 0.5), ("E4", 0.5),
        ("E4", 0.75), ("D4", 0.25), ("D4", 1.0),
    ]
    chords = [["C3", "E3", "G3"], ["G2", "D3", "G3"], ["A2", "E3", "A3"], ["G2", "D3", "G3"]]
    samples = make_buffer(32)
    time = 0.0
    for repeat in range(4):
        for chord_index, chord in enumerate(chords):
            add_chord(samples, chord, repeat * 8 + chord_index * 2, 2.0, 0.085)
        for note, duration in melody:
            add_note(samples, note, time, duration * 0.96, 0.16, "soft")
            time += duration
    add_delay(samples)
    return track("ode-to-joy-loop", "Ode to Joy Loop", "Ludwig van Beethoven", "클래식", samples)


def make_fur_elise() -> dict[str, object]:
    motif = [
        ("E5", 0.24), ("D#5", 0.24), ("E5", 0.24), ("D#5", 0.24), ("E5", 0.24),
        ("B4", 0.24), ("D5", 0.24), ("C5", 0.24), ("A4", 0.72),
        ("C4", 0.24), ("E4", 0.24), ("A4", 0.24), ("B4", 0.72),
        ("E4", 0.24), ("G#4", 0.24), ("B4", 0.24), ("C5", 0.72),
    ]
    samples = make_buffer(34)
    time = 0.0
    while time < 32:
        for note, duration in motif:
            add_note(samples, note, time, duration * 0.92, 0.15, "bell")
            time += duration
        time += 0.24
    add_delay(samples, 0.18, 0.18)
    return track("fur-elise-loop", "Für Elise Loop", "Ludwig van Beethoven", "클래식", samples)


def make_bach_prelude() -> dict[str, object]:
    patterns = [
        ["C3", "E3", "G3", "C4", "E4", "G4", "C4", "G3"],
        ["A2", "E3", "A3", "C4", "E4", "A4", "E4", "C4"],
        ["F2", "C3", "F3", "A3", "C4", "F4", "C4", "A3"],
        ["G2", "D3", "G3", "B3", "D4", "G4", "D4", "B3"],
    ]
    samples = make_buffer(40)
    time = 0.0
    for _ in range(5):
        for pattern in patterns:
            for note in pattern:
                add_note(samples, note, time, 0.28, 0.12, "soft")
                time += 0.25
    add_delay(samples, 0.26, 0.2)
    return track("bach-prelude-loop", "Prelude in C Loop", "Johann Sebastian Bach", "클래식", samples)


def make_pachelbel_canon() -> dict[str, object]:
    chords = [
        ["D3", "F#3", "A3"], ["A2", "E3", "A3"], ["B2", "D3", "F#3"], ["F#2", "C#3", "F#3"],
        ["G2", "D3", "G3"], ["D3", "F#3", "A3"], ["G2", "D3", "G3"], ["A2", "E3", "A3"],
    ]
    samples = make_buffer(48)
    time = 0.0
    for _ in range(3):
        for chord in chords:
            add_chord(samples, chord, time, 2.0, 0.11)
            for offset, note in enumerate(chord + chord[::-1]):
                add_note(samples, note, time + offset * 0.25, 0.32, 0.1, "bell")
            time += 2.0
    add_delay(samples, 0.32, 0.24)
    return track("pachelbel-canon-loop", "Canon Progression Loop", "Johann Pachelbel", "클래식", samples)


def make_gymnopedie() -> dict[str, object]:
    chords = [["G2", "B3", "D4", "F#4"], ["D2", "A3", "C4", "F#4"], ["E2", "G3", "B3", "D4"], ["C2", "G3", "B3", "E4"]]
    melody = ["B4", "A4", "G4", "D4", "E4", "G4", "F#4", "D4"]
    samples = make_buffer(48)
    time = 0.0
    for repeat in range(3):
        for i, chord in enumerate(chords):
            add_chord(samples, chord, time, 4.0, 0.09)
            add_note(samples, melody[(repeat * 4 + i) % len(melody)], time + 0.8, 2.4, 0.13, "soft")
            time += 4.0
    add_delay(samples, 0.42, 0.3)
    return track("gymnopedie-loop", "Gymnopédie-Style Loop", "Erik Satie", "클래식", samples)


def make_chopin_nocturne() -> dict[str, object]:
    left = [["Eb2", "Bb2", "G3"], ["Bb1", "F2", "Ab3"], ["C2", "G2", "Eb3"], ["Ab1", "Eb2", "C3"]]
    melody = ["G4", "F4", "Eb4", "Bb4", "Ab4", "G4", "F4", "Eb4", "C5", "Bb4", "Ab4", "G4"]
    samples = make_buffer(48)
    time = 0.0
    melody_index = 0
    for _ in range(4):
        for chord in left:
            add_chord(samples, chord, time, 3.0, 0.1)
            add_note(samples, melody[melody_index % len(melody)], time + 0.3, 1.1, 0.13, "bell")
            add_note(samples, melody[(melody_index + 1) % len(melody)], time + 1.45, 1.1, 0.1, "soft")
            melody_index += 2
            time += 3.0
    add_delay(samples, 0.36, 0.28)
    return track("chopin-nocturne-loop", "Nocturne-Style Loop", "Frédéric Chopin", "클래식", samples)


def make_evangelion_piano() -> dict[str, object]:
    chords = [
        ["C3", "Eb3", "G3"], ["Ab2", "Eb3", "C4"], ["Bb2", "F3", "D4"], ["G2", "D3", "Bb3"],
        ["C3", "G3", "Eb4"], ["F2", "C3", "Ab3"], ["Bb2", "F3", "D4"], ["G2", "D3", "B3"],
    ]
    melody = ["G4", "C5", "Bb4", "G4", "Eb5", "D5", "C5", "Bb4", "C5", "G4", "Ab4", "Bb4", "C5", "D5", "Eb5", "D5"]
    samples = make_anime_piano_loop(chords, melody, 0.38, 4)
    return anime_track("anime-evangelion-piano", "A Cruel Angel's Thesis Piano Tribute", "Neon Genesis Evangelion", samples)


def make_gurenge_piano() -> dict[str, object]:
    chords = [
        ["D3", "F3", "A3"], ["Bb2", "F3", "D4"], ["C3", "G3", "E4"], ["A2", "E3", "C4"],
        ["D3", "A3", "F4"], ["G2", "D3", "Bb3"], ["C3", "G3", "E4"], ["A2", "E3", "C#4"],
    ]
    melody = ["D5", "F5", "E5", "D5", "A4", "C5", "D5", "E5", "F5", "E5", "D5", "C5", "A4", "D5", "E5", "F5"]
    samples = make_anime_piano_loop(chords, melody, 0.32, 4)
    return anime_track("anime-gurenge-piano", "Gurenge Piano Tribute", "Demon Slayer: Kimetsu no Yaiba", samples)


def make_unravel_piano() -> dict[str, object]:
    chords = [
        ["E3", "G3", "B3"], ["C3", "G3", "E4"], ["D3", "A3", "F#4"], ["B2", "F#3", "D4"],
        ["E3", "B3", "G4"], ["A2", "E3", "C4"], ["D3", "A3", "F#4"], ["B2", "F#3", "D#4"],
    ]
    melody = ["E5", "B4", "G4", "B4", "D5", "E5", "F#5", "E5", "D5", "B4", "A4", "B4", "D5", "E5", "G5", "F#5"]
    samples = make_anime_piano_loop(chords, melody, 0.34, 4)
    return anime_track("anime-unravel-piano", "Unravel Piano Tribute", "Tokyo Ghoul", samples)


def make_blue_bird_piano() -> dict[str, object]:
    chords = [
        ["G3", "B3", "D4"], ["D3", "A3", "F#4"], ["E3", "B3", "G4"], ["C3", "G3", "E4"],
        ["G3", "D4", "B4"], ["D3", "A3", "F#4"], ["C3", "G3", "E4"], ["D3", "A3", "F#4"],
    ]
    melody = ["B4", "D5", "E5", "D5", "G5", "F#5", "E5", "D5", "B4", "A4", "G4", "A4", "B4", "D5", "E5", "D5"]
    samples = make_anime_piano_loop(chords, melody, 0.36, 4)
    return anime_track("anime-blue-bird-piano", "Blue Bird Piano Tribute", "Naruto Shippuden", samples)


def make_butter_fly_piano() -> dict[str, object]:
    chords = [
        ["C3", "E3", "G3"], ["G2", "D3", "B3"], ["A2", "E3", "C4"], ["F2", "C3", "A3"],
        ["C3", "G3", "E4"], ["G2", "D3", "B3"], ["F2", "C3", "A3"], ["G2", "D3", "B3"],
    ]
    melody = ["E4", "G4", "C5", "B4", "A4", "G4", "E4", "G4", "A4", "C5", "D5", "C5", "B4", "G4", "A4", "B4"]
    samples = make_anime_piano_loop(chords, melody, 0.35, 4)
    return anime_track("anime-butter-fly-piano", "Butter-Fly Piano Tribute", "Digimon Adventure", samples)


def make_tank_piano() -> dict[str, object]:
    chords = [
        ["C3", "Eb3", "G3", "Bb3"], ["F2", "Eb3", "A3", "C4"], ["C3", "Eb3", "G3", "Bb3"], ["G2", "F3", "B3", "D4"],
        ["C3", "G3", "Bb3", "Eb4"], ["Ab2", "Eb3", "G3", "C4"], ["D3", "A3", "C4", "F#4"], ["G2", "D3", "F3", "B3"],
    ]
    melody = ["C5", "Eb5", "G5", "Bb4", "C5", "G4", "F4", "Eb4", "G4", "Bb4", "C5", "Eb5", "D5", "C5", "Bb4", "G4"]
    samples = make_anime_piano_loop(chords, melody, 0.26, 5, swing=True)
    return anime_track("anime-tank-piano", "Tank! Piano Jazz Tribute", "Cowboy Bebop", samples)


def make_one_summers_day_piano() -> dict[str, object]:
    chords = [
        ["A2", "E3", "C#4"], ["E2", "B2", "G#3"], ["F#2", "C#3", "A3"], ["D2", "A2", "F#3"],
        ["A2", "E3", "C#4"], ["C#3", "G#3", "E4"], ["D3", "A3", "F#4"], ["E3", "B3", "G#4"],
    ]
    melody = ["E5", "C#5", "A4", "B4", "C#5", "E5", "F#5", "E5", "C#5", "B4", "A4", "B4", "C#5", "B4", "A4", "E4"]
    samples = make_anime_piano_loop(chords, melody, 0.48, 3)
    return anime_track("anime-one-summers-day-piano", "One Summer's Day Piano Tribute", "Spirited Away", samples)


HEALING_ANIME_PIANO_TRACKS = [
    {
        "id": "anime-merry-go-round-life-piano",
        "title": "Merry-Go-Round of Life Piano Tribute",
        "series": "Howl's Moving Castle",
        "beat": 0.44,
        "repeats": 3,
        "chords": [
            ["G2", "D3", "B3"], ["B2", "F#3", "D4"], ["E3", "B3", "G4"], ["C3", "G3", "E4"],
            ["A2", "E3", "C4"], ["D3", "A3", "F#4"], ["G2", "D3", "B3"], ["D3", "A3", "C4"],
        ],
        "melody": ["B4", "D5", "G5", "F#5", "E5", "D5", "B4", "A4", "G4", "B4", "D5", "E5", "D5", "B4", "A4", "G4"],
    },
    {
        "id": "anime-ocean-view-town-piano",
        "title": "A Town with an Ocean View Piano Tribute",
        "series": "Kiki's Delivery Service",
        "beat": 0.4,
        "repeats": 3,
        "chords": [
            ["C3", "E3", "G3"], ["G2", "D3", "B3"], ["A2", "E3", "C4"], ["E2", "B2", "G3"],
            ["F2", "C3", "A3"], ["C3", "G3", "E4"], ["D3", "A3", "F4"], ["G2", "D3", "B3"],
        ],
        "melody": ["E5", "G5", "E5", "D5", "C5", "D5", "E5", "G5", "A5", "G5", "E5", "D5", "C5", "E5", "D5", "C5"],
    },
    {
        "id": "anime-path-of-wind-piano",
        "title": "Path of the Wind Piano Tribute",
        "series": "My Neighbor Totoro",
        "beat": 0.5,
        "repeats": 3,
        "chords": [
            ["F2", "C3", "A3"], ["C3", "G3", "E4"], ["D3", "A3", "F4"], ["Bb2", "F3", "D4"],
            ["F2", "C3", "A3"], ["A2", "E3", "C4"], ["Bb2", "F3", "D4"], ["C3", "G3", "E4"],
        ],
        "melody": ["A4", "C5", "F5", "E5", "D5", "C5", "A4", "G4", "A4", "C5", "D5", "F5", "E5", "C5", "A4", "G4"],
    },
    {
        "id": "anime-ashitaka-san-piano",
        "title": "Ashitaka and San Piano Tribute",
        "series": "Princess Mononoke",
        "beat": 0.56,
        "repeats": 3,
        "chords": [
            ["D2", "A2", "F3"], ["Bb2", "F3", "D4"], ["C3", "G3", "E4"], ["A2", "E3", "C4"],
            ["D2", "A2", "F3"], ["G2", "D3", "Bb3"], ["Bb2", "F3", "D4"], ["A2", "E3", "C#4"],
        ],
        "melody": ["A4", "D5", "F5", "E5", "D5", "C5", "A4", "F4", "G4", "A4", "C5", "D5", "F5", "E5", "D5", "A4"],
    },
    {
        "id": "anime-sincerely-piano",
        "title": "Sincerely Piano Tribute",
        "series": "Violet Evergarden",
        "beat": 0.42,
        "repeats": 3,
        "chords": [
            ["Eb3", "G3", "Bb3"], ["Bb2", "F3", "D4"], ["C3", "G3", "Eb4"], ["Ab2", "Eb3", "C4"],
            ["F2", "C3", "Ab3"], ["Bb2", "F3", "D4"], ["Eb3", "Bb3", "G4"], ["Ab2", "Eb3", "C4"],
        ],
        "melody": ["G4", "Bb4", "Eb5", "D5", "C5", "Bb4", "G4", "Ab4", "Bb4", "C5", "Eb5", "F5", "Eb5", "D5", "C5", "Bb4"],
    },
    {
        "id": "anime-michishirube-piano",
        "title": "Michishirube Piano Tribute",
        "series": "Violet Evergarden",
        "beat": 0.54,
        "repeats": 3,
        "chords": [
            ["A2", "E3", "C#4"], ["F#2", "C#3", "A3"], ["D3", "A3", "F#4"], ["E3", "B3", "G#4"],
            ["A2", "E3", "C#4"], ["C#3", "G#3", "E4"], ["F#2", "C#3", "A3"], ["D3", "A3", "F#4"],
        ],
        "melody": ["E5", "C#5", "A4", "C#5", "B4", "A4", "F#4", "A4", "B4", "C#5", "E5", "F#5", "E5", "C#5", "B4", "A4"],
    },
    {
        "id": "anime-sparkle-piano",
        "title": "Sparkle Piano Tribute",
        "series": "Your Name",
        "beat": 0.36,
        "repeats": 4,
        "chords": [
            ["D3", "A3", "F#4"], ["A2", "E3", "C#4"], ["B2", "F#3", "D4"], ["G2", "D3", "B3"],
            ["D3", "A3", "F#4"], ["A2", "E3", "C#4"], ["G2", "D3", "B3"], ["A2", "E3", "C#4"],
        ],
        "melody": ["F#5", "E5", "D5", "A4", "B4", "D5", "E5", "F#5", "A5", "F#5", "E5", "D5", "B4", "D5", "E5", "F#5"],
    },
    {
        "id": "anime-nandemonaiya-piano",
        "title": "Nandemonaiya Piano Tribute",
        "series": "Your Name",
        "beat": 0.48,
        "repeats": 3,
        "chords": [
            ["G2", "D3", "B3"], ["D3", "A3", "F#4"], ["E3", "B3", "G4"], ["C3", "G3", "E4"],
            ["G2", "D3", "B3"], ["B2", "F#3", "D4"], ["C3", "G3", "E4"], ["D3", "A3", "F#4"],
        ],
        "melody": ["B4", "A4", "G4", "D5", "E5", "D5", "B4", "A4", "G4", "B4", "D5", "E5", "D5", "B4", "A4", "G4"],
    },
    {
        "id": "anime-natsu-yuuzora-piano",
        "title": "Natsu Yuuzora Piano Tribute",
        "series": "Natsume's Book of Friends",
        "beat": 0.52,
        "repeats": 3,
        "chords": [
            ["C3", "G3", "E4"], ["G2", "D3", "B3"], ["A2", "E3", "C4"], ["E2", "B2", "G3"],
            ["F2", "C3", "A3"], ["C3", "G3", "E4"], ["F2", "C3", "A3"], ["G2", "D3", "B3"],
        ],
        "melody": ["G4", "C5", "E5", "D5", "C5", "B4", "A4", "G4", "A4", "C5", "D5", "E5", "D5", "C5", "A4", "G4"],
    },
    {
        "id": "anime-yasashisa-piano",
        "title": "Yasashisa ni Tsutsumareta Nara Piano Tribute",
        "series": "Kiki's Delivery Service",
        "beat": 0.42,
        "repeats": 3,
        "chords": [
            ["F2", "C3", "A3"], ["C3", "G3", "E4"], ["D3", "A3", "F4"], ["A2", "E3", "C4"],
            ["Bb2", "F3", "D4"], ["F2", "C3", "A3"], ["G2", "D3", "Bb3"], ["C3", "G3", "E4"],
        ],
        "melody": ["A4", "C5", "F5", "E5", "D5", "C5", "A4", "C5", "D5", "F5", "G5", "F5", "E5", "C5", "D5", "C5"],
    },
    {
        "id": "anime-always-with-me-piano",
        "title": "Always With Me Piano Tribute",
        "series": "Spirited Away",
        "beat": 0.5,
        "repeats": 3,
        "chords": [
            ["C3", "E3", "G3"], ["E2", "B2", "G3"], ["A2", "E3", "C4"], ["F2", "C3", "A3"],
            ["D3", "A3", "F4"], ["G2", "D3", "B3"], ["C3", "G3", "E4"], ["G2", "D3", "B3"],
        ],
        "melody": ["E5", "D5", "C5", "G4", "A4", "C5", "D5", "E5", "F5", "E5", "D5", "C5", "A4", "G4", "A4", "C5"],
    },
    {
        "id": "anime-sixth-station-piano",
        "title": "The Sixth Station Piano Tribute",
        "series": "Spirited Away",
        "beat": 0.62,
        "repeats": 3,
        "chords": [
            ["F2", "C3", "A3"], ["G2", "D3", "Bb3"], ["C3", "G3", "E4"], ["A2", "E3", "C4"],
            ["D3", "A3", "F4"], ["Bb2", "F3", "D4"], ["F2", "C3", "A3"], ["C3", "G3", "E4"],
        ],
        "melody": ["C5", "A4", "F4", "A4", "Bb4", "C5", "D5", "C5", "A4", "G4", "F4", "G4", "A4", "C5", "D5", "C5"],
    },
    {
        "id": "anime-lit-piano",
        "title": "Lit Piano Tribute",
        "series": "A Silent Voice",
        "beat": 0.5,
        "repeats": 3,
        "chords": [
            ["E3", "G3", "B3"], ["G2", "D3", "B3"], ["C3", "G3", "E4"], ["D3", "A3", "F#4"],
            ["E3", "B3", "G4"], ["C3", "G3", "E4"], ["A2", "E3", "C4"], ["B2", "F#3", "D4"],
        ],
        "melody": ["G4", "B4", "E5", "D5", "B4", "A4", "G4", "A4", "B4", "D5", "E5", "G5", "E5", "D5", "B4", "A4"],
    },
    {
        "id": "anime-secret-base-piano",
        "title": "Secret Base Piano Tribute",
        "series": "Anohana",
        "beat": 0.46,
        "repeats": 3,
        "chords": [
            ["D3", "A3", "F#4"], ["A2", "E3", "C#4"], ["B2", "F#3", "D4"], ["G2", "D3", "B3"],
            ["D3", "A3", "F#4"], ["F#2", "C#3", "A3"], ["G2", "D3", "B3"], ["A2", "E3", "C#4"],
        ],
        "melody": ["A4", "D5", "F#5", "E5", "D5", "C#5", "B4", "A4", "B4", "D5", "E5", "F#5", "E5", "D5", "B4", "A4"],
    },
    {
        "id": "anime-fukashigi-carte-piano",
        "title": "Fukashigi no Carte Piano Tribute",
        "series": "Rascal Does Not Dream of Bunny Girl Senpai",
        "beat": 0.44,
        "repeats": 3,
        "swing": True,
        "chords": [
            ["F2", "A2", "C3", "E3"], ["Bb2", "D3", "F3", "A3"], ["E2", "G#2", "B2", "D3"], ["A2", "C3", "E3", "G3"],
            ["D3", "F3", "A3", "C4"], ["G2", "B2", "D3", "F3"], ["C3", "E3", "G3", "B3"], ["C3", "E3", "G3", "Bb3"],
        ],
        "melody": ["A4", "C5", "E5", "D5", "C5", "A4", "G4", "A4", "Bb4", "C5", "D5", "E5", "D5", "C5", "A4", "G4"],
    },
    {
        "id": "anime-isabellas-lullaby-piano",
        "title": "Isabella's Lullaby Piano Tribute",
        "series": "The Promised Neverland",
        "beat": 0.58,
        "repeats": 3,
        "chords": [
            ["A2", "E3", "C4"], ["E2", "B2", "G3"], ["F2", "C3", "A3"], ["C3", "G3", "E4"],
            ["D3", "A3", "F4"], ["A2", "E3", "C4"], ["Bb2", "F3", "D4"], ["E2", "B2", "G#3"],
        ],
        "melody": ["E5", "C5", "A4", "C5", "B4", "A4", "F4", "A4", "C5", "D5", "E5", "D5", "C5", "A4", "G#4", "A4"],
    },
    {
        "id": "anime-kimi-shiranai-piano",
        "title": "Kimi no Shiranai Monogatari Piano Tribute",
        "series": "Bakemonogatari",
        "beat": 0.38,
        "repeats": 4,
        "chords": [
            ["G3", "B3", "D4"], ["D3", "A3", "F#4"], ["E3", "B3", "G4"], ["C3", "G3", "E4"],
            ["G3", "D4", "B4"], ["B2", "F#3", "D4"], ["C3", "G3", "E4"], ["D3", "A3", "F#4"],
        ],
        "melody": ["B4", "D5", "G5", "F#5", "E5", "D5", "B4", "A4", "G4", "A4", "B4", "D5", "E5", "D5", "B4", "G4"],
    },
]


def make_healing_anime_piano_tracks() -> list[dict[str, object]]:
    tracks = []
    for item in HEALING_ANIME_PIANO_TRACKS:
        samples = make_anime_piano_loop(
            item["chords"],
            item["melody"],
            item["beat"],
            item["repeats"],
            item.get("swing", False),
        )
        tracks.append(anime_track(item["id"], item["title"], item["series"], samples))
    return tracks


def make_anime_piano_loop(
    chords: list[list[str]],
    melody: list[str],
    beat: float,
    repeats: int,
    swing: bool = False,
) -> list[float]:
    bar = beat * 4
    samples = make_buffer(len(chords) * bar * repeats + 1.5)
    melody_index = 0
    for repeat in range(repeats):
        for chord_index, chord in enumerate(chords):
            start = (repeat * len(chords) + chord_index) * bar
            add_chord(samples, chord, start, bar, 0.075)
            add_broken_chord(samples, chord + chord[::-1], start, bar, beat / 2, 0.074)
            for step in range(2):
                note_start = start + step * beat * 2
                length = beat * (1.58 if not swing or step == 0 else 1.28)
                add_note(samples, melody[melody_index % len(melody)], note_start, length, 0.13, "bell")
                if swing:
                    add_note(samples, melody[(melody_index + 1) % len(melody)], note_start + beat * 0.72, beat * 0.75, 0.09, "soft")
                melody_index += 1
    add_delay(samples, 0.28 if not swing else 0.18, 0.24)
    return samples


def make_rain_night() -> dict[str, object]:
    rng = random.Random(20260503)
    samples = make_buffer(50)
    value = 0.0
    for i in range(len(samples)):
        value = value * 0.82 + rng.uniform(-0.16, 0.16)
        shimmer = rng.uniform(-0.03, 0.03)
        samples[i] = value * 0.25 + shimmer
    for _ in range(95):
        start = rng.uniform(0, 49)
        add_noise_drop(samples, start, rng.uniform(0.03, 0.12), rng.uniform(0.12, 0.28), rng)
    return track("rain-night-loop", "Rain at Night", "Procedural nature sound", "자연", samples)


def make_ocean_waves() -> dict[str, object]:
    rng = random.Random(20260504)
    samples = make_buffer(56)
    for i in range(len(samples)):
        t = i / SAMPLE_RATE
        swell = 0.5 + 0.5 * math.sin(2 * math.pi * t / 7.0)
        foam = rng.uniform(-1, 1) * (0.02 + 0.13 * swell)
        low = math.sin(2 * math.pi * 0.11 * t) * 0.18
        samples[i] = low + foam
    return track("ocean-waves-loop", "Slow Ocean Waves", "Procedural nature sound", "자연", samples)


def add_noise_drop(samples: list[float], start: float, duration: float, amp: float, rng: random.Random) -> None:
    start_i = int(start * SAMPLE_RATE)
    end_i = min(len(samples), int((start + duration) * SAMPLE_RATE))
    for i in range(start_i, end_i):
        pos = (i - start_i) / max(1, end_i - start_i)
        samples[i] += rng.uniform(-1, 1) * amp * (1 - pos)


def track(track_id: str, title: str, artist: str, mood: str, samples: list[float]) -> dict[str, object]:
    return {
        "id": track_id,
        "title": title,
        "artist": artist,
        "mood": mood,
        "license": "Project-generated; public-domain melody/procedural sound",
        "source": "Generated locally by scripts/generate_music_assets.py",
        "sourceUrl": "https://github.com/sungreong/korea-art-clock",
        "licenseUrl": "https://creativecommons.org/publicdomain/mark/1.0/",
        "_samples": samples,
    }


def anime_track(track_id: str, title: str, series: str, samples: list[float]) -> dict[str, object]:
    return {
        "id": track_id,
        "title": title,
        "artist": series,
        "mood": "애니 피아노",
        "license": "Project-generated piano tribute loop; no third-party recording",
        "source": "Generated locally by scripts/generate_music_assets.py",
        "sourceUrl": "https://github.com/sungreong/korea-art-clock",
        "licenseUrl": "https://github.com/sungreong/korea-art-clock",
        "_samples": samples,
    }


def write_manifest(tracks: list[dict[str, object]]) -> None:
    manifest = {
        "version": 2,
        "defaultTrack": "gymnopedie-loop",
        "tracks": tracks,
    }
    MANIFEST.write_text(
        "window.KOREA_ART_CLOCK_MUSIC = " + json.dumps(manifest, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
