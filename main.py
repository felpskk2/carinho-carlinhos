# ==============================================================================
# --- 1. CONFIGURAÇÕES E DECLARAÇÕES ---
# ==============================================================================
# --- Declarações de Variáveis ---
strip: neopixel.Strip = None
brilho_calculado = 0
COR_FRENTE = 0; COR_TRAS = 0; COR_CURVA = 0;

# --- Variáveis de Estado e Efeitos ---
ultimo_comando_recebido_tempo = 0
TIMEOUT_CONEXAO = 500
robot_state = "INICIALIZANDO"
rainbow_hue = 0
ultimo_pisca_tempo = 0
led_pisca_ligado = True

# --- Variáveis de Movimento Suave (Ramping) ---
velocidade_alvo_M1 = 0; velocidade_alvo_M2 = 0
velocidade_atual_M1 = 0; velocidade_atual_M2 = 0

# --- Configurações Personalizáveis ---
RADIO_GROUP = 1
VELOCIDADE_MAXIMA = 255
PASSO_ACELERACAO = 25
PORTA_SERVO = robotbit.Servos.S2
ANGULO_CENTRO = 90; ANGULO_RIGHT = 110; ANGULO_LEFT = 70
BRILHO_LEDS = 0.5
RGB_FRENTE = (0, 255, 0); RGB_TRAS = (255, 0, 0); RGB_CURVA = (0, 0, 255)

# ==============================================================================
# --- 2. DEFINIÇÃO DAS FUNÇÕES ---
# ==============================================================================

def definir_alvo_movimento(estado, servo_angulo, vel_m1, vel_m2, icone, cor_led):
    global robot_state, velocidade_alvo_M1, velocidade_alvo_M2
    robot_state = estado
    robotbit.servo(PORTA_SERVO, servo_angulo)
    velocidade_alvo_M1 = vel_m1
    velocidade_alvo_M2 = vel_m2
    basic.show_arrow(icone)
    strip.show_color(cor_led)

def mover_frente():
    definir_alvo_movimento("MOVENDO", ANGULO_CENTRO, VELOCIDADE_MAXIMA, VELOCIDADE_MAXIMA, ArrowNames.NORTH, COR_FRENTE)
def mover_tras():
    definir_alvo_movimento("MOVENDO", ANGULO_CENTRO, -VELOCIDADE_MAXIMA, -VELOCIDADE_MAXIMA, ArrowNames.SOUTH, COR_TRAS)
def virar_esquerda():
    definir_alvo_movimento("MOVENDO", ANGULO_LEFT, VELOCIDADE_MAXIMA, VELOCIDADE_MAXIMA, ArrowNames.WEST, COR_CURVA)
def virar_direita():
    definir_alvo_movimento("MOVENDO", ANGULO_RIGHT, VELOCIDADE_MAXIMA, VELOCIDADE_MAXIMA, ArrowNames.EAST, COR_CURVA)

def parar_robô_normal():
    global robot_state, velocidade_alvo_M1, velocidade_alvo_M2
    robot_state = "PARADO_NORMAL"
    velocidade_alvo_M1 = 0; velocidade_alvo_M2 = 0
    basic.show_icon(IconNames.ASLEEP)

def parada_de_emergencia():
    global robot_state, velocidade_alvo_M1, velocidade_alvo_M2
    robot_state = "EMERGENCIA"
    velocidade_alvo_M1 = 0; velocidade_alvo_M2 = 0
    basic.show_icon(IconNames.NO)

# --- Funções de Evento (Callbacks) ---
def on_radio_received(receivedNumber):
    global ultimo_comando_recebido_tempo
    ultimo_comando_recebido_tempo = input.running_time()
    if receivedNumber == 5: parar_robô_normal()
    else:
        if receivedNumber == 1: mover_frente()
        elif receivedNumber == 2: mover_tras()
        elif receivedNumber == 3: virar_esquerda()
        elif receivedNumber == 4: virar_direita()
radio.on_received_number(on_radio_received)

