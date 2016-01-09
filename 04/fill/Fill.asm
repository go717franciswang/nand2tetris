// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

(INIF_LOOP)

  @SCREEN     // i = 16384
  D=A
  @i
  M=D

  @24576      // keyboard
  D=M
  @KEYDOWN
  D;JNE       // if keyboard <> 0 goto KEYDOWN
  @color
  M=0
  @END_KEYDOWN
  0;JMP
  (KEYDOWN)
  @color
  M=-1
  (END_KEYDOWN)

  @24576      // end = 16384+256*32
  D=A
  @end
  M=D

  (LOOP)
    @color    // M[i] = color
    D=M
    @i
    A=M
    M=D

    @i        // i = i+1
    M=M+1

    @i        // if i-end < 0 goto LOOP
    D=M
    @end
    D=D-M
    @LOOP
    D;JLT

@INIF_LOOP
0;JMP
