addi $s1,$0,2
addi $s2, $0, 1
addi $t1,$t1,1
loop_out:beq $t1,$s1,loop_out_end
	addi $t1,$t1,1
	addi $t2, $0, 1
	add $t3,$0,$s2
	loop_in: beq $t1, $t2, loop_in_end
		add $s2, $s2, $t3
		addi $t2,$t2,1
		j loop_in
	loop_in_end: j loop_out
loop_out_end: add $s1 $s1 $s1