def on_logo_pressed():
    parada_de_emergencia()
input.on_logo_event(TouchButtonEvent.PRESSED, on_logo_pressed)

# ==============================================================================
# --- 3. LOOP PRINCIPAL (O "PARA SEMPRE" DO MAKECODE) ---
# ==============================================================================

def on_forever():
    global velocidade_atual_M1, velocidade_atual_M2, robot_state
    global rainbow_hue, ultimo_pisca_tempo, led_pisca_ligado

    # --- Lógica de Aceleração Suave (Ramping) ---
    if velocidade_atual_M1 < velocidade_alvo_M1: velocidade_atual_M1 = min(velocidade_alvo_M1, velocidade_atual_M1 + PASSO_ACELERACAO)
    elif velocidade_atual_M1 > velocidade_alvo_M1: velocidade_atual_M1 = max(velocidade_alvo_M1, velocidade_atual_M1 - PASSO_ACELERACAO)
    if velocidade_atual_M2 < velocidade_alvo_M2: velocidade_atual_M2 = min(velocidade_alvo_M2, velocidade_atual_M2 + PASSO_ACELERACAO)
    elif velocidade_atual_M2 > velocidade_alvo_M2: velocidade_atual_M2 = max(velocidade_alvo_M2, velocidade_atual_M2 - PASSO_ACELERACAO)
    robotbit.motor_run_dual(robotbit.Motors.M1A, velocidade_atual_M1, robotbit.Motors.M2A, velocidade_atual_M2)

    # --- Lógica do Failsafe (Timeout) ---
    if input.running_time() - ultimo_comando_recebido_tempo > TIMEOUT_CONEXAO and robot_state != "EMERGENCIA":
        parada_de_emergencia()

    # --- Lógica dos Efeitos de Luz com base no Estado ---
    if robot_state == "PARADO_NORMAL":
        rainbow_hue = (rainbow_hue + 1) % 360
        strip.show_color(neopixel.hsl(rainbow_hue, 255, 128))
    elif robot_state == "EMERGENCIA":
        if input.running_time() - ultimo_pisca_tempo > 250:
            ultimo_pisca_tempo = input.running_time()
            led_pisca_ligado = not led_pisca_ligado
        strip.show_color(neopixel.colors(NeoPixelColors.RED) if led_pisca_ligado else neopixel.colors(NeoPixelColors.BLACK))

    basic.pause(20)

# ==============================================================================
# --- 4. EXECUÇÃO INICIAL ---
# ==============================================================================

# --- Inicialização dos Periféricos ---
radio.set_transmit_power(7)
radio.set_group(RADIO_GROUP)
strip = neopixel.create(DigitalPin.P16, 4, NeoPixelMode.RGB)
brilho_calculado = int(BRILHO_LEDS * 255)
strip.set_brightness(brilho_calculado)

# SEÇÃO CORRIGIDA PARA RESOLVER O ERRO
COR_FRENTE = neopixel.rgb(RGB_FRENTE[0], RGB_FRENTE[1], RGB_FRENTE[2])
COR_TRAS = neopixel.rgb(RGB_TRAS[0], RGB_TRAS[1], RGB_TRAS[2])
COR_CURVA = neopixel.rgb(RGB_CURVA[0], RGB_CURVA[1], RGB_CURVA[2])

# --- Sequência de Inicialização (Jingle Básico) ---
basic.show_icon(IconNames.TARGET)
startup_jingle = "C4:1 E4:1 G4:1 C5:2"
music.play_melody(startup_jingle, 220)
# Teste Rápido de Sistemas
strip.show_color(neopixel.colors(NeoPixelColors.WHITE)); basic.pause(200)
strip.show_color(neopixel.colors(NeoPixelColors.BLACK)); basic.pause(200)
robotbit.servo(PORTA_SERVO, ANGULO_CENTRO)
# Entra no estado normal de espera
parar_robô_normal()
ultimo_comando_recebido_tempo = input.running_time()

# Registra a função on_forever para ser executada em loop
basic.forever(on_forever)