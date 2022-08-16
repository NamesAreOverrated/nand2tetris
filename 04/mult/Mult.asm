// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

    @R2
    M=0

    @i
    M=0


(LOOP)
    @i
    D=M   //get current i count

    @R1
    D=D-M //see if i - r1 == 0

    @END
    D;JEQ //if true end the program

    @R0
    D=M

    @END
    D;JEQ //if r0 == 0 then jump to end

    @R2
    M=M+D //R2+=R1

    @i
    M=M+1 //i++

    @LOOP
    0;JMP
    
   

(END)
    @END
    0;JMP