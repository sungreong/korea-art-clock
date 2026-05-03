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
