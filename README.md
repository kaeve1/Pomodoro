# pomoDojo

Gerador programático de vídeos de estudo no estilo Pomodoro. O projeto produz vídeos completos, com imagem e som, sem nenhuma edição manual: você descreve as sessões em um arquivo JSON, roda um comando, e recebe um MP4 pronto para publicar. Cada frame e cada trecho de áudio são gerados por código, do countdown inicial ao ruído ambiente de fundo.

Este documento explica o que o projeto faz, como o pipeline funciona por dentro e como executá-lo, para que qualquer pessoa entenda cada etapa antes de rodar.

## O que ele faz

Vídeos de Pomodoro para estudo, aqueles com um cronômetro de foco e pausa acompanhado de ruído ambiente, costumam ser feitos manualmente em editores de vídeo, o que é repetitivo e demorado. O pomoDojo elimina esse trabalho: ele desenha o cronômetro quadro a quadro, sintetiza o áudio inteiro em código e monta o vídeo final automaticamente.

Você define quantos vídeos quiser em um JSON, cada um com duração de foco, duração de pausa, número de ciclos, cores e tipo de ruído. O programa percorre a lista e gera cada vídeo do começo ao fim, um após o outro.

## Como o pipeline funciona

O orquestrador é o `generateVideos.py`. Ele lê a lista de vídeos, e para cada um prepara as variáveis, limpa arquivos temporários e executa cinco etapas em sequência, cada uma num script próprio dentro de `src/`. As configurações de cada vídeo são passadas para as etapas através de variáveis de ambiente, o que mantém cada script independente e executável isoladamente.

```
videos.json → generateVideos.py
                ├── makeIntro.py   → countdown animado de abertura
                ├── makeFrames.py  → frames do cronômetro (foco e pausa)
                ├── makeAudio.py   → ruído ambiente e tick-tock, gerados em código
                ├── makeOutro.py   → tela final
                └── makeVideo.py   → montagem final com FFmpeg → .mp4
```

**Intro.** Gera um countdown animado de dez segundos a trinta quadros por segundo. Um arco circular vai se preenchendo a cada segundo enquanto o número decresce, e ao final aparece uma mensagem motivacional sorteada de uma lista. As cores vêm da configuração do vídeo.

**Frames do cronômetro.** Esta é a etapa mais pesada. Desenha a tela principal, dividida ao meio entre foco e pausa, cada lado com seu título, ícone, círculo de progresso e cronômetro numérico. A cada segundo de vídeo são trinta quadros, então uma sessão longa pode significar dezenas de milhares de imagens. Para dar conta disso em tempo razoável, os quadros são gerados em paralelo com multiprocessing, distribuindo o trabalho entre vários processos e acompanhando o progresso por um contador compartilhado. As transições entre foco e pausa também são animadas.

**Áudio.** Todo o som é sintetizado, não gravado. O ruído ambiente de fundo é gerado matematicamente através de filtros digitais, e o projeto oferece vários tipos de ruído colorido, cada um com uma característica sonora diferente: branco, rosa, marrom, azul, violeta, cinza e verde. Sobre esse fundo, o script adiciona um tick-tock sintetizado na contagem final de cada fase, com ênfase e eco nos últimos segundos para marcar a virada. Um som de transição suave toca nos momentos de troca entre foco e pausa. Toda a linha do tempo do áudio é montada para casar exatamente com a duração dos quadros.

**Outro.** Gera a tela de encerramento a partir de uma arte sobreposta, recolorida conforme o tema do vídeo.

**Montagem.** A última etapa usa o FFmpeg para transformar cada conjunto de quadros em um clipe de vídeo, concatenar intro, corpo e outro em um único arquivo, e por fim casar esse vídeo com a trilha de áudio gerada. Os arquivos intermediários são sempre limpos ao final, mesmo se ocorrer um erro no meio do caminho.

## Tecnologias

* Python, para geração dos quadros, síntese de áudio e orquestração do pipeline
* Pillow, para desenhar os quadros, textos, ícones e círculos de progresso
* NumPy e SciPy, para gerar e filtrar o ruído ambiente
* pydub, para montar e aplicar efeitos na trilha de áudio
* FFmpeg, para codificar e montar o vídeo final
* multiprocessing, da biblioteca padrão, para gerar os quadros em paralelo

## Estrutura de pastas

```
generateVideos.py     Orquestrador: lê o JSON e roda o pipeline por vídeo
videos.json           Definição dos vídeos a gerar
config.json           Resolução, fontes, ícones e som de transição
src/
  makeIntro.py        Countdown animado de abertura
  makeFrames.py       Frames do cronômetro (paralelizado)
  makeAudio.py        Síntese de ruído e tick-tock
  makeOutro.py        Tela final
  makeVideo.py        Montagem final via FFmpeg
assets/
  fonts/              Fontes usadas nos textos
  icons/              Ícones de foco e pausa
  audios/             Som de transição
```

## Como rodar

Pré-requisitos: Python instalado e FFmpeg disponível no PATH do sistema.

Clone o repositório e entre na pasta:

```
git clone https://github.com/kaeve1/Pomodoro.git
cd Pomodoro
```

Crie um ambiente virtual e instale as dependências:

```
python -m venv venv
venv\Scripts\activate
pip install pillow pydub numpy scipy
```

Defina os vídeos que deseja gerar no arquivo `videos.json`, dentro da lista `videos`. Cada item aceita:

```json
{
  "nome": "pomodoro_2h_25_5_pink",
  "focus": 1500,
  "break": 300,
  "focus_color": "#FFC2C2",
  "break_color": "#FFE6E6",
  "ciclos": 4,
  "noise": "pink"
}
```

O campo `focus` e `break` são durações em segundos, `ciclos` é quantas vezes a sessão se repete, `focus_color` e `break_color` definem o tema visual, e `noise` escolhe o tipo de ruído de fundo entre branco, rosa (`pink`), marrom (`brown`), azul (`blue`), violeta (`violet`), cinza (`grey`) e verde (`green`).

Por convenção, o nome do vídeo segue o formato `pomodoro_{duração}h_{foco}_{pausa}_{noise}`.

Rode o gerador:

```
python generateVideos.py
```

Cada vídeo finalizado é salvo em `output/videos/{nome}.mp4`.

## Configuração

O `config.json` controla a resolução, as fontes, os ícones de foco e pausa e o som de transição.

Um ponto importante para quem for rodar em outra máquina: os scripts foram escritos para gravar os quadros temporários em um drive secundário, no caminho `E:\PomodojoFrames`, para não ocupar o disco principal durante a geração. Esse caminho está definido diretamente no código, em `generateVideos.py`, `makeFrames.py`, `makeIntro.py`, `makeOutro.py` e `makeVideo.py`. Se você não tiver esse drive, ajuste esse caminho nesses arquivos para uma pasta que exista no seu sistema antes de rodar.

## Licença

MIT.
