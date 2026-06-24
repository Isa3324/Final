.syntax unified
.arch armv7-a
.fpu vfpv3
.global _start

.text
_start:
    ldr r10, =pilha_expr       @ pilha temporaria para expressoes
    ldr r11, =resultados       @ resultados dos comandos principais
    ldr r12, =resultados_null  @ flag NULL: 0=valor, 1=NULL

    @ ==========================================
    @ Comando 1 - linha fonte 2
    @ ==========================================
    @ comando morse otimizado: 1 ISA STOHLER BERTOLACCINI
    ldr r0, =morse_seq_0
    b morse_executar_loop
    @ resultado neutro inalcançavel por causa do loop morse
    ldr r0, =const_zero
    vldr d0, [r0]
    mov r7, #0
    @ salva resultado do comando 1
    ldr r8, =resultados
    vstr d0, [r8]
    ldr r8, =resultados_null
    str r7, [r8]

    b fim

fim:
    b fim

erro_null:
    @ NULL usado onde era necessario um valor numerico
    b erro_null

erro_div_zero:
    @ tentativa de divisao por zero
    b erro_div_zero

erro_expoente:
    @ expoente deve ser inteiro nao negativo
    b erro_expoente


@ ==========================================
@ Runtime Morse - LEDR e Timer DE1-SoC
@ ==========================================
.equ LEDR_BASE,  0xFF200000
.equ TIMER_BASE, 0xFF202000

@ ==========================================
@ Runtime Hardware - sequencia led/delay
@ ==========================================
executar_seq_hardware:
    push {r4, r5, r6, lr}
    mov r5, r0              @ r5 aponta para a sequencia

seq_hw_loop:
    ldr r4, [r5], #4        @ codigo da acao
    ldr r6, [r5], #4        @ argumento da acao

    cmp r4, #0              @ 0 = fim da sequencia
    beq seq_hw_fim

    cmp r4, #1              @ 1 = ligar LED
    beq seq_hw_ligar

    cmp r4, #2              @ 2 = desligar LED
    beq seq_hw_desligar

    cmp r4, #3              @ 3 = delay em ciclos
    beq seq_hw_delay

    b seq_hw_loop           @ ignora codigo desconhecido

seq_hw_ligar:
    mov r0, r6
    bl hw_led_ligar
    b seq_hw_loop

seq_hw_desligar:
    mov r0, r6
    bl hw_led_desligar
    b seq_hw_loop

seq_hw_delay:
    mov r0, r6
    bl delay_cycles
    b seq_hw_loop

seq_hw_fim:
    pop {r4, r5, r6, pc}

hw_led_ligar:
    push {r1, r2, r3, lr}
    ldr r1, =estado_leds
    ldr r2, [r1]
    orr r2, r2, r0
    str r2, [r1]
    ldr r3, =LEDR_BASE
    str r2, [r3]
    pop {r1, r2, r3, pc}

hw_led_desligar:
    push {r1, r2, r3, lr}
    ldr r1, =estado_leds
    ldr r2, [r1]
    bic r2, r2, r0
    str r2, [r1]
    ldr r3, =LEDR_BASE
    str r2, [r3]
    pop {r1, r2, r3, pc}

morse_executar_loop:
    mov r4, r0              @ r4 guarda o inicio da sequencia

morse_reiniciar:
    mov r5, r4              @ r5 percorre a sequencia desde o inicio

morse_ler_proximo:
    ldrb r0, [r5], #1       @ le um byte e avanca o ponteiro

    cmp r0, #0              @ 0 = fim da sequencia
    beq morse_reiniciar

    cmp r0, #1              @ 1 = ponto
    beq morse_chama_ponto

    cmp r0, #2              @ 2 = traco
    beq morse_chama_traco

    cmp r0, #3              @ 3 = espaco dentro da letra
    beq morse_chama_gap_simbolo

    cmp r0, #4              @ 4 = espaco entre letras
    beq morse_chama_gap_letra

    cmp r0, #5              @ 5 = espaco entre palavras
    beq morse_chama_gap_palavra

    b morse_ler_proximo     @ ignora codigo desconhecido

