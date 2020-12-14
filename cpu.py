"""CPU functionality."""

SP = 7 # Stack Pointer 
HLT = 0b00000001 # Halt
PRN = 0b01000111 # Print
LDI = 0b10000010 # Load Immediate
MUL = 0b10100010 # Multiply
PUSH = 0b01000101 # Push
POP = 0b01000110 # Pop
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JEQ = 0b01010101
JNE = 0b01010110
JMP = 0b01010100

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.reg[SP] = 0xF4
        self.pc = 0
        # self.halted = False
        self.flag = 0

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, new_value):
        self.ram[address] = new_value

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        # open file
        with open(filename) as my_file:
            # go through each line to parse and get the instruction
            for line in my_file:
                # try to get instruction/operand in the line
                comment_split = line.split('#')
                maybe_binary_number = comment_split[0]
                try:
                    x = int(maybe_binary_number, 2)
                    self.ram_write(x, address)
                    address += 1
                except:
                    print("Error writing instruction")

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            self.flag = 0b00000000
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while not self.halted:
            instruction_to_execute = self.ram_read(self.pc)
            operand_A = self.ram_read(self.pc + 1)
            operand_B = self.ram_read(self.pc + 2)
            self.execute_instruction(instruction_to_execute, operand_A, operand_B)

    def execute_instruction(self, operand_A, operand_B, instruction):
        if instruction == HLT:
            self.halted = True
            self.pc += 1
        elif instruction == PRN:
            print(self.reg[operand_A])
            self.pc += 2
        elif instruction == LDI:
            self.reg[operand_A] = operand_B
            self.pc += 3
        elif instruction == MUL:
            self.reg[operand_A] *= self.reg[operand_B]
            self.pc += 3
        elif instruction == PUSH:
            # decrement stack pointer by 1
            self.reg[SP] -= 1
            # gather register number for push
            reg_number = self.ram_read(self.pc + 1)
            # make value equal to register number where stack pointer is
            reg_value = self.reg[reg_number]
            # address is equal to register stack pointer
            address = self.reg[SP]
            # put the value at the given address
            self.ram[address] = reg_value
            self.pc += 2
        elif instruction == POP:
            number_to_pop_in = self.ram_read(self.pc + 1)
            address = self.reg[SP]
            pop_value = self.reg[number_to_pop_in]
            self.reg[number_to_pop_in] = pop_value
            self.reg[SP] += 1
            self.pc += 2
        elif instruction == CMP:
            self.alu("CMP", operand_A, operand_B)
        elif instruction == JEQ:
            if self.flag & 0b1 == 1:
                self.pc = self.reg[operand_A]
            else:
                self.pc += 2
        elif instruction == JMP:
            self.pc = self.reg[operand_A]
        elif instruction == JNE:
            if self.flag  & 0b1 == 0:
                self.pc = self.reg[operand_A]
            else:
                self.pc += 2
        elif instruction == CALL:
            self.reg[SP] -= 1
            self.ram[self.reg[SP]] = self.pc + 2
            self.pc = self.reg[operand_A]
        elif instruction == RET:
            self.pc = self.ram[self.reg[SP]]
            self.reg[SP] += 1
        elif instruction == ADD:
            self.alu("ADD", operand_A, operand_B)
        else:
            print("Invalid instruction")