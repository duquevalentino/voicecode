# VoiceCode - Plano de Implementação

**Versão:** 1.0
**Data:** 2026-01-28
**Baseado em:** Especificação de Requisitos v1.0

---

## Visão Geral das Fases

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PLANO DE IMPLEMENTAÇÃO                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  FASE 1: Foundation          FASE 2: Core MVP        FASE 3: Polish    │
│  ─────────────────           ──────────────          ──────────────    │
│  □ Setup ambiente            □ Hotkey listener       □ Context injection│
│  □ Estrutura projeto         □ Gravação áudio        □ Modos formatação │
│  □ Config loader             □ Transcrição Groq      □ Ciclar modos     │
│  □ Testes básicos            □ Output clipboard      □ Vocabulário      │
│                              □ System tray básico    □ Histórico        │
│                                                                         │
│  FASE 4: Local Backend       FASE 5: Refinamento                        │
│  ────────────────────        ──────────────────                         │
│  □ Whisper local             □ Sons feedback                            │
│  □ LLM local (Ollama)        □ Tratamento erros                         │
│  □ Switch backends           □ Documentação                             │
│                              □ Testes integração                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## FASE 1: Foundation (Setup e Estrutura)

**Objetivo:** Ter o ambiente pronto e estrutura base do projeto.

### 1.1 Setup do Ambiente Conda

```bash
# Tarefas:
□ Criar ambiente conda "voicecode"
□ Instalar dependências core
□ Configurar variáveis de ambiente (GROQ_API_KEY)
□ Verificar CUDA disponível
```

**Dependências iniciais:**
```
sounddevice numpy scipy groq keyboard pyperclip pystray Pillow pyyaml
```

### 1.2 Estrutura do Projeto

```
voicecode/
├── src/
│   └── voicecode/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       ├── config.py            # Loader de configuração
│       ├── audio/
│       │   ├── __init__.py
│       │   └── recorder.py      # Captura de áudio
│       ├── transcription/
│       │   ├── __init__.py
│       │   ├── base.py          # Interface abstrata
│       │   ├── groq_backend.py  # Implementação Groq
│       │   └── local_backend.py # Implementação local (Fase 4)
│       ├── processing/
│       │   ├── __init__.py
│       │   ├── base.py          # Interface abstrata
│       │   ├── groq_backend.py  # LLM via Groq
│       │   └── local_backend.py # LLM via Ollama (Fase 4)
│       ├── output/
│       │   ├── __init__.py
│       │   └── clipboard.py     # Clipboard e auto-paste
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── tray.py          # System tray
│       │   └── sounds.py        # Feedback sonoro
│       └── hotkeys/
│           ├── __init__.py
│           └── listener.py      # Listener de hotkeys
├── config.yaml                  # Configuração do usuário
├── sounds/
│   ├── start.wav
│   └── end.wav
├── history/
│   └── .gitkeep
├── tests/
│   └── ...
├── requirements.txt
└── README.md
```

### 1.3 Config Loader

```python
# Tarefas:
□ Criar config.py com dataclasses tipadas
□ Carregar YAML com valores default
□ Suportar variáveis de ambiente (${VAR})
□ Validar configuração na inicialização
```

### 1.4 Entregável Fase 1

- [x] Rodar `python -m voicecode` sem erros
- [x] Config carregada e validada
- [x] Estrutura de pastas criada

**Teste de validação:**
```bash
python -m voicecode --check-config
# Output: "Configuration valid. Ready to start."
```

---

## FASE 2: Core MVP (Fluxo Principal)

**Objetivo:** Gravar áudio → Transcrever via Groq → Colar texto. Fluxo completo funcional.

### 2.1 Gravação de Áudio

```python
# Tarefas:
□ Implementar AudioRecorder com sounddevice
□ Suportar gravação contínua (enquanto tecla pressionada)
□ Converter para formato WAV em memória
□ Detectar silêncio (opcional, otimização)
```

**Interface:**
```python
class AudioRecorder:
    def start_recording(self) -> None
    def stop_recording(self) -> bytes  # Retorna WAV
```

### 2.2 Transcrição via Groq

```python
# Tarefas:
□ Implementar GroqTranscriber
□ Enviar áudio WAV para API
□ Receber texto transcrito
□ Tratar erros de API (rate limit, timeout)
```

**Interface:**
```python
class GroqTranscriber(BaseTranscriber):
    def transcribe(self, audio: bytes) -> str
```

### 2.3 Hotkey Listener

```python
# Tarefas:
□ Implementar listener global de teclas
□ Suportar Push-to-Talk (on_press / on_release)
□ Suportar Toggle (press para start/stop)
□ Parsear hotkey string do config ("ctrl+shift+space")
```

