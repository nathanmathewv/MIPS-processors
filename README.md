# MIPS-processors
This is a Python project which is used to simulate 5-stage MIPS processors in a pipelined and non-pipelined manner.

The 5 stages of a MIPS processor are -
  1. IF (Instruction Fetch)
  2. ID (Instruction Decode)
  3. EX (Execution state)
  4. MEM (Memory write)
  5. WB (Writeback)

## Non-Pipelined Processor
The non-pipelined processor takes one instruction and does all 5 stages, only after which it fetches the next instruction. This leads to wastage in clock cycles as when an instruction is in one stage, the other stages are idle when they can process some other instruction to reduce clock cycles.

## Pipelined Processor
The main aim of a pipelined architecture is to reduce the amount clock cycles taken to execute one program in its entirety. The pipelined processor consists of 4 pipelined registers which help to keep information about previous instruction control signals saved to prevent any case of control/data hazard. At the same time, it keeps all the stages engaged in processing some instruction.
