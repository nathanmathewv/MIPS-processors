from src import mipsRegisters
from src import regMemory
from src import memAddress

ifIDDef={"instruction":None}        #pipeline registers
idEXDef={"rs":None,"rt":None,"rd":None,"imm":None,"pc":None,"lineAddress":None,"regDst":None,"regWrite":None,"jump":None,
      "branch":None,"memRead":None,"memToReg":None,"aluOp":None,"MemWrite":None,"aluSrc":None}
exMEMDef={"rd":None,"rt":None,"alu":None,"regDst":None,"regWrite":None,"jump":None,"branch":None,
       "memRead":None,"memToReg":None,"aluOp":None,"MemWrite":None,"aluSrc":None}
memWBDef={"rd":None,"rt":None,"alu":None,"regDst":None,"regWrite":None,"jump":None,"branch":None,
        "memRead":None,"memToReg":None,"aluOp":None,"MemWrite":None,"aluSrc":None}
ifID=ifIDDef
idEX=idEXDef
exMEM=exMEMDef
memWB=memWBDef

def clock():                #clock function to increment time everytime
    global clk
    clk+=1

def flushIFID():                        #flush function
    global ifID                         #resets all 
    ifID=ifIDDef.copy()                 #ifID gets reset to default dictionary ifIDDef

def flushIDEX():                        #flush function
    global idEX                         #resets all 
    idEX=idEXDef.copy()                 #idEX gets reset to default dictionary idEXDef


def flushEXMEM():                       #flush function
    global exMEM                        #resets all 
    exMEM=exMEMDef.copy()                  #exMEM gets reset to default dictionary exMEMDef


def forwardFromReg():
    global regMemory,stall
    if exMEM["regDst"] and (exMEM["rd"]==idEX["rt"] or exMEM["rd"]==idEX["rs"]) and exMEM["regWrite"]:
        if exMEM["rd"]==idEX["rt"]:
            idEX["rtDat"]=exMEM["alu"]
        if exMEM["rd"]==idEX["rs"]:
            idEX["rsDat"]=exMEM["alu"]
    elif memWB["regDst"] and (memWB["rd"]==idEX["rt"] or memWB["rd"]==idEX["rs"]) and memWB["regWrite"]:
        if memWB["rd"]==idEX["rt"]:
            idEX["rtDat"]=memWB["alu"]
        if memWB["rd"]==idEX["rs"]:
            idEX["rsDat"]=memWB["alu"]
    if not exMEM["regDst"] and (exMEM["rt"]==idEX["rt"] or exMEM["rt"]==idEX["rs"]) and exMEM["regWrite"]:
        if exMEM["memToReg"]:
            if exMEM["rt"]==idEX["rt"]:
                idEX["rtDat"]=exMEM["alu"]
            if exMEM["rt"]==idEX["rs"]:
                idEX["rsDat"]=exMEM["alu"]
        else:
            stall=1
    elif not memWB["regDst"] and (memWB["rt"]==idEX["rt"] or memWB["rt"]==idEX["rs"]) and memWB["regWrite"]:
        if memWB["rt"]==idEX["rt"]:
            idEX["rtDat"]=memWB["alu"]
        if memWB["rt"]==idEX["rs"]:
            idEX["rsDat"]=memWB["alu"]

def instructionFetch():
    global pc, ifID
    instruction=pc
    pc+=4                                   #the funtion increments by 4 i.e. it gets the next instruction
    ifID["instruction"]=instruction

def instructionDecode():            #function to decode the type of instruction
    global idEX
    flushIDEX()
    instruction=instructionQueue[0]
    rs=instruction[6:11]                    #fetching rs
    rt=instruction[11:16]                   #fetching rt
    if instruction[:6]=="000000":           #condition for  r type
        idEX["regDst"]=1
        idEX["regWrite"]=1
        rd=instruction[16:21]
        if instruction[26:]=="100000":          #condition for add
            idEX["aluOp"]="010"
        elif instruction[26:]=="100010":            #condition for subtraction
            idEX["aluOp"]="110"
        elif instruction[26:]=="101010":         #condiiton for set less than
            idEX["aluOp"]="111"
        idEX["rs"]=rs
        idEX["rt"]=rt
        idEX["rd"]=rd
        idEX["rsDat"]=regMemory[rs]
        idEX["rtDat"]=regMemory[rt]
    else:                                       #else not r type
        imm = int(instruction[16:],2)
        if instruction[:6]=="001000":               #condition for add immediete
            idEX["aluSrc"]=1
            idEX["regWrite"]=1

        elif instruction[:6]=="100011":             #coondition for load word lw
            idEX["aluSrc"]=1
            idEX["memToReg"]=1
            idEX["regWrite"]=1
            idEX["memRead"]=1
            idEX["aluOp"]="010"

        elif instruction[:6]=="101011":             #condition for store word 
            idEX["aluSrc"]=1
            idEX["MemWrite"]=1
            idEX["aluOp"]="010"
        
        elif instruction[:6]=="000100":             #condition for branch
            idEX["branch"]=1
            idEX["aluOp"]="110"
            if instruction[16]=="1":
                imm=imm-0x10000
        idEX["rs"]=rs
        idEX["rt"]=rt
        idEX["imm"]=imm
        idEX["rsDat"]=regMemory[rs]
        idEX["rtDat"]=regMemory[rt]
        idEX["pc"]=ifID["instruction"]

    if instruction[:6]=="000010":                        #checking condiiton for jump
        idEX["jump"]=1
        lineAddress = int(instruction[6:],2)
        idEX["lineAddress"]=lineAddress

