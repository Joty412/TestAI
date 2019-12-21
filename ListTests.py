

# Phases    123456789ABC
phases = [0b001100001100,
          0b100001100001,
          0b000011000011,
          0b011000010001,
          0b000000001111,
          0b000001111000,
          0b111000000001,
          0b000001001011,
          0b001001011000,
          0b001011000001,
          0b011000001001,
          0b001001001001,
          0b000000000000]

# to red
print(bin(phases[12] & ~ phases[2]))
# to green
print(bin(phases[2] & ~ phases[12]))

test = str(bin(phases[0]))
print([bool(phases[2] & (1 << n)) for n in range(11, -1, -1)])

a = 4
a = False
if not a:
    print("a")
