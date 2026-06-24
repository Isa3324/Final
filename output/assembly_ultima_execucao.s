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
    @ Comando 1 - linha fonte 3
    @ ==========================================
    @ operacao aritmetica /
    @ literal 7
    ldr r0, =const_0
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vstr d0, [r10]
    add r10, r10, #8
    @ literal 2
    ldr r0, =const_1
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vmov.f64 d1, d0
    sub r10, r10, #8
    vldr d0, [r10]
    ldr r0, =const_zero
    vldr d3, [r0]
    vcmp.f64 d1, d3
    vmrs APSR_nzcv, FPSCR
    beq erro_div_zero
    @ operandos inteiros ja foram validados semanticamente
    @ calcula quociente e converte para inteiro
    vdiv.f64 d2, d0, d1
    vcvt.s32.f64 s4, d2
    vcvt.f64.s32 d2, s4
    vmov.f64 d0, d2
    mov r7, #0
    @ salva resultado do comando 1
    ldr r8, =resultados
    vstr d0, [r8]
    ldr r8, =resultados_null
    str r7, [r8]

    @ ==========================================
    @ Comando 2 - linha fonte 4
    @ ==========================================
    @ operacao aritmetica //
    @ literal 7
    ldr r0, =const_0
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vstr d0, [r10]
    add r10, r10, #8
    @ literal 2
    ldr r0, =const_1
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vmov.f64 d1, d0
    sub r10, r10, #8
    vldr d0, [r10]
    ldr r0, =const_zero
    vldr d3, [r0]
    vcmp.f64 d1, d3
    vmrs APSR_nzcv, FPSCR
    beq erro_div_zero
    @ operandos inteiros ja foram validados semanticamente
    @ calcula quociente e converte para inteiro
    vdiv.f64 d2, d0, d1
    vcvt.s32.f64 s4, d2
    vcvt.f64.s32 d2, s4
    vmov.f64 d0, d2
    mov r7, #0
    @ salva resultado do comando 2
    ldr r8, =resultados
    add r8, r8, #8
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #4
    str r7, [r8]

    @ ==========================================
    @ Comando 3 - linha fonte 5
    @ ==========================================
    @ operacao aritmetica %
    @ literal 7
    ldr r0, =const_0
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vstr d0, [r10]
    add r10, r10, #8
    @ literal 2
    ldr r0, =const_1
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vmov.f64 d1, d0
    sub r10, r10, #8
    vldr d0, [r10]
    ldr r0, =const_zero
    vldr d3, [r0]
    vcmp.f64 d1, d3
    vmrs APSR_nzcv, FPSCR
    beq erro_div_zero
    @ operandos inteiros ja foram validados semanticamente
    @ calcula quociente e converte para inteiro
    vdiv.f64 d2, d0, d1
    vcvt.s32.f64 s4, d2
    vcvt.f64.s32 d2, s4
    @ resto = dividendo - (quociente * divisor)
    vmul.f64 d3, d2, d1
    vsub.f64 d0, d0, d3
    mov r7, #0
    @ salva resultado do comando 3
    ldr r8, =resultados
    add r8, r8, #16
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #8
    str r7, [r8]

    @ ==========================================
    @ Comando 4 - linha fonte 6
    @ ==========================================
    @ atribuicao literal para A
    @ literal 1
    ldr r0, =const_um
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    ldr r9, =mem_A
    vstr d0, [r9]
    mov r7, #0
    @ salva resultado do comando 4
    ldr r8, =resultados
    add r8, r8, #24
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #12
    str r7, [r8]

    @ ==========================================
    @ Comando 5 - linha fonte 7
    @ ==========================================
    @ atribuicao literal para B
    @ literal 2
    ldr r0, =const_1
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    ldr r9, =mem_B
    vstr d0, [r9]
    mov r7, #0
    @ salva resultado do comando 5
    ldr r8, =resultados
    add r8, r8, #32
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #16
    str r7, [r8]

    @ ==========================================
    @ Comando 6 - linha fonte 8
    @ ==========================================
    @ atribuicao literal para C
    @ literal 3
    ldr r0, =const_2
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    ldr r9, =mem_C
    vstr d0, [r9]
    mov r7, #0
    @ salva resultado do comando 6
    ldr r8, =resultados
    add r8, r8, #40
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #20
    str r7, [r8]

    @ ==========================================
    @ Comando 7 - linha fonte 9
    @ ==========================================
    @ atribuicao literal para D
    @ literal 4
    ldr r0, =const_3
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    ldr r9, =mem_D
    vstr d0, [r9]
    mov r7, #0
    @ salva resultado do comando 7
    ldr r8, =resultados
    add r8, r8, #48
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #24
    str r7, [r8]

    @ ==========================================
    @ Comando 8 - linha fonte 10
    @ ==========================================
    @ atribuicao literal para S
    @ literal 5
    ldr r0, =const_4
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    ldr r9, =mem_S
    vstr d0, [r9]
    mov r7, #0
    @ salva resultado do comando 8
    ldr r8, =resultados
    add r8, r8, #56
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #28
    str r7, [r8]

    @ ==========================================
    @ Comando 9 - linha fonte 11
    @ ==========================================
    @ operacao aritmetica +
    @ literal 2.00
    ldr r0, =const_5
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vstr d0, [r10]
    add r10, r10, #8
    @ literal 3
    ldr r0, =const_2
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vmov.f64 d1, d0
    sub r10, r10, #8
    vldr d0, [r10]
    vadd.f64 d0, d0, d1
    mov r7, #0
    @ salva resultado do comando 9
    ldr r8, =resultados
    add r8, r8, #64
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #32
    str r7, [r8]

    @ ==========================================
    @ Comando 10 - linha fonte 12
    @ ==========================================
    @ operacao aritmetica ^
    @ literal 2.00
    ldr r0, =const_5
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vstr d0, [r10]
    add r10, r10, #8
    @ literal 3.00
    ldr r0, =const_6
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vmov.f64 d1, d0
    sub r10, r10, #8
    vldr d0, [r10]
    @ potenciacao: expoente inteiro nao negativo
    vcvt.s32.f64 s4, d1
    vmov r1, s4
    cmp r1, #0
    blt erro_expoente
    vmov.f64 d3, d0
    ldr r0, =const_um
    vldr d0, [r0]
