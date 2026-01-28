# VoiceCode - Especificação de Requisitos

**Versão:** 1.0
**Data:** 2026-01-28
**Status:** MVP

---

## 1. Visão Geral

### 1.1 Objetivo
Desenvolver uma ferramenta de transcrição de voz para código no Windows, similar ao Wispr Flow/Superwhisper, mas open-source e DIY. A ferramenta permitirá ao usuário ditar instruções para assistentes de IA (Claude Code, Gemini CLI) de forma fluida, com processamento inteligente do texto.

### 1.2 Escopo
- **In Scope:** Transcrição de voz, limpeza de texto, formatação técnica, integração com clipboard, feedback visual/sonoro
- **Out of Scope:** Integração direta com IDEs, reconhecimento de comandos de sistema, múltiplos usuários

### 1.3 Usuário Alvo
Desenvolvedor que utiliza ferramentas de IA para programação (Claude Code, Gemini CLI) e deseja ditar instruções ao invés de digitar.

---

## 2. Ambiente Técnico

| Item | Especificação |
|------|---------------|
| Sistema Operacional | Windows 10 |
| Python | 3.11 (ambiente conda isolado) |
| GPU | NVIDIA RTX 3060 12GB VRAM |
| Microfone | Mesa (qualidade adequada) |
| Ferramentas de Destino | Claude Code, Gemini CLI |
| Linguagens de Trabalho | Python, TypeScript, React, Remotion |

---

## 3. Requisitos Funcionais

### 3.1 Captura de Áudio

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-01 | Suportar modo **Push-to-Talk** (grava enquanto tecla pressionada) | Alta |
| RF-02 | Suportar modo **Toggle** (tecla inicia, tecla para) | Alta |
| RF-03 | Permitir configuração da tecla de ativação via arquivo de config | Alta |
| RF-04 | Detectar e usar microfone padrão do sistema | Alta |
| RF-05 | Permitir seleção de microfone específico via config | Baixa |

### 3.2 Transcrição (Speech-to-Text)

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-06 | Suportar transcrição via **API Groq** (Whisper Large v3) | Alta |
| RF-07 | Suportar transcrição **local** (Whisper via faster-whisper) | Alta |
| RF-08 | Permitir escolha do backend (local/groq) via config | Alta |
| RF-09 | Suportar idioma **português** como principal | Alta |
| RF-10 | Suportar **inglês** para termos técnicos (mixed language) | Alta |

### 3.3 Processamento de Texto (Limpeza/Formatação)

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-11 | **Modo Raw:** Apenas transcrição sem processamento | Alta |
| RF-12 | **Modo Clean:** Remover palavras de preenchimento (hm, tipo, então, uh) | Alta |
| RF-13 | **Modo Tech:** Formatar termos técnicos (camelCase, snake_case, nomes de libs) | Alta |
| RF-14 | **Modo Full:** Aplicar Clean + Tech | Alta |
| RF-15 | Permitir **ciclar entre modos** com uma tecla dedicada | Alta |
| RF-16 | Suportar processamento via **LLM local** (Llama 3 8B via Ollama) | Média |
| RF-17 | Suportar processamento via **API Groq** (Llama 3) | Alta |
| RF-18 | Permitir escolha do backend de LLM (local/groq) via config | Alta |

### 3.4 Vocabulário Customizado

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-19 | Permitir definir lista de termos técnicos customizados via config | Média |
| RF-20 | Termos customizados devem ser priorizados na formatação | Média |

### 3.5 Context Injection

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-21 | Suportar modo **com contexto** via tecla modificadora (ex: Hotkey + Shift) | Alta |
| RF-22 | Quando ativado, incluir conteúdo do **clipboard** como contexto para o LLM | Alta |
| RF-23 | LLM deve entender referências como "isso", "esse erro", "esse código" | Alta |

### 3.6 Output

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-24 | Copiar texto final para o **clipboard** | Alta |
| RF-25 | Opção de **colar automaticamente** (simular Ctrl+V) | Alta |
| RF-26 | Permitir configurar comportamento de output (clipboard only / auto-paste) | Alta |

### 3.7 Histórico

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-27 | Salvar transcrições em arquivo de log | Média |
| RF-28 | Implementar **sliding window** (manter últimos N registros ou últimos N dias) | Média |
| RF-29 | Incluir timestamp e modo usado em cada registro | Média |

