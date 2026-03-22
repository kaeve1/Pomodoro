## Visão Geral

O pomoDojo gera vídeos de estudo completos de forma programática — sem edição de vídeo. Defina suas sessões em um arquivo JSON, execute um comando, receba um MP4 pronto para upload.

## Stack

- **Python** — geração de frames, síntese de áudio, orquestração do pipeline
- **Pillow** — renderização visual (frames, fontes, ícones)
- **NumPy / SciPy** — geração e filtragem de ruído ambiente
- **pydub** — montagem e efeitos de áudio
- **FFmpeg** — codificação do vídeo final

## Como Funciona

```
videos.json → generateVideos.py
                ├── makeIntro.py    # countdown animado de 10s (30fps)
                ├── makeFrames.py   # frames do timer (30fps, multiprocessing)
                ├── makeAudio.py    # ruído ambiente + tick-tock (gerado em código)
                ├── makeOutro.py    # tela final de 20s
                └── makeVideo.py   # montagem FFmpeg → .mp4
```

Os frames são escritos em um HD secundário para preservar o armazenamento principal. Arquivos temporários são limpos automaticamente após cada vídeo.

## Instalação

```bash
git clone https://github.com/youruser/PomodoroYouTube.git
cd PomodoroYouTube
python -m venv venv && venv\Scripts\activate
pip install pillow pydub numpy scipy moviepy
```

O FFmpeg deve estar instalado e disponível no PATH.

## Uso

Defina seus vídeos em `videos.json`:

```json
{
  "videos": [
    {
      "nome": "pomodoro_4h_50_10_pink",
      "focus": 3000,
      "break": 600,
      "focus_color": "#FFC2C2",
      "break_color": "#FFE6E6",
      "ciclos": 4,
      "noise": "pink"
    }
  ]
}
```

> **Convenção de nome:** `pomodoro_{duração}h_{focus}_{break}_{noise}`  
> **Tipos de noise:** `pink` `brown` `green` `white` `grey` `blue`

```bash
python generateVideos.py
```

Saída: `output/videos/{nome}.mp4`

## Configuração

`config.json` — resolução, fontes, ícones, caminho do som de transição.  
`src/makeFrames.py` — altere `OUTPUT_DIR` para o caminho do seu HD secundário.


## Visual
visite o meu canal no youtube que usa esta tecnologia -> https://www.youtube.com/@Pomo_Dojo
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/a73d4829-e053-4670-acb7-65d0049ecd0b" />

<img width="1918" height="1071" alt="image" src="https://github.com/user-attachments/assets/a08df6ae-3549-4348-820d-ebf626e398e7" />

<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/6943367b-a0d8-4354-9e46-b2f9a5683bdd" />






--------------------------------------------------------------------------------------------


## Overview

pomoDojo generates full-length study timer videos programmatically — no video editing required. Define your sessions in a JSON file, run one command, get a production-ready MP4.

## Stack

- **Python** — frame generation, audio synthesis, pipeline orchestration
- **Pillow** — visual rendering (frames, fonts, icons)
- **NumPy / SciPy** — ambient noise generation and filtering
- **pydub** — audio assembly and effects
- **FFmpeg** — final video encoding

## How It Works

```
videos.json → generateVideos.py
                ├── makeIntro.py    # 10s animated countdown (30fps)
                ├── makeFrames.py   # timer frames (30fps, multiprocessing)
                ├── makeAudio.py    # ambient noise + tick-tock (pure code)
                ├── makeOutro.py    # 20s end screen
                └── makeVideo.py   # FFmpeg assembly → .mp4
```

Frames are written to a secondary drive to preserve main storage. Temporary files are cleaned automatically after each video.

## Setup

```bash
git clone https://github.com/youruser/PomodoroYouTube.git
cd PomodoroYouTube
python -m venv venv && venv\Scripts\activate
pip install pillow pydub numpy scipy moviepy
```

FFmpeg must be installed and available in PATH.

## Usage

Define your videos in `videos.json`:

```json
{
  "videos": [
    {
      "nome": "pomodoro_4h_50_10_pink",
      "focus": 3000,
      "break": 600,
      "focus_color": "#FFC2C2",
      "break_color": "#FFE6E6",
      "ciclos": 4,
      "noise": "pink"
    }
  ]
}
```

> **File naming:** `pomodoro_{duration}h_{focus}_{break}_{noise}`  
> **Noise options:** `pink` `brown` `green` `white` `grey` `blue`

```bash
python generateVideos.py
```

Output: `output/videos/{nome}.mp4`

## Configuration

`config.json` — resolution, fonts, icons, transition sound path.  
`src/makeFrames.py` — set `OUTPUT_DIR` to your secondary drive path.


MIT License
