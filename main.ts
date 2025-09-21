//  ==============================================================================
//  --- 1. CONFIGURAÇÕES E DECLARAÇÕES ---
//  ==============================================================================
//  --- Declarações de Variáveis ---
let strip : neopixel.Strip = null
let brilho_calculado = 0
let COR_FRENTE = 0
let COR_TRAS = 0
let COR_CURVA = 0
//  --- Variáveis de Estado e Efeitos ---
let ultimo_comando_recebido_tempo = 0
let TIMEOUT_CONEXAO = 500
let robot_state = "INICIALIZANDO"
let rainbow_hue = 0
let ultimo_pisca_tempo = 0
let led_pisca_ligado = true
//  --- Variáveis de Movimento Suave (Ramping) ---
let velocidade_alvo_M1 = 0
let velocidade_alvo_M2 = 0
let velocidade_atual_M1 = 0
let velocidade_atual_M2 = 0
//  --- Configurações Personalizáveis ---
let RADIO_GROUP = 1
let VELOCIDADE_MAXIMA = 255
let PASSO_ACELERACAO = 25
let PORTA_SERVO = robotbit.Servos.S2
let ANGULO_CENTRO = 90
let ANGULO_RIGHT = 110
let ANGULO_LEFT = 70
let BRILHO_LEDS = 0.5
let RGB_FRENTE = [0, 255, 0]
let RGB_TRAS = [255, 0, 0]
let RGB_CURVA = [0, 0, 255]
//  ==============================================================================
//  --- 2. DEFINIÇÃO DAS FUNÇÕES ---
//  ==============================================================================
function definir_alvo_movimento(estado: string, servo_angulo: number, vel_m1: number, vel_m2: number, icone: number, cor_led: number) {
    
    robot_state = estado
    robotbit.Servo(PORTA_SERVO, servo_angulo)
    velocidade_alvo_M1 = vel_m1
    velocidade_alvo_M2 = vel_m2
    basic.showArrow(icone)
    strip.showColor(cor_led)
}

function mover_frente() {
    definir_alvo_movimento("MOVENDO", ANGULO_CENTRO, VELOCIDADE_MAXIMA, VELOCIDADE_MAXIMA, ArrowNames.North, COR_FRENTE)
}

function mover_tras() {
    definir_alvo_movimento("MOVENDO", ANGULO_CENTRO, -VELOCIDADE_MAXIMA, -VELOCIDADE_MAXIMA, ArrowNames.South, COR_TRAS)
}

function virar_esquerda() {
    definir_alvo_movimento("MOVENDO", ANGULO_LEFT, VELOCIDADE_MAXIMA, VELOCIDADE_MAXIMA, ArrowNames.West, COR_CURVA)
}

function virar_direita() {
    definir_alvo_movimento("MOVENDO", ANGULO_RIGHT, VELOCIDADE_MAXIMA, VELOCIDADE_MAXIMA, ArrowNames.East, COR_CURVA)
}

function parar_robô_normal() {
    
    robot_state = "PARADO_NORMAL"
    velocidade_alvo_M1 = 0
    velocidade_alvo_M2 = 0
    basic.showIcon(IconNames.Asleep)
}

function parada_de_emergencia() {
    
    robot_state = "EMERGENCIA"
    velocidade_alvo_M1 = 0
    velocidade_alvo_M2 = 0
    basic.showIcon(IconNames.No)
}