### 3.8 Feedback ao Usuário

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-30 | Exibir **ícone na system tray** | Alta |
| RF-31 | Ícone deve mudar de cor conforme estado (idle/gravando/processando) | Alta |
| RF-32 | Emitir **som** ao iniciar gravação | Alta |
| RF-33 | Emitir **som** ao finalizar processamento | Alta |
| RF-34 | Mostrar modo atual no tooltip do ícone da tray | Média |

### 3.9 Configuração

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-35 | Toda configuração via arquivo **YAML** | Alta |
| RF-36 | Hot-reload de configuração (sem reiniciar aplicação) | Baixa |

---

## 4. Requisitos Não-Funcionais

| ID | Requisito | Métrica |
|----|-----------|---------|
| RNF-01 | Latência total (fala → texto colado) | < 2s para frases curtas (via Groq) |
| RNF-02 | Latência local | < 3s para frases curtas (com GPU) |
| RNF-03 | Uso de VRAM (modo full local) | < 10GB |
| RNF-04 | Aplicação deve rodar em background | Consumo CPU idle < 1% |
| RNF-05 | Instalação isolada em ambiente conda | Não poluir sistema |

---

## 5. Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────────────┐
│                         VoiceCode                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Hotkey     │    │    Audio     │    │   System     │       │
│  │   Listener   │───▶│   Recorder   │    │    Tray      │       │
│  │  (keyboard)  │    │ (sounddevice)│    │  (pystray)   │       │
│  └──────────────┘    └──────┬───────┘    └──────────────┘       │
│                             │                                    │
│                             ▼                                    │
│                    ┌────────────────┐                           │
│                    │  Transcriber   │                           │
│                    │ ┌────────────┐ │                           │
│                    │ │   Groq     │ │                           │
│                    │ │    API     │ │                           │
│                    │ └────────────┘ │                           │
│                    │ ┌────────────┐ │                           │
│                    │ │  Local     │ │                           │
│                    │ │ (faster-   │ │                           │
│                    │ │  whisper)  │ │                           │
│                    │ └────────────┘ │                           │
│                    └───────┬────────┘                           │
│                            │                                     │
│                            ▼                                     │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────┐        │
│  │   Clipboard  │  │   Processor    │  │   History    │        │
│  │   (context)  │─▶│ ┌────────────┐ │─▶│    Logger    │        │
│  └──────────────┘  │ │  Groq LLM  │ │  └──────────────┘        │
│                    │ └────────────┘ │                           │
│                    │ ┌────────────┐ │                           │
│                    │ │ Local LLM  │ │                           │
│                    │ │  (Ollama)  │ │                           │
│                    │ └────────────┘ │                           │
│                    └───────┬────────┘                           │
│                            │                                     │
│                            ▼                                     │
│                    ┌────────────────┐                           │
│                    │    Output      │                           │
│                    │  (clipboard/   │                           │
│                    │   auto-paste)  │                           │
│                    └────────────────┘                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────┐
        │           config.yaml                   │
        │  - hotkeys                              │
        │  - backend (groq/local)                 │
        │  - mode (raw/clean/tech/full)           │
        │  - vocabulary                           │
        │  - output behavior                      │
        │  - history settings                     │
        └─────────────────────────────────────────┘
```

---

## 6. Fluxo Principal

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │     │ Record  │     │Transcribe│    │ Process │     │ Output  │
│ presses │────▶│  Audio  │────▶│  (STT)  │────▶│  (LLM)  │────▶│  Text   │
│ hotkey  │     │         │     │         │     │         │     │         │
└─────────┘     └─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │               │
     │          ┌────┴────┐          │          ┌────┴────┐          │
     │          │ Som de  │          │          │ Context │          │
     │          │ início  │          │          │Injection│          │
     │          └─────────┘          │          │(opcional)│         │
     │                               │          └─────────┘          │
     │                               │                               │
     │         ┌─────────────────────┴───────────────────────┐      │
     │         │              Tray Icon                       │      │
     │         │  🔴 Gravando → 🟡 Processando → 🟢 Pronto    │      │
     │         └─────────────────────────────────────────────┘      │
     │                                                               │
     └───────────────────────────────────────────────────────────────┘
                              Feedback Visual
```

---

## 7. Estrutura de Configuração (config.yaml)