pot_loop_0:
    cmp r1, #0
    beq pot_fim_1
    vmul.f64 d0, d0, d3
    sub r1, r1, #1
    b pot_loop_0
pot_fim_1:
    mov r7, #0
    @ salva resultado do comando 10
    ldr r8, =resultados
    add r8, r8, #72
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #36
    str r7, [r8]

    @ ==========================================
    @ Comando 11 - linha fonte 13
    @ ==========================================
    @ decisao se
    @ operacao relacional <=
    @ leitura da memoria A
    ldr r9, =mem_A
    vldr d0, [r9]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vstr d0, [r10]
    add r10, r10, #8
    @ leitura da memoria C
    ldr r9, =mem_C
    vldr d0, [r9]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vmov.f64 d1, d0
    sub r10, r10, #8
    vldr d0, [r10]
    vcmp.f64 d0, d1
    vmrs APSR_nzcv, FPSCR
    ldr r0, =const_zero
    vldr d0, [r0]
    ble rel_true_4
    b rel_fim_5
rel_true_4:
    ldr r0, =const_um
    vldr d0, [r0]
rel_fim_5:
    mov r7, #0
    cmp r7, #0
    bne erro_null
    ldr r0, =const_zero
    vldr d1, [r0]
    vcmp.f64 d0, d1
    vmrs APSR_nzcv, FPSCR
    beq se_falso_2
    @ decisao se
    @ operacao relacional <=
    @ leitura da memoria A
    ldr r9, =mem_A
    vldr d0, [r9]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vstr d0, [r10]
    add r10, r10, #8
    @ leitura da memoria B
    ldr r9, =mem_B
    vldr d0, [r9]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vmov.f64 d1, d0
    sub r10, r10, #8
    vldr d0, [r10]
    vcmp.f64 d0, d1
    vmrs APSR_nzcv, FPSCR
    ldr r0, =const_zero
    vldr d0, [r0]
    ble rel_true_8
    b rel_fim_9
