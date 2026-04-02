import random

# Два сегмента динамической памяти
seg1, seg2 = [], []  # seg1 - вещественные, seg2 - целые

# Статический сегмент (хранит указатели)
mem = {}  # {id: [сегмент, индекс, размер, данные]}

def new_ptr(size, typ=None):
    """Создаёт новый указатель"""
    seg = seg1 if typ == float else seg2
    data = [0.0]*size if typ == float else [0]*size
    seg.append(data)
    pid = id(seg[-1])
    mem[pid] = [seg, len(seg)-1, size, seg[-1]]
    return pid

def realloc_ptr(pid, new_size):
    """Повторное выделение памяти (с утечкой)"""
    if pid not in mem:
        return None
    
    # ДЕМОНСТРАЦИЯ УТЕЧКИ: не освобождаем старую память
    old_info = mem[pid]
    old_seg = old_info[0]
    old_idx = old_info[1]
    old_data = old_info[3]
    
    # Создаём новый массив
    typ = float if isinstance(old_data[0], float) else int
    new_seg = seg1 if typ == float else seg2
    new_data = [0.0]*new_size if typ == float else [0]*new_size
    new_seg.append(new_data)
    new_pid = id(new_seg[-1])
    
    # Обновляем указатель на новую память
    mem[pid] = [new_seg, len(new_seg)-1, new_size, new_seg[-1]]
    
    
    print(f"старая память (размер {old_info[2]}) потеряна")
    
    return pid

def write(pid, idx, val):
    if pid not in mem: return
    if 0 <= idx < mem[pid][2]:
        mem[pid][3][idx] = val

def read(pid, idx):
    if pid not in mem or mem[pid][3] is None: return None
    return mem[pid][3][idx] if 0 <= idx < mem[pid][2] else None

def copy(dst, src):
    if dst in mem and src in mem and mem[dst][2] == mem[src][2]:
        for i in range(mem[dst][2]):
            mem[dst][3][i] = mem[src][3][i]

def free(pid):
    if pid in mem:
        seg, idx = mem[pid][0], mem[pid][1]
        if 0 <= idx < len(seg): 
            del seg[idx]
        del mem[pid]
        print(f"   Память по указателю {pid} освобождена")

# Ввод с проверкой
def inp(msg, cast, cond=None):
    while True:
        try:
            x = cast(input(msg))
            if cond and not cond(x): 
                print("Ошибка!")
            else: 
                return x
        except: 
            print("Ошибка!")

# ========== ЗАДАНИЕ 1 ==========
n1 = inp("Размер вещественного массива: ", int, lambda x: x>0)
p1 = new_ptr(n1, float)
for i in range(n1):
    write(p1, i, round(random.uniform(-10,10), 2))

print("Массив:", [read(p1,i) for i in range(n1)])

# Поиск последнего отрицательного
last = -1
for i in range(n1):
    val = read(p1,i)
    if val is not None and val < 0:
        last = i

# Сумма целых частей после последнего отрицательного
s = 0
for i in range(last+1, n1):
    val = read(p1,i)
    if val is not None:
        s += int(val)
print("Сумма целых частей после последнего отрицательного:", s if last!=-1 else 0)

# ========== ЗАДАНИЕ 2 ==========
n2 = inp("Размер целого массива: ", int, lambda x: x>0)
p2 = new_ptr(n2, int)
for i in range(n2):
    write(p2, i, random.randint(-100,100))

print("Массив:", [read(p2,i) for i in range(n2)])

# Максимальный элемент
mx = read(p2,0)
for i in range(1,n2):
    v = read(p2,i)
    if v is not None and v > mx: 
        mx = v
print("Максимальный элемент:", mx)


print("\n -Демонстрация- ")

# 1. NewPointer с утечкой (используем realloc_ptr)
print("\n1. Демонстрация утечки памяти:")
leak = new_ptr(3, float)
print(f"   Создан указатель {leak} на массив из 3 элементов")
print(f"   Данные в старом массиве: {[read(leak,i) for i in range(3)]}")
realloc_ptr(leak, 5)  # повторное выделение - утечка!
print(f"   Указатель {leak} теперь указывает на массив из 5 элементов")
print(f"   Старый массив из 3 элементов потерян навсегда")

# 2. SetPointer (копирование)
print("\n2. SetPointer (копирование данных):")
p3 = new_ptr(n1, float)
copy(p3, p1)
print(f"   Данные скопированы из p1 в p3")
print(f"   p1[0] = {read(p1,0)}, p3[0] = {read(p3,0)}")

# 3. ReadPointer (обработка NULL)
print("\n3. ReadPointer (обработка NULL):")
print(f"   Чтение по несуществующему указателю: {read(999999, 0)}")

# 4. FreePointer
print("\n4. FreePointer (освобождение памяти):")
free(p3)
print(f"   Попытка прочитать p3 после освобождения: {read(p3, 0)}")