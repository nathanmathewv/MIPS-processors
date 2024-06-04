from src import mipsRegisters
from src import regMemory
from src import memAddress

controlSignals={
    "regDst":0,
    "regWrite":0,
    "jump":0,
    "branch":0,
    "memRead":0,
    "memToReg":0,
    "aluOp":"000",
    "MemWrite":0,
    "aluSrc":0,
}

def clock():
    global clk
    clk+=1

def resetSignals():
    global controlSignals
    controlSignals["regDst"]=0
    controlSignals["regWrite"]=0
    controlSignals["jump"]=0
    controlSignals["branch"]=0
    controlSignals["memRead"]=0
    controlSignals["memToReg"]=0
    controlSignals["aluOp"]="000"
    controlSignals["MemWrite"]=0
    controlSignals["aluSrc"]=0

def instructionFetch():
    global pc
    instruction=pc
    pc+=4
    return instruction

def instructionDecode(instruction):
    global controlSignals,rs,rt,rdDat,rsDat,rtDat
    resetSignals()
    rs=instruction[6:11]
    rt=instruction[11:16]
    if instruction[:6]=="000000":
        controlSignals["regDst"]=1
        controlSignals["regWrite"]=1
        global rd
        rd=instruction[16:21]
        if instruction[26:]=="100000":#add
            controlSignals["aluOp"]="010"
        elif instruction[26:]=="100010":#sub
            controlSignals["aluOp"]="110"
        elif instruction[26:]=="101010":#slt
            controlSignals["aluOp"]="111"
        rsDat=regMemory[rs]
        rtDat=regMemory[rt]
        rdDat=regMemory[rd]
    else:
        global imm,immDat
        imm = int(instruction[16:],2)
        if instruction[:6]=="001000":#addi
            controlSignals["aluSrc"]=1
            controlSignals["regWrite"]=1

        elif instruction[:6]=="100011":#lw
            controlSignals["aluSrc"]=1
            controlSignals["memToReg"]=1
            controlSignals["regWrite"]=1
            controlSignals["memRead"]=1
            controlSignals["aluOp"]="010"

        elif instruction[:6]=="101011":#sw
            controlSignals["aluSrc"]=1
            controlSignals["MemWrite"]=1
            controlSignals["aluOp"]="010"
        
        elif instruction[:6]=="000100":#branch
            controlSignals["branch"]=1
            controlSignals["aluOp"]="110"
            if instruction[16]=="1":
                imm=imm-0x10000
        immDat=imm
        rsDat=regMemory[rs]
        rtDat=regMemory[rt]

    if instruction[:6]=="000010":#jump
        controlSignals["jump"]=1
        global lineAddress
        lineAddress = int(instruction[6:],2)


def execute():
    global pc
    alu=0
    if not controlSignals["jump"]: 
        if controlSignals["regDst"]: # r format
            if controlSignals["aluOp"]=="010":
                alu=rsDat+rtDat
            elif controlSignals["aluOp"]=="110":
                alu=rsDat-rtDat
            else:
                alu=int(rsDat<rtDat)
        else: # i format 
            if controlSignals["branch"] and rsDat==rtDat:
                pc+=(immDat)*4

            elif controlSignals["aluOp"]=="010" and controlSignals["aluSrc"]:#load word or store word
                alu=immDat+rsDat

            elif controlSignals["aluSrc"] and controlSignals["regWrite"] and not controlSignals["memToReg"]:#addi
                alu=rsDat+immDat

    else:#j format
        pc=lineAddress*4
    return alu

def memoryrw(alu):
    if controlSignals["MemWrite"]:#sw
        memAddress[alu]=regMemory[rt]
    if controlSignals["memRead"]:
        global loadIntoReg
        loadIntoReg=memAddress[alu]

def writeBack(alu):
    if controlSignals["regDst"]:
        regMemory[rd]=alu
    elif controlSignals["aluSrc"] and controlSignals["regWrite"] and not controlSignals["memToReg"]:#addi
        regMemory[rt]=alu
    elif controlSignals["regWrite"]:#lw
        regMemory[rt]=loadIntoReg
            


factorialCodeFile=open("FactorialCode.txt","r")
factorialCode=factorialCodeFile.readlines()
fiboCodeFile=open("fibo.txt","r")
fiboCode=fiboCodeFile.readlines()

code=[]
for i in fiboCode:
    code+=[i.rstrip("\n")]

global clk,pc
clk=0
pc=4194304

while True:
    i=instructionFetch()
    if int((i-4194304)/4)<len(code):
        instruction=code[int((i-4194304)/4)]
        instructionDecode(instruction)
        temp=execute()
        memoryrw(temp)
        writeBack(temp)
        clock()
    else:
        break

print("----------Register Memory----------")
for i in range(len(regMemory)):
    print(f"{mipsRegisters[2*i+1]} : {regMemory[mipsRegisters[2*i]]}")
print()

print("----------Data Memory----------")
print(memAddress)
print()

print(f'Code was compiled in {clk} clock cycles')