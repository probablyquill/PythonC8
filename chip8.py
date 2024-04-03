import random

class Chip8:
    drawFlag = True

    #Opcode is an unsigned short integer
    opcode = 00

    #The Chip8 has 4k of memory.
    memory = [0] * 4096

    #The register is 15 8 bit general registers and a 16th register for the carry flag.
    registers = [0] * 16

    #I is index register and pc is the program counter.
    I = 0
    pc = 0x200

    #Timers that count at 60hz. They will count down to 0 if above 0.
    delay_timer = 0
    sound_timer = 0

    #The graphics system is black and white and uses a total of 2048 pixels in a 62x32 size.
    #0 will be off, 1 will be on.
    gfx = [0] * 2048

    #The stack will be used to remember locations before jumps. The system has 16 levels of stack and will
    #use a stack pointer to remever what level of the stack is being used.
    stack = [0] * 16
    sp = 0

    #Chip8 uses a Hex based keypad 0x0-0xF.
    key = [0] * 16

    chip8_fontset = [
        0xF0, 0x90, 0x90, 0x90, 0xF0,
        0x20, 0x60, 0x20, 0x20, 0x70,
        0xF0, 0x10, 0xF0, 0x80, 0xF0,
        0xF0, 0x10, 0xF0, 0x10, 0xF0,
        0x90, 0x90, 0xF0, 0x10, 0x10,
        0xF0, 0x80, 0xF0, 0x10, 0xF0,
        0xF0, 0x80, 0xF0, 0x90, 0xF0,
        0xF0, 0x10, 0x20, 0x40, 0x40,
        0xF0, 0x90, 0xF0, 0x90, 0xF0,
        0xF0, 0x90, 0xF0, 0x10, 0xF0,
        0xF0, 0x90, 0xF0, 0x90, 0x90,
        0xE0, 0x90, 0xE0, 0x90, 0xE0,
        0xF0, 0x80, 0x80, 0x80, 0xF0,
        0xE0, 0x90, 0x90, 0x90, 0xE0,
        0xF0, 0x80, 0xF0, 0x80, 0xF0,
        0xF0, 0x80, 0xF0, 0x80, 0x80
    ]

    def initialize(self):
        self.pc = 0x200
        self.opcode = 0
        self.I = 0
        self.sp = 0

        #Clear display, stack, registers, and memory.

        for i in range(80):
            self.memory[i + 50] = self.chip8_fontset[i]

    
    def loadGame(self, rom):
        bufferSize = len(rom)

        for i in range(bufferSize):
            self.memory[i + 512] = rom[i]
        
    
    #Fetch, decode, execute one opcode.
    def emulateCycle(self):
        #Fetch opcode
        self.opcode = (int(self.memory[self.pc]) << 8) | int(self.memory[self.pc + 1])
        #print(f"Starting: I = {self.I} PC = {self.pc}")
        #print(f"Loaded opcode: {hex(self.opcode)}")
        #Decode Opcode

        #This website was incredibly useful.
        #http://devernay.free.fr/hacks/chip8/C8TECH10.HTM

        #0x0XYN
        #0x0XNN
        #0x0NNN
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        n = (self.opcode & 0x000F)
        nn = self.opcode & 0x00FF
        nnn = self.opcode & 0x0FFF

        match (self.opcode & 0xF000):  
            case 0x0000:
                match (n):
                    case 0x0000: #0x00E0 Clears the screen
                        self.gfx.clear()
                        self.gfx = [0] * 2048
                        self.drawFlag = True
                        self.pc += 2
                    
                    case 0x000E: #0x000E returns from subroutine
                        #not actually sure if this is enough to take it back one on the stack but idk
                        self.sp -= 1
                        self.pc = self.stack[self.sp]
                        self.pc += 2

                    case _: #0x0NNN or Unrecognized
                        print("Unrecognized instruciton or call machine code routine triggered.")
                        print(f"Instruction: {hex(self.opcode)}")

            case 0x1000: #0x1NNN
                self.pc = nnn

            case 0x2000: #0x2NNN Might be wrong please check later 
                self.stack[self.sp] = self.pc
                self.sp += 1
                self.pc = int(nnn)

            case 0x3000: #0x3XNN
                if(self.registers[x] == nn):
                    self.pc += 4
                else:
                    self.pc += 2

            case 0x4000: #0x4XNN
                if(self.registers[x] != nn):
                    self.pc += 4
                else:
                    self.pc += 2
            
            case 0x5000: #0x5XY0
                if(self.registers[x] == self.registers[y]):
                    self.pc += 4
                else:
                    self.pc += 2

            case 0x6000: #0x6XNN
                self.registers[x] = nn
                self.pc += 2
            
            case 0x7000: #0x7XNN
                rx = self.registers[x]
                rx += nn

                if (rx > 255): rx = rx - 256

                self.registers[x] = rx
                self.pc += 2

            case 0x8000:
                match (self.opcode & 0x000F):
                    case 0x0000: #0x8XY0
                        self.registers[x] = self.registers[y]
                        self.pc += 2

                    case 0x0001: #0x8XY1
                        rx = self.registers[x]
                        ry = self.registers[y]
                        self.registers[x] = (rx | ry)
                        self.pc += 2

                    case 0x0002: #0x8XY2
                        rx = self.registers[x]
                        ry = self.registers[y]
                        self.registers[x] = (rx & ry)
                        self.pc += 2

                    case 0x0003: #0x8XY3
                        rx = self.registers[x]
                        ry = self.registers[y]
                        self.registers[x] = (rx ^ ry)
                        self.pc += 2

                    case 0x0004:
                        #8XY4 is an add operation, with N refering to one register and X refering to another.
                        #Checks before adding to see if it will overflow past 255.
                        rx = self.registers[x]
                        ry = self.registers[y]
                        rx = rx + ry

                        if (rx > 255):
                            rx = rx - 256
                            self.registers[x] = rx
                            self.registers[0xF] = 1 #Carry
                        else:
                            self.registers[x] = rx
                            self.registers[0xF] = 0 #No carry

                        self.pc += 2
                    
                    case 0x0005: #0x8XY5
                        #Subtract operation. If there will be underflow, the carry register is set to 1.
                        #Otherwise it will be set to 0.
                        rx = self.registers[x]
                        ry = self.registers[y]

                        rx = rx - ry

                        #ORDER MATTERS
                        #Register X needs to be set before the carry flag.
                        if (rx < 0):
                            rx += 256
                            self.registers[x] = rx
                            self.registers[0xF] = 0
                        else:
                            self.registers[x] = rx
                            self.registers[0xF] = 1

                        self.pc += 2

                    case 0x0006: #0x8XY6              
                        rx = self.registers[x]
                        temp = rx & 1

                        self.registers[x] = rx >> 1
                        self.registers[0xF] = temp

                        self.pc += 2

                    case 0x0007: #0x8XY7
                        rx = self.registers[x]
                        ry = self.registers[y]
                        rx = ry - rx

                        if (rx < 0):
                            rx += 256
                            self.registers[x] = rx
                            self.registers[0xF] = 0
                        else:
                            self.registers[x] = rx
                            self.registers[0xF] = 1

                        self.pc += 2

                    case 0x000E: #0x8XYE
                        rx = self.registers[x]
                        temp = (rx >> 7) & 1

                        rx = rx << 1
                        if (rx > 255): rx = rx - 256

                        self.registers[x] = rx
                        self.registers[0xF] = temp

                        self.pc += 2

                    case _:
                        ce = hex(self.opcode)
                        print(f"Unknown opcode: {ce}")
            
            case 0x9000: #0x9XY0
                if (self.registers[x] != self.registers[y]):
                    self.pc += 4
                else:
                    self.pc += 2

            case 0xA000: #0xANNN
                self.I = nnn
                self.pc += 2

            case 0xB000: #0xBNNN
                self.pc = self.registers[0x00] + nnn

            case 0xC000: #0xCXNN
                ran = random.randrange(255)
                #Sanity check to prevent overflow
                ran = (ran & 0x00FF)
                self.registers[x] = ran
                self.pc += 2

            case 0xD000:
                #DXYN -> Draws a sprite at coordinates VX VY with a width of 8 pixels and a height of N pixels.
                x = self.registers[x]
                y = self.registers[y]
                height = n

                self.registers[0xF] = 0
                for i in range(height):
                    pixel = self.memory[int(self.I + i)]

                    for j in range(8):
                        if ((pixel & (0x80 >> j)) != 0):
                            temp_location = ((x + j + ((y + i) * 64)))
                            #This isn't correct overflow handling and leads to inconsistencies / bugs.
                            #Since the rendering is tied to collision, this is probably the
                            #largest known issue at the moment.
                            if temp_location > 2047: temp_location = temp_location - 2048
                            if (self.gfx[temp_location] == 1): self.registers[0xF] = 1
                            self.gfx[temp_location] ^= 1

                self.drawFlag = True
                self.pc += 2
            
            case 0xE000:
                match (self.opcode & 0x00FF):
                    case 0x09E: #0xEX9E -> 0xE29E
                        checkKey = self.registers[x]
                        if (self.key[checkKey] > 0):
                            self.pc += 4
                        else:
                            self.pc += 2

                    case 0x0A1: #0xEXA1
                        checkKey = self.registers[x]
                        if (self.key[checkKey] > 0):
                            self.pc += 2
                        else:
                            self.pc += 4

                    case _:
                        ce = hex(self.opcode)
                        print(f"Unknown opcode: {ce}")


            case 0xF000:
                match (self.opcode & 0x00FF):
                    case 0x0007: #0xFX07
                        self.registers[x] = self.delay_timer
                        self.pc += 2

                    #This is potentially really problematic as I'm going to have to implement halting until a key is pressed.
                    #This works at the moment but it doesn't prevent the timer from ticking down.
                    case 0x000A: #0xFX0A
                        checkKey = self.registers[x]
                        if self.key[checkKey] > 0:
                            self.pc += 2

                    case 0x0015:
                        #Sets the delay timer to memory address VX.
                        self.delay_timer = self.registers[x]
                        self.pc += 2

                    case 0x0018:
                        #Sets the sound timer to memory address VX
                        self.sound_timer = self.registers[x]
                        self.pc += 2

                    case 0x001E: # 0xFX1E
                        self.I += self.registers[x]
                        self.pc += 2

                    case 0x0029: #0xFX29
                        self.I = self.registers[x]
                        self.pc += 2

                    #Need to find a good explanation for this. I took the logic from 
                    #Octo but I don't fully understand what this is doing.
                    case 0x0033: #0xFX33
                        x = self.registers[x]
                        self.memory[self.I] = int((x / 100) % 10)
                        self.memory[self.I + 1] =int((x / 10) % 10)
                        self.memory[self.I + 2] = int(x % 10)

                        self.pc += 2
                    
                    case 0x055: #0xFX55
                        for i in range(x + 1):
                            self.memory[self.I + i] = self.registers[i]
                        
                        self.pc += 2

                    case 0x0065: #0xFX65
                        for i in range(x + 1):
                            self.registers[i] = self.memory[self.I + i]
                        
                        self.pc += 2

                    case _:
                        ce = hex(self.opcode)
                        print(f"Unknown opcode: {ce}")
                        self.pc += 2

            case _:
                ce = hex(self.opcode)
                print(f"Unknown opcode: {ce}")
        
        if (self.delay_timer > 0):
            self.delay_timer -= 1
        if (self.sound_timer > 0):
            if (self.sound_timer == 1):
                print("Beep")
            self.sound_timer -= 1
        
        #Execute Opcode
        #print(f"Executed opcode: {hex(self.opcode)} resulting in {self.registers}")
        #print(f"I = {self.I} PC = {self.pc}\n")