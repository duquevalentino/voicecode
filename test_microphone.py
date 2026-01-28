"""Test microphone recording."""

import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import time

print("=== Teste de Microfone ===\n")

# 1. Listar dispositivos
print("Dispositivos de entrada disponíveis:")
print("-" * 50)
devices = sd.query_devices()
input_devices = []
for i, d in enumerate(devices):
    if d['max_input_channels'] > 0:
        default = " [DEFAULT]" if i == sd.default.device[0] else ""
        print(f"  [{i}] {d['name'][:45]}{default}")
        input_devices.append((i, d))
print()

# 2. Procurar Fifine
fifine_device = None
for i, d in input_devices:
    if 'fifine' in d['name'].lower():
        fifine_device = (i, d)
        break

if fifine_device:
    device_id, device_info = fifine_device
    print(f"[ENCONTRADO] Fifine Microphone no dispositivo [{device_id}]")
else:
    device_id = sd.default.device[0]
    device_info = sd.query_devices(device_id)
    print(f"[AVISO] Fifine nao encontrado, usando padrao [{device_id}]")

print(f"  Nome: {device_info['name']}")
print(f"  Sample rate nativo: {device_info['default_samplerate']}")
print(f"  Canais: {device_info['max_input_channels']}")
print()

# 3. Gravar 3 segundos usando sample rate nativo
duration = 3  # segundos
sample_rate = int(device_info['default_samplerate'])

print(f"Gravando {duration} segundos com {device_info['name'][:30]}...")
print(">>> FALE ALGO AGORA! <<<")
print("-" * 50)

try:
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='int16',
        device=device_id,  # Usar dispositivo especifico
    )

    # Mostrar progresso
    for i in range(duration):
        time.sleep(1)
        print(f"  {i+1}/{duration} segundos...")

    sd.wait()
    print("Gravacao concluida!")

    # 4. Verificar se tem audio
    audio_level = np.abs(recording).mean()
    audio_max = np.abs(recording).max()

    print(f"\nAnalise do audio:")
    print(f"  Nivel medio: {audio_level:.1f}")
    print(f"  Nivel maximo: {audio_max}")
    print(f"  Amostras: {len(recording)} (esperado: {duration * sample_rate})")
    print(f"  Duracao real: {len(recording) / sample_rate:.2f}s")

    if audio_max < 500:
        print("\n" + "=" * 50)
        print("[PROBLEMA] Audio muito baixo ou silencio!")
        print("=" * 50)
        print("Possiveis solucoes:")
        print("  1. Verificar se o Fifine esta conectado via USB")
        print("  2. No Windows: Configuracoes > Som > Entrada")
        print("     - Selecionar 'Fifine Microphone' como padrao")
        print("     - Aumentar o volume do microfone")
        print("  3. Testar o microfone no Gravador de Voz do Windows")
    elif audio_max < 3000:
        print("\n[AVISO] Audio baixo. Aumente o volume do microfone no Windows.")
    else:
        print("\n[OK] Nivel de audio BOM!")

    # 5. Salvar arquivo para verificacao
    output_file = "test_recording.wav"
    wavfile.write(output_file, sample_rate, recording)
    print(f"\nArquivo salvo: {output_file}")
    print("Abra o arquivo para ouvir a gravacao.")

    # 6. Mostrar configuracao recomendada
    if fifine_device and audio_max > 500:
        print("\n" + "=" * 50)
        print("CONFIGURACAO RECOMENDADA para config.yaml:")
        print("=" * 50)
        print(f"Adicione no config.yaml para usar o Fifine:")
        print(f"  audio:")
        print(f"    device: {device_id}")
        print(f"    # ou device: \"{device_info['name']}\"")

except Exception as e:
    print(f"\n[ERRO] {e}")
    import traceback
    traceback.print_exc()