**Interface:**
```python
class HotkeyListener:
    def __init__(self, config: HotkeyConfig, callbacks: Callbacks)
    def start(self) -> None
    def stop(self) -> None
```

### 2.4 Output (Clipboard)

```python
# Tarefas:
□ Implementar clipboard copy
□ Implementar auto-paste (simular Ctrl+V)
□ Respeitar config (clipboard_only vs auto_paste)
```

### 2.5 System Tray Básico

```python
# Tarefas:
□ Criar ícone na tray
□ Menu com "Exit"
□ Mudar cor do ícone (idle/recording/processing)
□ Tooltip com estado atual
```

### 2.6 Orquestrador Principal

```python
# Tarefas:
□ Integrar todos os componentes
□ Fluxo: hotkey → record → transcribe → output
□ Gerenciar estados (idle/recording/processing)
□ Atualizar tray conforme estado
```

### 2.7 Entregável Fase 2

- [x] Pressionar hotkey grava áudio
- [x] Soltar hotkey transcreve via Groq
- [x] Texto aparece no clipboard/colado
- [x] Ícone da tray muda de cor

**Teste de validação:**
```
1. Iniciar voicecode
2. Abrir Notepad
3. Pressionar Ctrl+Shift+Space
4. Falar "Olá mundo, isso é um teste"
5. Soltar tecla
6. Verificar: texto aparece no Notepad
```

---

## FASE 3: Polish (Modos e Features)

**Objetivo:** Adicionar processamento inteligente, modos, context injection.

### 3.1 Processamento LLM (Groq)

```python
# Tarefas:
□ Implementar GroqProcessor
□ System prompts para cada modo:
  - Raw: bypass (sem LLM)
  - Clean: remover fillers
  - Tech: formatar termos técnicos
  - Full: Clean + Tech
□ Integrar vocabulário customizado no prompt
```

**System Prompt (modo Full):**
```
Você é um assistente de transcrição para programadores.

Regras:
1. Remova palavras de preenchimento (hm, uh, tipo, então, né, ah)
2. Corrija pontuação
3. Formate termos técnicos corretamente:
   - Nomes de funções em camelCase ou snake_case conforme contexto
   - Nomes de bibliotecas com capitalização correta
4. Mantenha o significado original
5. Retorne APENAS o texto corrigido, sem explicações

Vocabulário técnico prioritário:
{vocabulary}

Texto para processar:
{transcription}
```

### 3.2 Ciclar Modos

```python
# Tarefas:
□ Implementar tecla para ciclar modos
□ Ordem: raw → clean → tech → full → raw
□ Atualizar tooltip da tray com modo atual
□ Feedback sonoro ao mudar modo (opcional)
```

### 3.3 Context Injection

```python
# Tarefas:
□ Detectar tecla modificadora (ex: +Alt)
□ Ler clipboard atual
□ Modificar prompt para incluir contexto:
  "Contexto (clipboard): {clipboard_content}

   Instrução do usuário: {transcription}

   Responda considerando o contexto."
```

### 3.4 Histórico

```python
# Tarefas:
□ Criar HistoryLogger
□ Salvar em JSONL: {timestamp, mode, raw, processed}
□ Implementar sliding window (max_entries)
□ Rotacionar arquivo quando exceder limite
```

### 3.5 Entregável Fase 3

- [x] Modo "full" formata termos técnicos
- [x] Ciclar modos com hotkey
- [x] Context injection funciona
- [x] Histórico salva transcrições

**Teste de validação:**
```
1. Modo Full ativo
2. Falar "crie uma função camel case chamada get user by id"
3. Verificar: "Crie uma função camelCase chamada getUserById"

4. Copiar um erro de Python
5. Hotkey + Alt (context)
6. Falar "o que está errado aqui"
7. Verificar: resposta menciona o erro copiado
```

---

## FASE 4: Local Backend (Opcional)

**Objetivo:** Rodar 100% local com Whisper + Ollama.

### 4.1 Whisper Local

```python
# Tarefas:
□ Instalar faster-whisper
□ Implementar LocalTranscriber
□ Carregar modelo na inicialização
□ Detectar CUDA automaticamente
□ Fallback para CPU se necessário
```

**Dependências adicionais:**
```
faster-whisper torch
```

### 4.2 LLM Local (Ollama)

```python
# Tarefas:
□ Implementar OllamaProcessor
□ Verificar se Ollama está rodando
□ Usar mesmo system prompt da Groq
□ Tratar timeout (modelos locais são mais lentos)
```

**Pré-requisito:** Ollama instalado com modelo `llama3:8b`

### 4.3 Switch de Backends