rel_true_8:
    ldr r0, =const_um
    vldr d0, [r0]
rel_fim_9:
    mov r7, #0
    cmp r7, #0
    bne erro_null
    ldr r0, =const_zero
    vldr d1, [r0]
    vcmp.f64 d0, d1
    vmrs APSR_nzcv, FPSCR
    beq se_falso_6
    @ leitura da memoria D
    ldr r9, =mem_D
    vldr d0, [r9]
    mov r7, #0
    b se_fim_7
se_falso_6:
    ldr r0, =const_zero
    vldr d0, [r0]
    mov r7, #1          @ resultado NULL
se_fim_7:
    b se_fim_3
se_falso_2:
    ldr r0, =const_zero
    vldr d0, [r0]
    mov r7, #1          @ resultado NULL
se_fim_3:
    @ salva resultado do comando 11
    ldr r8, =resultados
    add r8, r8, #80
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #40
    str r7, [r8]

    @ ==========================================
    @ Comando 12 - linha fonte 14
    @ ==========================================
    @ repeticao enquanto
    ldr r0, =const_zero
    vldr d0, [r0]
    ldr r9, =temp_laco_valor_0
    vstr d0, [r9]
    mov r7, #1          @ inicialmente NULL
    ldr r9, =temp_laco_null_0
    str r7, [r9]
enquanto_inicio_10:
    @ operacao relacional <
    @ leitura da memoria A
    ldr r9, =mem_A
    vldr d0, [r9]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vstr d0, [r10]
    add r10, r10, #8
    @ leitura da memoria B
    ldr r9, =mem_B
    vldr d0, [r9]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vmov.f64 d1, d0
    sub r10, r10, #8
    vldr d0, [r10]
    vcmp.f64 d0, d1
    vmrs APSR_nzcv, FPSCR
    ldr r0, =const_zero
    vldr d0, [r0]
    blt rel_true_12
    b rel_fim_13
rel_true_12:
    ldr r0, =const_um
    vldr d0, [r0]
rel_fim_13:
    mov r7, #0
    cmp r7, #0
    bne erro_null
    ldr r0, =const_zero
    vldr d1, [r0]
    vcmp.f64 d0, d1
    vmrs APSR_nzcv, FPSCR
    beq enquanto_fim_11
    @ atribuicao literal para A
    @ literal 2
    ldr r0, =const_1
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    ldr r9, =mem_A
    vstr d0, [r9]
    mov r7, #0
    ldr r9, =temp_laco_valor_0
    vstr d0, [r9]
    ldr r9, =temp_laco_null_0
    str r7, [r9]
    b enquanto_inicio_10
enquanto_fim_11:
    ldr r9, =temp_laco_valor_0
    vldr d0, [r9]
    ldr r9, =temp_laco_null_0
    ldr r7, [r9]
    @ salva resultado do comando 12
    ldr r8, =resultados
    add r8, r8, #88
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #44
    str r7, [r8]

    @ ==========================================
    @ Comando 13 - linha fonte 15
    @ ==========================================
    @ RES 0: carrega resultado do comando 12
    ldr r8, =resultados
    add r8, r8, #88
    vldr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #44
    ldr r7, [r8]
    @ salva resultado do comando 13
    ldr r8, =resultados
    add r8, r8, #96
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #48
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

.data
    .align 3
const_zero: .double 0.0
const_um:   .double 1.0
const_0: .double 7.0
const_1: .double 2.0
const_2: .double 3.0
const_3: .double 4.0
const_4: .double 5.0
const_5: .double 2.00
const_6: .double 3.00
mem_A: .double 0.0
mem_B: .double 0.0
mem_C: .double 0.0
mem_D: .double 0.0
mem_S: .double 0.0
temp_laco_valor_0: .double 0.0
temp_laco_null_0: .word 1
    .align 3
resultados:      .space 104
resultados_null: .space 52
pilha_expr:      .space 2048