//  --- Funções de Evento (Callbacks) ---
radio.onReceivedNumber(function on_radio_received(receivedNumber: number) {
    
    ultimo_comando_recebido_tempo = input.runningTime()
    if (receivedNumber == 5) {
        parar_robô_normal()
    } else if (receivedNumber == 1) {
        mover_frente()
    } else if (receivedNumber == 2) {
        mover_tras()
    } else if (receivedNumber == 3) {
        virar_esquerda()
    } else if (receivedNumber == 4) {
        virar_direita()
    }
    
})
input.onLogoEvent(TouchButtonEvent.Pressed, function on_logo_pressed() {
    parada_de_emergencia()
})
//  ==============================================================================
//  --- 3. LOOP PRINCIPAL (O "PARA SEMPRE" DO MAKECODE) ---
//  ==============================================================================
//  ==============================================================================
//  --- 4. EXECUÇÃO INICIAL ---
//  ==============================================================================
//  --- Inicialização dos Periféricos ---
radio.setTransmitPower(7)
radio.setGroup(RADIO_GROUP)
strip = neopixel.create(DigitalPin.P16, 4, NeoPixelMode.RGB)
brilho_calculado = Math.trunc(BRILHO_LEDS * 255)
strip.setBrightness(brilho_calculado)
//  SEÇÃO CORRIGIDA PARA RESOLVER O ERRO
COR_FRENTE = neopixel.rgb(RGB_FRENTE[0], RGB_FRENTE[1], RGB_FRENTE[2])
COR_TRAS = neopixel.rgb(RGB_TRAS[0], RGB_TRAS[1], RGB_TRAS[2])
COR_CURVA = neopixel.rgb(RGB_CURVA[0], RGB_CURVA[1], RGB_CURVA[2])
//  --- Sequência de Inicialização (Jingle Básico) ---
basic.showIcon(IconNames.Target)
let startup_jingle = "C4:1 E4:1 G4:1 C5:2"
music.playMelody(startup_jingle, 220)
//  Teste Rápido de Sistemas
strip.showColor(neopixel.colors(NeoPixelColors.White))
basic.pause(200)
strip.showColor(neopixel.colors(NeoPixelColors.Black))
basic.pause(200)
robotbit.Servo(PORTA_SERVO, ANGULO_CENTRO)
//  Entra no estado normal de espera
parar_robô_normal()
ultimo_comando_recebido_tempo = input.runningTime()
//  Registra a função on_forever para ser executada em loop
basic.forever(function on_forever() {
    
    
    //  --- Lógica de Aceleração Suave (Ramping) ---
    if (velocidade_atual_M1 < velocidade_alvo_M1) {
        velocidade_atual_M1 = Math.min(velocidade_alvo_M1, velocidade_atual_M1 + PASSO_ACELERACAO)
    } else if (velocidade_atual_M1 > velocidade_alvo_M1) {
        velocidade_atual_M1 = Math.max(velocidade_alvo_M1, velocidade_atual_M1 - PASSO_ACELERACAO)
    }
    
    if (velocidade_atual_M2 < velocidade_alvo_M2) {
        velocidade_atual_M2 = Math.min(velocidade_alvo_M2, velocidade_atual_M2 + PASSO_ACELERACAO)
    } else if (velocidade_atual_M2 > velocidade_alvo_M2) {
        velocidade_atual_M2 = Math.max(velocidade_alvo_M2, velocidade_atual_M2 - PASSO_ACELERACAO)
    }
    
    robotbit.MotorRunDual(robotbit.Motors.M1A, velocidade_atual_M1, robotbit.Motors.M2A, velocidade_atual_M2)
    //  --- Lógica do Failsafe (Timeout) ---
    if (input.runningTime() - ultimo_comando_recebido_tempo > TIMEOUT_CONEXAO && robot_state != "EMERGENCIA") {
        parada_de_emergencia()
    }
    
    //  --- Lógica dos Efeitos de Luz com base no Estado ---
    if (robot_state == "PARADO_NORMAL") {
        rainbow_hue = (rainbow_hue + 1) % 360
        strip.showColor(neopixel.hsl(rainbow_hue, 255, 128))
    } else if (robot_state == "EMERGENCIA") {
        if (input.runningTime() - ultimo_pisca_tempo > 250) {
            ultimo_pisca_tempo = input.runningTime()
            led_pisca_ligado = !led_pisca_ligado
        }
        
        strip.showColor(led_pisca_ligado ? neopixel.colors(NeoPixelColors.Red) : neopixel.colors(NeoPixelColors.Black))
    }
    
    basic.pause(20)
})
