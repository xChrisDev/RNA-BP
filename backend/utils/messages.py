from colorama import Fore, Style, init

init(autoreset=True)

INFO_COLOR = Fore.CYAN
SUCCESS_COLOR = Fore.GREEN
WARNING_COLOR = Fore.YELLOW
ERROR_COLOR = Fore.RED
EPOCH_COLOR = Fore.MAGENTA

def message_color(texto, color=INFO_COLOR):
    print("\n" + color + "=" * 60)
    print(color + texto)
    print(color + "=" * 60 + Style.RESET_ALL)

def message_color_epochs(texto, color=EPOCH_COLOR):
    print(color + texto + Style.RESET_ALL)

def message_trained_success(epochs: int, final_rms: float, tiempo_total: float):
    print("\n" + SUCCESS_COLOR + "=" * 60)
    print(SUCCESS_COLOR + "✅ ¡ENTRENAMIENTO COMPLETADO CON ÉXITO!")
    print(SUCCESS_COLOR + f"🧠 Épocas totales: {epochs}")
    print(SUCCESS_COLOR + f"📉 RMS final: {final_rms:.6f}")
    print(SUCCESS_COLOR + f"⏱️ Tiempo total: {tiempo_total:.2f} segundos")
    print(SUCCESS_COLOR + "=" * 60 + Style.RESET_ALL)

def message_prediction_result(
    pattern_idx: int,
    binary_output: list,
    prediction_time: float,
):
    print("\n" + INFO_COLOR + "=" * 60)
    print(INFO_COLOR + "🔍 PREDICCIÓN COMPLETADA")
    print(INFO_COLOR + f"📌 Patrón reconocido: {pattern_idx + 1 if pattern_idx >= 0 else 'No reconocido'}")
    print(INFO_COLOR + f"🧾 Salida binaria: {binary_output}")
    print(INFO_COLOR + f"⏱️ Tiempo: {prediction_time:.3f}s")
    print(INFO_COLOR + "=" * 60 + Style.RESET_ALL)