morse_chama_ponto:
    bl morse_ponto
    b morse_ler_proximo

morse_chama_traco:
    bl morse_traco
    b morse_ler_proximo

morse_chama_gap_simbolo:
    bl morse_gap_simbolo
    b morse_ler_proximo

morse_chama_gap_letra:
    bl morse_gap_letra
    b morse_ler_proximo

morse_chama_gap_palavra:
    bl morse_gap_palavra
    b morse_ler_proximo

morse_ponto:
    push {r0, r1, r2, lr}
    ldr r1, =LEDR_BASE
    mov r2, #1
    str r2, [r1]
    ldr r0, =30000000      @ 300 ms
    bl delay_cycles
    mov r2, #0
    str r2, [r1]
    pop {r0, r1, r2, pc}

morse_traco:
    push {r0, r1, r2, lr}
    ldr r1, =LEDR_BASE
    mov r2, #1
    str r2, [r1]
    ldr r0, =60000000      @ 600 ms
    bl delay_cycles
    mov r2, #0
    str r2, [r1]
    pop {r0, r1, r2, pc}

morse_gap_simbolo:
    push {r0, lr}
    ldr r0, =45000000      @ 450 ms
    bl delay_cycles
    pop {r0, pc}

morse_gap_letra:
    push {r0, lr}
    ldr r0, =90000000      @ 900 ms
    bl delay_cycles
    pop {r0, pc}

morse_gap_palavra:
    push {r0, lr}
    ldr r0, =200000000     @ 2000 ms
    bl delay_cycles
    pop {r0, pc}

delay_cycles:
    push {r1, r2, r3, lr}
    ldr r1, =TIMER_BASE

    @ para o timer antes de configurar
    mov r2, #8
    str r2, [r1, #4]

    @ limpa status de timeout
    mov r2, #0
    str r2, [r1, #0]

    @ periodo baixo: r0 & 0xFFFF
    uxth r2, r0
    str r2, [r1, #8]

    @ periodo alto: r0 >> 16
    lsr r3, r0, #16
    str r3, [r1, #12]

    @ inicia timer: START = bit 2
    mov r2, #4
    str r2, [r1, #4]

delay_cycles_loop:
    ldr r2, [r1, #0]
    tst r2, #1
    beq delay_cycles_loop

    @ limpa timeout
    mov r2, #0
    str r2, [r1, #0]

    pop {r1, r2, r3, pc}

.data
    .align 3
const_zero: .double 0.0
const_um:   .double 1.0
estado_leds: .word 0
    .align 3
resultados:      .space 8
resultados_null: .space 4
    .align 3
pilha_expr:      .space 2048

morse_seq_0: .byte 1, 3, 2, 3, 2, 3, 2, 3, 2, 5, 1, 3, 1, 4, 1, 3, 1, 3, 1, 4, 1, 3, 2, 5, 1, 3, 1, 3, 1, 4, 2, 4, 2, 3, 2, 3, 2, 4, 1, 3, 1, 3, 1, 3, 1, 4, 1, 3, 2, 3, 1, 3, 1, 4, 1, 4, 1, 3, 2, 3, 1, 5, 2, 3, 1, 3, 1, 3, 1, 4, 1, 4, 1, 3, 2, 3, 1, 4, 2, 4, 2, 3, 2, 3, 2, 4, 1, 3, 2, 3, 1, 3, 1, 4, 1, 3, 2, 4, 2, 3, 1, 3, 2, 3, 1, 4, 2, 3, 1, 3, 2, 3, 1, 4, 1, 3, 1, 4, 2, 3, 1, 4, 1, 3, 1, 5, 0
    .align 2
