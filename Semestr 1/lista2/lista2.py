import time

sentence = 'Lorem ipsum dolor'
c = 'm'

# Zadanie 2
print("Zadanie 2:")
print([pos for pos, char in enumerate(sentence) if char == c])

# Zadanie 3
print('Zadanie 3: ')
position = 5
print([pos+position for pos, char in enumerate(sentence[position:]) if char == c])

# Zadanie 4
print('Zadanie 4: ')
start_time = time.time()
count = 0
for i in range(0, 100000):
    for i in sentence:
        if i == 'm':
            count+= 1
print(count)
end_time = time.time()
print("--- %s seconds ---" % (end_time - start_time))

# Zadanie 5
print('Zadanie 5:')
s = 'm'
start_time = time.time()
for i in range(0, 100000):
    sentence.count(s)
end_time = time.time()
print("--- %s seconds ---" % (end_time - start_time))

# Zadanie 6
print('Zadanie 6: ')
str1 = 'Ala ma kota'
str2 = 'Kot ma mopa'
def compare(a, b):
    c = 1
    for x, y in zip(a, b):
        if x == y:
            print('%i znak taki sam: %c' % (c,x))
        else:
            print('%i różnią się: [%c, %c] ' % (c,x,y))
        c+= 1
compare(str1, str2)

# Zadanie 7
print('Zadanie 7:')
def fibonnaci(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonnaci(n-1) + fibonnaci(n-2)
n = 15
for i in range(0,n):
    print(fibonnaci(i))