```python
# Tarefas:
□ Factory pattern para criar transcriber/processor
□ Respeitar config.yaml
□ Log indicando qual backend está ativo
```

### 4.4 Entregável Fase 4

- [x] Funciona 100% offline
- [x] Config permite trocar backend
- [x] Latência aceitável (< 3s)

**Teste de validação:**
```yaml
# config.yaml
transcription:
  backend: "local"
processing:
  backend: "local"
```
```
1. Desconectar internet
2. Testar transcrição
3. Verificar: funciona offline
```

---

## FASE 5: Refinamento

**Objetivo:** Polir UX, tratar edge cases, documentar.

### 5.1 Sons de Feedback

```python
# Tarefas:
□ Adicionar arquivos WAV (start.wav, end.wav)
□ Implementar SoundPlayer
□ Tocar som ao iniciar/parar gravação
□ Respeitar config (enabled: true/false)
```

### 5.2 Tratamento de Erros

```python
# Tarefas:
□ Erros de rede → notificação + fallback
□ Timeout → retry com backoff
□ Microfone não encontrado → erro claro
□ Config inválida → mensagem explicativa
□ VRAM insuficiente → sugerir modo cloud
```

### 5.3 Documentação

```markdown
# Tarefas:
□ README.md com instruções de instalação
□ Exemplos de config.yaml
□ Troubleshooting comum
□ GIF/vídeo demonstrando uso
```

### 5.4 Testes

```python
# Tarefas:
□ Testes unitários para cada módulo
□ Teste de integração do fluxo completo
□ Mock das APIs externas
```

### 5.5 Entregável Fase 5

- [x] Sons tocam corretamente
- [x] Erros são tratados graciosamente
- [x] README completo
- [x] Testes passando

---

## Cronograma Sugerido

| Fase | Descrição | Dependências |
|------|-----------|--------------|
| 1 | Foundation | Nenhuma |
| 2 | Core MVP | Fase 1 |
| 3 | Polish | Fase 2 |
| 4 | Local Backend | Fase 2 (paralelo à 3) |
| 5 | Refinamento | Fases 3 e 4 |

```
Fase 1 ──▶ Fase 2 ──┬──▶ Fase 3 ──┐
                    │             ├──▶ Fase 5
                    └──▶ Fase 4 ──┘
```

---

## Ordem de Implementação Detalhada

### Sessão 1: Setup (Fase 1)
1. Criar ambiente conda
2. Instalar dependências
3. Criar estrutura de pastas
4. Implementar `config.py`
5. Criar `config.yaml` de exemplo
6. Testar: `python -m voicecode --check-config`

### Sessão 2: Gravação + Transcrição (Fase 2.1-2.2)
1. Implementar `audio/recorder.py`
2. Testar gravação isolada
3. Implementar `transcription/groq_backend.py`
4. Testar transcrição isolada
5. Integrar: gravar → transcrever → print

### Sessão 3: Hotkeys + Output (Fase 2.3-2.4)
1. Implementar `hotkeys/listener.py`
2. Testar detecção de teclas
3. Implementar `output/clipboard.py`
4. Integrar: hotkey → gravar → transcrever → colar

### Sessão 4: System Tray (Fase 2.5-2.6)
1. Implementar `ui/tray.py`
2. Criar ícones coloridos
3. Implementar orquestrador em `__main__.py`
4. **MVP COMPLETO** - testar fluxo end-to-end

### Sessão 5: Processamento LLM (Fase 3.1-3.2)
1. Implementar `processing/groq_backend.py`
2. Criar system prompts para cada modo
3. Integrar no fluxo
4. Implementar ciclar modos

### Sessão 6: Context + Histórico (Fase 3.3-3.4)
1. Implementar context injection
2. Implementar histórico
3. Testar modos e context

### Sessão 7: Backend Local (Fase 4)
1. Instalar faster-whisper
2. Implementar `transcription/local_backend.py`
3. Implementar `processing/local_backend.py`
4. Testar modo 100% local

### Sessão 8: Refinamento (Fase 5)
1. Adicionar sons
2. Melhorar tratamento de erros
3. Escrever README
4. Testes finais

---

## Checklist de Validação Final

```
□ Instalar do zero seguindo README funciona
□ Push-to-talk funciona
□ Toggle funciona
□ Todos os 4 modos funcionam
□ Ciclar modos funciona
□ Context injection funciona
□ Histórico é salvo
□ Backend Groq funciona
□ Backend local funciona
□ Sons tocam
□ Tray mostra estados corretos
□ Config YAML é respeitada
□ Erros são tratados
```

---

## Aprovação

- [ ] Plano revisado pelo usuário
- [ ] Pronto para iniciar implementação

