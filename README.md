music-to-dmx-light
==================

Synchronize your lighting fixtures with DJ software in real time
----------------------------------------------------------------

Python 3.11+ | License: MIT

Overview
--------

`music-to-dmx-light` is a Python-based real-time DMX lighting controller designed
to react to live music playback — similar in spirit to SoundSwitch, but
fully open, modular, and scriptable.

It connects music events (beats, bars, phrases) from Rekordbox (or other future
sources) to DMX lighting fixtures via Art-Net, with flexible YAML configuration,
an effect system, and custom fixture definitions.

Features
--------

- Beat detection from Rekordbox using OpenCV screen capture of waveform/playhead.
- Real-time engine built with asyncio and multiprocessing for accurate timing.
- DMX output via Art-Net (default: pyartnet).
- Modular architecture separating capture, core engine, fixtures, effects, and transport.
- Effect system with fades, priorities, HTP/LTP rules, and per-fixture control.
- YAML configuration for universes, fixture groups, and show profiles.
- Planned visualization integration (Blender/3D or OSC viewer).

Project Structure
-----------------

How It Works
------------

Layer            | Responsibility
-----------------|-------------------------------------------------------------
Capture (Rekordbox) | OpenCV detects playhead & beat grid markers. Emits TransportState.
Clock               | Maintains musical timing (beat, bar, phrase).
Event Bus           | Async pub/sub system distributing beat/transport events.
Scheduler           | Activates effects based on timing, computes parameter intents.
Arbitration         | Merges effects by HTP/LTP rules and priorities.
DMX Transport       | Sends frames at fixed FPS via Art-Net using pyartnet.
Fixtures            | Describe channel mappings and capabilities.
Effects             | Generate dynamic looks responding to beat, phase, and groups.

Quick Start
-----------

1. Clone and install dependencies:
   git clone https://github.com/vultorio67/music-to-dmx-light.git
   cd music-to-dmx-light
   python -m venv .venv
   source .venv/bin/activate  (or .venv\Scripts\activate on Windows)
   pip install -r requirements.txt

2. Configure your show:
   Edit configs/config.yaml and configs/zones.yaml to match your setup.

   Example:
   transport:
     type: artnet
     host: 255.255.255.255
   universes:
     - id: 0
       name: main
   fixtures:
     - id: left_1
       type: LyreSylvain
       universe: 0
       address: 1
   groups:
     left: ["left_1"]
     all: ["left_1"]

3. Run:
   python main.py

Development Notes
-----------------
- Requires Python 3.11+
- asyncio-based non-blocking DMX I/O
- multiprocessing for OpenCV screen-capture
- Logging via structlog
- Configuration validation with pydantic

Testing
-------
Run tests:
    pytest -q

Future Roadmap
---------------
- Blender / 3D visualization bridge (OSC)
- Fixture GDTF import/export
- Timeline editor (GUI)
- MIDI or Ableton Link input
- Web dashboard

Author
------
Developed by Vultorio
Repository: https://github.com/vultorio67/music-to-dmx-light

License
-------
MIT License — see LICENSE for details.

Maintenance
-----------
This README will be updated automatically when:
- new modules or effects are added,
- configuration formats change,
- or architecture evolves.

