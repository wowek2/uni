import math
import datetime   
#   Zadanie 1
print("Zadanie 1:")
print(5)
x = 5
print(x+1)

#   Zadanie 2
print("Zadanie 2:")
szer = 13
wys = 12
znak = '.'
print("szer/2: ", szer/2)
print("szer/2.0: ", szer/2.0)
print("wys/3: ", wys/3)
print("znak * 5: ", znak * 5)
print("znak + 5: nie skompiluje, to nie javascript (ewentualnie rzutować typ: znak + str(5))")

#   Zadanie 3
print("Zadanie 3")
radius = 5
sphere_volume = 4/3*math.pi*radius**3
print("Objętość kuli o promienu r=5cm: %s [cm]" % (round(sphere_volume,2)))

#   Zadanie 4
r = int(input("Podaj promień kuli: "))

def sphereVolume(r: float):
    """ 
    Returns sphere volume based on the radius - r
    """
    return (4/3*math.pi*r**3)

print("Objętość kuli o zadanym promieniu wynosi: %s [cm]" % round(sphereVolume(r),2)) 

#Zadanie 5
print("Zadanie 5")
input = [
    ["6:15", "4:12", "6:15"],   #   Tempo [mm:ss/km]
    [1.5, 4.8, 1],              #   Dystans
    "6:52:00"                   #   Godzina początkowa [hh:mm:ss]
]

def get_sec(time):
    """Get seconds from hh:mm:ss format"""
    if time.count(':') == 1:
        m, s = time.split(':')
        h = 0
    else:
        h, m, s = time.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def format_seconds_to_hhmmss(ss):
    """Convert seconds to hh:mm:ss format"""
    hh = ss // (3600)
    ss %= (3600)
    mm = ss // 60
    ss %= 60
    return "%02i:%02i:%02i" % (hh, mm, ss)

input[0] = list(map(get_sec, input[0])) # konwersja tempa z formatu mm:ss na s

elapsed_time = sum(t*d for t, d in zip(input[0], input[1])) # całkowity czas biegu w sekundach

print("Godzina powrotu z biegu to:", 
      format_seconds_to_hhmmss(
        get_sec(input[2]) + elapsed_time))

# Zadanie 6
print("Zadanie :")
count = [1,3,5,3,5,3,5,1,1]
for i in count:
    print('*' * i)

# Zadanie 7
print("Zadanie 7: ")

print('  ----')
print('@/ ,. \@')
print('( \__/ )')
print(' \__U_/')