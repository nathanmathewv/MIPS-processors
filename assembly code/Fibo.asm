#############################################################
#Do not change any code above this line
#Occupied registers $t1,$t2. Don't use them in your function.
#############################################################
#function: 
add $t2,$0,$gp
addi $t1,$0,9
add $s0, $0, $0 # Analogous to a
addi $s1, $0, 1 # Analogous to b

sw $s0, 0($t2)
sw $s1, 4($t2)

addi $t3, $t2, 8 # Memory location where number has to be written
addi $t4, $0, 2 # Iteration variable

calculateNumbers: 

	beq $t4, $t1, endfunction
		
	add $s2, $s0, $s1
	sw $s2, 0($t3)
	add $s0, $s1, $0
	add $s1, $s2, $0
	
	addi $t4, $t4, 1
	addi $t3, $t3, 4

	j calculateNumbers
	
endfunction:
#endfunction
#############################################################
#You need not change any code below this line