```yaml
# VoiceCode Configuration

# === Hotkeys ===
hotkeys:
  activation_mode: "push_to_talk"  # push_to_talk | toggle
  main_key: "ctrl+shift+space"     # Tecla principal
  context_modifier: "alt"           # Adicionar para context injection
  cycle_mode_key: "ctrl+shift+m"   # Ciclar entre modos

# === Backend de Transcrição ===
transcription:
  backend: "groq"  # groq | local
  groq:
    api_key: "${GROQ_API_KEY}"  # Via variável de ambiente
    model: "whisper-large-v3"
  local:
    model: "large-v3"  # tiny | base | small | medium | large-v3
    device: "cuda"     # cuda | cpu

# === Backend de Processamento (LLM) ===
processing:
  backend: "groq"  # groq | local
  groq:
    model: "llama-3.1-8b-instant"
  local:
    model: "llama3:8b"  # Modelo do Ollama
    endpoint: "http://localhost:11434"

# === Modo de Formatação ===
mode: "full"  # raw | clean | tech | full

# === Vocabulário Customizado ===
vocabulary:
  - "Claude Code"
  - "Gemini CLI"
  - "TypeScript"
  - "Remotion"
  - "React"
  - "Next.js"
  - "FastAPI"
  - "Pydantic"
  - "useState"
  - "useEffect"

# === Output ===
output:
  behavior: "auto_paste"  # clipboard_only | auto_paste

# === Histórico ===
history:
  enabled: true
  max_entries: 1000        # Sliding window por quantidade
  file: "history.jsonl"

# === Feedback ===
feedback:
  sounds:
    enabled: true
    start: "sounds/start.wav"
    end: "sounds/end.wav"
  tray:
    show_mode_tooltip: true

# === Idiomas ===
language:
  primary: "pt"
  secondary: "en"  # Para termos técnicos
```

---

## 8. Estados do Sistema

| Estado | Ícone Tray | Descrição |
|--------|------------|-----------|
| **Idle** | ⚪ Cinza | Aguardando ativação |
| **Recording** | 🔴 Vermelho | Gravando áudio |
| **Processing** | 🟡 Amarelo | Transcrevendo/Processando |
| **Ready** | 🟢 Verde (2s) | Texto pronto e colado |
| **Error** | 🔴 Piscando | Erro no processamento |

---

## 9. Dependências Previstas

### Python Packages (conda/pip)
```
# Core
sounddevice        # Captura de áudio
numpy              # Manipulação de arrays de áudio
scipy              # Processamento de áudio (WAV)

# Transcrição
groq               # API Groq
faster-whisper     # Whisper local otimizado

# Sistema
keyboard           # Hotkeys globais (ou pynput)
pyperclip          # Clipboard
pystray            # System tray
Pillow             # Ícones para tray

# Config
pyyaml             # Arquivo de configuração

# Opcional (local LLM)
ollama             # Cliente Ollama (se usar local)
```

### Externos (se usar local)
- **Ollama** instalado no sistema (para LLM local)
- **CUDA Toolkit** compatível (para faster-whisper com GPU)

---

## 10. Critérios de Aceite do MVP

| # | Critério | Como Validar |
|---|----------|--------------|
| 1 | Pressionar hotkey inicia gravação | Som de início toca, ícone fica vermelho |
| 2 | Soltar hotkey processa áudio | Ícone fica amarelo, depois verde |
| 3 | Texto aparece onde cursor está | Texto colado no Claude Code/terminal |
| 4 | Modo "full" formata termos técnicos | "camel case function" → "camelCase function" |
| 5 | Context injection funciona | Copiar erro + falar "conserte isso" inclui o erro |
| 6 | Ciclar modos funciona | Tecla muda modo, tooltip atualiza |
| 7 | Histórico salva transcrições | Arquivo history.jsonl contém registros |
| 8 | Config YAML é respeitada | Mudar config altera comportamento |

---

## 11. Fora do Escopo (MVP)

- Interface gráfica de configuração
- Integração direta com VS Code/Cursor
- Comandos de voz para controlar o sistema
- Múltiplos perfis de configuração
- Sincronização de config na nuvem
- Suporte a outros idiomas além de PT/EN

---

## 12. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Latência alta no modo local | UX ruim | Oferecer modo Groq como fallback |
| API Groq instável | Indisponibilidade | Cache de modelo local como backup |
| Hotkey conflita com sistema | Não funciona | Permitir customização completa |
| VRAM insuficiente para full local | Crash | Detectar e alertar, sugerir modo híbrido |

---

## Aprovação

- [ ] Requisitos revisados pelo usuário
- [ ] Arquitetura aprovada
- [ ] Pronto para plano de implementação