def execute():
    global pc, exMEM, branchedOrJump
    alu = 0
    
    if not idEX["jump"]:
        if idEX["regDst"]:                      # r format
            if idEX["aluOp"] == "010":              #add
                alu = idEX["rsDat"] + idEX["rtDat"]
            elif idEX["aluOp"] == "110":
                alu = idEX["rsDat"] - idEX["rtDat"]                 #subtract
            else:
                alu = int(idEX["rsDat"] < idEX["rtDat"])
            exMEM["rd"] = idEX["rd"]
        else:  # i format
            if idEX["branch"] and idEX["rsDat"] == idEX["rtDat"]:
                pc = idEX["pc"]+((idEX["imm"])+1)* 4
                branchedOrJump=True
            elif idEX["aluOp"] == "010" and idEX["aluSrc"]:  # load word or store word
                alu = idEX["imm"] + idEX["rsDat"]
            elif idEX["aluSrc"] and idEX["regWrite"] and not idEX["memToReg"]:  # addi
                alu = idEX["rsDat"] + idEX["imm"]
        exMEM["rt"] = idEX["rt"]
        exMEM["alu"] = alu


    else:  # j format
        pc = idEX["lineAddress"] * 4
        branchedOrJump=True


    exMEM["regDst"] = idEX["regDst"]
    exMEM["regWrite"] = idEX["regWrite"]
    exMEM["jump"] = idEX["jump"]
    exMEM["branch"] = idEX["branch"]
    exMEM["memRead"] = idEX["memRead"]
    exMEM["memToReg"] = idEX["memToReg"]
    exMEM["aluOp"] = idEX["aluOp"]
    exMEM["MemWrite"] = idEX["MemWrite"]
    exMEM["aluSrc"] = idEX["aluSrc"]
    

def memoryrw():                         # the memoryrw function basically executes the store word function
    global memWB
    if exMEM["MemWrite"]:                   #sw
        memAddress[exMEM["alu"]]=regMemory[exMEM["rt"]]             #write into the memory
    if exMEM["memRead"]:
        memWB["loadIntoReg"]=memAddress[exMEM["alu"]]               # read from memory
    if exMEM["regDst"]:
        memWB["rd"]=exMEM["rd"]
    
    memWB["alu"]=exMEM["alu"]
    memWB["rt"]=exMEM["rt"]
    memWB["regDst"] = exMEM["regDst"]
    memWB["regWrite"] = exMEM["regWrite"]
    memWB["jump"] = exMEM["jump"]
    memWB["branch"] = exMEM["branch"]
    memWB["memRead"] = exMEM["memRead"]
    memWB["memToReg"] = exMEM["memToReg"]
    memWB["aluOp"] = exMEM["aluOp"]
    memWB["MemWrite"] = exMEM["MemWrite"]
    memWB["aluSrc"] = exMEM["aluSrc"]


def writeBack():
    if memWB["regDst"]:
        regMemory[memWB["rd"]]=memWB["alu"]
    elif memWB["aluSrc"] and memWB["regWrite"] and not memWB["memToReg"]:#addi
        regMemory[memWB["rt"]]=memWB["alu"]
    elif memWB["regWrite"]:#lw or sw
        regMemory[memWB["rt"]]=memWB["loadIntoReg"]             #load word from the memory
            


factorialCodeFile=open("FactorialCode.txt","r")
factorialCode=factorialCodeFile.readlines()
fiboFile=open("fibo.txt","r")
fibo=fiboFile.readlines()

code=[]
for i in factorialCode:
    code+=[i.rstrip("\n")]

instructionQueue=[None]*5
global clk,pc
clk=0
pc=4194304
global branchedOrJump
branchedOrJump=False

while (True):
    forwardFromReg()
    if (instructionQueue[3]!=None):
        writeBack()
    if (instructionQueue[2]!=None):
        memoryrw()
    if (instructionQueue[1]!=None):
        execute()
    if (instructionQueue[0]!=None):
        instructionDecode()
    instructionFetch()
    i=ifID["instruction"]
    
    if branchedOrJump:
            flushIFID()
            flushIDEX()
            flushEXMEM()
            instructionQueue[0]=None
            instructionQueue[1]=None
            branchedOrJump=False
            
    if int((i-4194304)/4)<len(code):
        instructionQueue.insert(0,code[int((i-4194304)/4)])
    else:
        instructionQueue.insert(0,None)
    instructionQueue.pop()
    if instructionQueue.count(None)==5:
        break
    clock()

print("----------Register Memory----------")
for i in range(len(regMemory)):
    print(f"{mipsRegisters[2*i+1]} : {regMemory[mipsRegisters[2*i]]}")
print()

print("----------Data Memory----------")
print(memAddress)
print()

print(f'Code was executed in {clk} clock cycles')