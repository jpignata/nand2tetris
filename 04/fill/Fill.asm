// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.


// Sets the number of lines of the screen memory map for use in loops
@8192
D=A
@lines
M=D       // lines = 8192

// Listens for keyboard input. If key is pressed, fill all pixels which will
//   turn the screen black. Otherwise, clear all pixels which will clear the
//   screen.
(LISTEN)
	@KBD
	D=M
	@FILL
	D; JNE     // Goto FILL if key pressed (keyboard memory map != 0)
	@CLEAR
	D; JEQ     // Goto CLEAR if key not press (keyboard memory map == 0)
	@LISTEN
	0; JMP     // Goto LISTEN

// Fills all pixels on the screen.
(FILL)
	@R0
	M=-1       // R1 = -1 (decimal "all bits" number which will fill the screen)
	@DRAW      
	0; JMP     // Goto DRAW

// Clears all pixels on the screen.
(CLEAR)
	@R0
	M=0        // R1 = 0 (decimal "no bits" number which will clear the screen)
	@DRAW
	0; JMP     // Goto DRAW

// Sets contents of memory map to the number stored in R0. This allows a caller
// to set the register and call DRAW to either fill or clear the screen.
(DRAW)
	@i
	M=0        // i = 0

	(LOOP)
		@i
		D=M
		@lines
		D=M-D    // D = lines - i
		@LISTEN
		D; JEQ   // Goto LISTEN if D == 0

		@SCREEN
		D=A      // D = 16384
		@i
		D=D+M    // D = 16384 + i (current line)
		@R1
		M=D      // R1 = D
		@R0
		D=M      // D = R0 (either -1 or 0 which means fill or clear respectively)
		@R1
		A=M      // Move pointer to current line
		M=D      // Set current line to either -1 or 0

		@i
		M=M+1    // i += 1

		@LOOP
		0; JMP   // Goto LOOP
