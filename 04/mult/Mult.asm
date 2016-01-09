// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

  @i        // i=0
  M=0
  @R2       // R2=0
  M=0

  @R1       // if R1 < 0 goto NEGATIVE
  D=M
  @NEGATIVE
  D;JLT
  @inc
  M=1
  @R0       // mult=R0
  D=M
  @mult
  M=D
  @END_NEGATIVE
  0;JMP
(NEGATIVE)
  @inc
  M=-1
  @R0      // mult=-R0
  D=-M
  @mult
  M=D
(END_NEGATIVE)

(LOOP)
  @i        // if i-R1=0 goto END_LOOP
  D=M
  @R1
  D=D-M
  @END_LOOP
  D;JEQ

  @mult       // R2=R2+mult
  D=M
  @R2
  M=M+D
  @inc      // i=i+inc
  D=M
  @i
  M=M+D
  @LOOP
  0;JMP
(END_LOOP)

(END)
  @END
  0;JMP
