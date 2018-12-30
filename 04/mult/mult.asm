@R2
M=0            // Set R2 to 0
@R1
D=M            // Set D to multiplier
@END
M=D; JEQ       // Goto END if multiplier == 0 

(LOOP)
	@R0
	D=M          // Set D to multiplicand
	@R2
	M=D+M        // multiplicand += multiplicand
	@END
	M=M-1; JEQ   // Decrement multiplier; goto END if multiplier == 0
	@LOOP
	0; JMP       // Goto LOOP
	
(END)
	@END
	0; JMP       // Termination
