# This Python file uses the following encoding: utf-8
import os
import string
from pathlib import Path
import sys
import re
from PySide6.QtGui import QPalette, QBrush, QPixmap
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtUiTools import QUiLoader

import threading
import random

# 加密S盒
S_he = [[9, 4, 10, 11],
        [13, 1, 8, 5],
        [6, 2, 0, 3],
        [12, 14, 15, 7]]

# 解密S盒
S_he_ni = [[10, 5, 9, 11],
           [1, 7, 8, 15],
           [6, 0, 2, 3],
           [12, 4, 13, 14]]

# 替换盒
replace_he = [[0, 0, 0, 0],
              [0, 0, 0, 1],
              [0, 0, 1, 0],
              [0, 0, 1, 1],
              [0, 1, 0, 0],
              [0, 1, 0, 1],
              [0, 1, 1, 0],
              [0, 1, 1, 1],
              [1, 0, 0, 0],
              [1, 0, 0, 1],
              [1, 0, 1, 0],
              [1, 0, 1, 1],
              [1, 1, 0, 0],
              [1, 1, 0, 1],
              [1, 1, 1, 0],
              [1, 1, 1, 1]]
# 定义两个轮常数
Rc1 = [1, 0, 0, 0, 0, 0, 0, 0]
Rc2 = [0, 0, 1, 1, 0, 0, 0, 0]


# 异或运算
def exclusive_or(x, y):
    length = len(x)
    result = []
    if length == 4:
        result = [0] * 4
        for i in range(4):
            result[i] = x[i] ^ y[i]
    elif length == 8:
        result = [0] * 8
        for i in range(8):
            result[i] = x[i] ^ y[i]
    elif length == 16:
        result = [0] * 16
        for i in range(16):
            result[i] = x[i] ^ y[i]

    return result

# 将数字字符串改为数组
def string_list(input):
    data_list = re.split(r'\D+', input)  # 根据非数字字符分割字符串

    # 将列表中的字符串转换为整数
    data_list = [int(item) for item in data_list if item]  # 过滤空字符串

    return data_list

# S盒替换
def S_replace(w):
    t1 = w[0] * 2 + w[1]
    t2 = w[2] * 2 + w[3]
    t3 = w[4] * 2 + w[5]
    t4 = w[6] * 2 + w[7]

    rep1 = S_he[t1][t2]
    rep2 = S_he[t3][t4]

    for i in range(4):
        w[i] = replace_he[rep1][i]
        w[i + 4] = replace_he[rep2][i]


# S盒逆替换
def S_replace_ni(w):
    t1 = w[0] * 2 + w[1]
    t2 = w[2] * 2 + w[3]
    t3 = w[4] * 2 + w[5]
    t4 = w[6] * 2 + w[7]

    rep1 = S_he_ni[t1][t2]
    rep2 = S_he_ni[t3][t4]

    for i in range(4):
        w[i] = replace_he[rep1][i]
        w[i + 4] = replace_he[rep2][i]


# g函数
# w表示要作g变换的列表，iter表示当前的变换轮数
def g(w, iter):
    wt = [0] * 8
    for i in range(8):
        wt[i] = w[i]

    for i in range(4):
        temp = wt[i + 4]
        wt[i + 4] = wt[i]
        wt[i] = temp

    S_replace(wt)

    if iter == 1:
        wt = exclusive_or(wt, Rc1)
    else:
        wt = exclusive_or(wt, Rc2)

    return wt


# 密钥扩展
def key_update(key, iter):
    wg = g(key[1], iter)

    w3 = exclusive_or(key[0], wg)
    w4 = exclusive_or(key[1], w3)

    new_key = [w3, w4]

    return new_key


# 分割明文为两部分
def split_data(data):
    data_length = len(data)

    middle = data_length // 2

    left_data = data[:middle]
    right_data = data[middle:]

    return left_data, right_data


# 乘法分步
def multiply_step(x, a):
    if a[0] == 0:
        for i in range(3):
            x[i] = a[i + 1]
    else:
        x[1] = a[2]
        x[2] = 0 if a[3] == 1 else 1
        x[3] = 1


# 二维数据的乘法
def multiply(a, b):
    result = [0] * 4
    x1 = [0] * 4
    multiply_step(x1, a)
    x2 = [0] * 4
    multiply_step(x2, x1)
    x3 = [0] * 4
    multiply_step(x3, x2)

    if b[0] == 1:
        for i in range(4):
            result[i] ^= x3[i]
    if b[1] == 1:
        for i in range(4):
            result[i] ^= x2[i]
    if b[2] == 1:
        for i in range(4):
            result[i] ^= x1[i]
    if b[3] == 1:
        for i in range(4):
            result[i] ^= a[i]

    return result


# 行移位
def hangyiwei(mingwen):
    for i in range(4, 8):
        temp = mingwen[0][i]
        mingwen[0][i] = mingwen[1][i]
        mingwen[1][i] = temp


# 列混淆
def liehunxiao(mingwen):
    function_matrix = [0, 1, 0, 0]
    s0_0 = []
    s1_0 = []
    s0_1 = []
    s1_1 = []

    for i in range(4):
        s0_0.append(mingwen[0][i])
        s1_0.append(mingwen[0][i + 4])
        s0_1.append(mingwen[1][i])
        s1_1.append(mingwen[1][i + 4])

    s1_00 = exclusive_or(s0_0, multiply(function_matrix, s1_0))
    s1_10 = exclusive_or(multiply(function_matrix, s0_0), s1_0)
    s1_01 = exclusive_or(s0_1, multiply(function_matrix, s1_1))
    s1_11 = exclusive_or(multiply(function_matrix, s0_1), s1_1)

    for i in range(4):
        mingwen[0][i] = s1_00[i]
        mingwen[0][i + 4] = s1_10[i]
        mingwen[1][i] = s1_01[i]
        mingwen[1][i + 4] = s1_11[i]


# 列混淆逆
def liehunxiao_ni(mingwen):
    function_matrix_1 = [1, 0, 0, 1]
    function_matrix_2 = [0, 0, 1, 0]
    s0_0 = []
    s1_0 = []
    s0_1 = []
    s1_1 = []

    for i in range(4):
        s0_0.append(mingwen[0][i])
        s1_0.append(mingwen[0][i + 4])
        s0_1.append(mingwen[1][i])
        s1_1.append(mingwen[1][i + 4])

    s1_00 = exclusive_or(multiply(function_matrix_1, s0_0), multiply(function_matrix_2, s1_0))
    s1_10 = exclusive_or(multiply(function_matrix_2, s0_0), multiply(function_matrix_1, s1_0))
    s1_01 = exclusive_or(multiply(function_matrix_1, s0_1), multiply(function_matrix_2, s1_1))
    s1_11 = exclusive_or(multiply(function_matrix_2, s0_1), multiply(function_matrix_1, s1_1))

    for i in range(4):
        mingwen[0][i] = s1_00[i]
        mingwen[0][i + 4] = s1_10[i]
        mingwen[1][i] = s1_01[i]
        mingwen[1][i + 4] = s1_11[i]


# 轮密钥加
def lunmiyaojia(mingwen, key):
    for i in range(2):
        for j in range(8):
            mingwen[i][j] ^= key[i][j]

# ---------------------------第1关---------------------------------
# 加密
def Encrypt(mingwen, key):
    mingwen_left, mingwen_right = split_data(mingwen)
    new_text = [mingwen_left, mingwen_right]
    key_left, key_right = split_data(key)
    new_key = [key_left, key_right]

    # 第0轮的轮密钥加
    lunmiyaojia(new_text, new_key)

    # 第一轮加密
    # 明文半字节代替
    S_replace(new_text[0])
    S_replace(new_text[1])
    # 明文的行移位
    hangyiwei(new_text)
    # 明文的列混淆
    liehunxiao(new_text)
    # 扩展密钥1
    key1 = key_update(new_key, 1)
    # 明文的轮密钥加
    lunmiyaojia(new_text, key1)

    # 第二轮加密
    # 明文半字节代替
    S_replace(new_text[0])
    S_replace(new_text[1])
    # 明文的行移位
    hangyiwei(new_text)
    # 扩展密钥2
    key2 = key_update(key1, 2)
    # 明文的轮密钥加
    lunmiyaojia(new_text, key2)

    # print(new_text)

    miwen = [0] * 16
    m = 0
    for i in range(2):
        for j in range(8):
            miwen[m] = new_text[i][j]
            m += 1

    return miwen


# 解密
def Decrypt(miwen, key):
    miwen_left, miwen_right = split_data(miwen)
    new_text = [miwen_left, miwen_right]
    key_left, key_right = split_data(key)
    new_key = [key_left, key_right]

    # 扩展密钥1
    key1 = key_update(new_key, 1)
    # 扩展密钥2
    key2 = key_update(key1, 2)

    # 第0轮轮密钥加
    lunmiyaojia(new_text, key2)

    # 第一轮解密
    # 逆行移位
    hangyiwei(new_text)
    # 逆半字节代替
    S_replace_ni(new_text[0])
    S_replace_ni(new_text[1])
    # 轮密钥加
    lunmiyaojia(new_text, key1)
    # 逆列混淆
    liehunxiao_ni(new_text)

    # 第二轮解密
    # 逆行移位
    hangyiwei(new_text)
    # 逆半字节代替
    S_replace_ni(new_text[0])
    S_replace_ni(new_text[1])
    # 轮密钥加
    lunmiyaojia(new_text, new_key)

    # print("text:", new_text)

    mingwen = [0] * 16
    m = 0
    for i in range(2):
        for j in range(8):
            mingwen[m] = new_text[i][j]
            m += 1

    return mingwen


text = [1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1]
key = [1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1]


# miwen = Encrypt(text, key)
# mingwen = Decrypt(miwen, key)

# ------------------------------------------------------------


# 将ASULL码转为二进制数
def bit_ascll(ascii_string, bit_num):
    if bit_num == 8:
        binary_string = ''.join(format(ord(char), '08b') for char in ascii_string)
        # 将二进制数位分开存入列表
        binary_list = [int(bit) for bit in binary_string]
    else:
        binary_string = ''.join(format(ord(char), '016b') for char in ascii_string)
        # 将二进制数位分开存入列表
        binary_list = [int(bit) for bit in binary_string]

    return binary_list


# 将二进制数转为ASCII码
def ascii_bit(binary_list, bit_num):
    # 将二进制列表转换为ASCII码
    ascii_string = ''
    if bit_num == 8:
        for i in range(0, len(binary_list), 8):
            byte = binary_list[i:i + 8]
            char = chr(int(''.join(str(bit) for bit in byte), 2))
            ascii_string += char
    else:
        for i in range(0, len(binary_list), 16):
            byte = binary_list[i:i + 16]
            char = chr(int(''.join(str(bit) for bit in byte), 2))
            ascii_string += char

    return ascii_string


# ----------------第3关--------------------
# ASCII码加密
def change_ASCII(ascii_string, key):
    binary_list = bit_ascll(ascii_string, 16)
    binary_list_en = [0] * len(binary_list)
    m = len(binary_list) // 16  # 字符的个数
    n = 0  # 当前二进制位数
    k = 0
    # 加密
    for i in range(m):
        bit = [0] * 16
        for j in range(16):
            bit[j] = binary_list[n]
            n += 1
        en_bit = Encrypt(bit, key)
        for j in range(16):
            binary_list_en[k] = en_bit[j]
            k += 1

    en_ascii_string = ascii_bit(binary_list_en, 16)

    return en_ascii_string


# ASCII码解密
def de_change_ASCII(en_ascii_string, key):
    binary_list = bit_ascll(en_ascii_string, 16)
    binary_list_en = [0] * len(binary_list)
    m = len(binary_list) // 16  # 字符的个数
    n = 0  # 当前二进制位数
    k = 0  # 当前二进制数
    # 加密
    for i in range(m):
        bit = [0] * 16
        for j in range(16):
            bit[j] = binary_list[n]
            n += 1
        en_bit = Decrypt(bit, key)
        for j in range(16):
            binary_list_en[k] = en_bit[j]
            k += 1

    en_ascii_string = ascii_bit(binary_list_en, 16)

    return en_ascii_string


# string = 'Hello!'

# en_string = change_ASCII(string, key)
# print(en_string)
# de_string = de_change_ASCII(en_string, key)
# print(de_string)


# -----------------------------------------------

# -----------------------------第4关------------------------------
# 4.1 双重加密
# 将32位的密钥分解为两个16位的密钥
def divide_key(key):
    key1, key2 = split_data(key)
    return key1, key2


# 加密
def double_encrypt(ascii_string, key):
    # 分解密钥
    key1, key2 = divide_key(key)

    # 第一次加密
    en_string1 = change_ASCII(ascii_string, key1)

    # 第二次加密
    en_string2 = change_ASCII(en_string1, key2)

    return en_string2


# 解密
def double_decrypt(en_ascii_string, key):
    # 分解密钥
    key1, key2 = divide_key(key)

    # 第一次解密
    de_string1 = de_change_ASCII(en_ascii_string, key2)

    # 第二次解密
    de_string2 = de_change_ASCII(de_string1, key1)

    return de_string2


# 测试
# keydouble = [1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1]

# en_string = double_encrypt(string, keydouble)
# print(en_string)
# de_string = double_decrypt(en_string, keydouble)
# print(de_string)

# -----------------------------------------------------------------
# 4.2 中间相遇攻击
key_start = 0
key_end = 65536


def number_bit(number1, number2=0):
    binary_string = format(number1, '016b')
    # 将二进制数位分开存入列表
    binary_list = [int(bit) for bit in binary_string]

    # 如果第二个数字不为默认值0，则将其转为二进制数导入二进制列表
    if number2 != 0:
        binary_string2 = format(number2, '016b')
        for i in binary_string2:
            binary_list.append(int(i))

    return binary_list


# 通过值来找到对应的键
def get_key_from_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None


# 计算得到可能的加、解密结果
def middle_meet_attack(en_string, de_string):
    # 存储加解密得到的结果
    encrypt_result = {}
    decrypt_result = {}

    # 加解密可能的结果
    for key_test in range(key_start, key_end):
        k1 = number_bit(key_test)
        # 导入解密中间结果
        middle_string_de = de_change_ASCII(en_string, k1)
        decrypt_result[key_test] = middle_string_de

        # 导入加密中间结果
        middle_string_en = change_ASCII(de_string, k1)
        encrypt_result[key_test] = middle_string_en

    decrypt_result_value = set(decrypt_result.values())
    encrypt_result_value = set(encrypt_result.values())

    # 找到相同的中间值集合
    same_middle_values = decrypt_result_value & encrypt_result_value
    key1_list = []
    key2_list = []

    for same_middle_value in same_middle_values:
        # 根据相同值获取可能的密钥
        key1 = get_key_from_value(decrypt_result, same_middle_value)
        key2 = get_key_from_value(encrypt_result, same_middle_value)
        # 导入可能的密钥
        key1_list.append(key1)
        key2_list.append(key2)

    # 存储可能的密钥对
    possible_key = []

    for i in range(0, len(key1_list)):
        possible_key.append(number_bit(key2_list[i], key1_list[i]))


    return possible_key



# -----------------------------------------------------
# 4.3 三重加密
# 划分密钥
def divide_three_key(key):
    key1 = key[0:16]
    key2 = key[16:32]
    key3 = key[32:48]

    return key1, key2, key3


# 加密
def three_encrypt(ascii_string, key):
    # 分解密钥
    key1, key2, key3 = divide_three_key(key)

    # 第一次加密
    en_string1 = change_ASCII(ascii_string, key1)

    # 第二次加密
    en_string2 = change_ASCII(en_string1, key2)

    # 第三次加密

    en_string3 = change_ASCII(en_string2, key3)

    return en_string3


# 解密
def three_decrypt(en_ascii_string, key):
    # 分解密钥
    key1, key2, key3 = divide_three_key(key)

    # 第一次解密
    de_string1 = de_change_ASCII(en_ascii_string, key3)

    # 第二次解密
    de_string2 = de_change_ASCII(de_string1, key2)

    # 第三次解密
    de_string3 = de_change_ASCII(de_string2, key1)

    return de_string3


# 测试
# keythree = [1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0,
#             0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0]
#
# en_string = three_encrypt(string, keythree)
# print(en_string)
# de_string = three_decrypt(en_string, keythree)
# print(de_string)


# ------------------------------第5关------------------------------
# 工作模式
# 将分部数据导入一个列表
def append_data(list, part_list):
    n = len(part_list)
    for i in range(n):
        list.append(part_list[i])


def append_data_ni(list, part_list):
    n = len(part_list)
    for i in range(n - 1, -1, -1):
        list.append(part_list[i])


# CBC模式加密
def CBC_encrypt(ascll_string, key):
    # 生成初始向量
    rand_num1 = random.randint(1, 65535)
    rand_num2 = random.randint(1, 65535)
    rand_num = (rand_num2 + rand_num1) // 2
    init_list = number_bit(rand_num)

    # 划分原句
    binary = bit_ascll(ascll_string, 16)
    n = len(binary) // 16
    m = 0

    # 初始化存取加密结果的列表
    encrypt_list = []

    # 第0轮异或
    string_m = binary[0:(m + 1) * 16]
    m += 1
    exclusive_string = exclusive_or(string_m, init_list)

    while m != n:
        string_m = binary[(m * 16):((m + 1) * 16)]
        # 第m轮加密
        en_string_m = Encrypt(exclusive_string, key)
        # 加密结果存入列表
        append_data(encrypt_list, en_string_m)

        # 第m轮异或
        exclusive_string = exclusive_or(en_string_m, string_m)
        m += 1

    # 最后一次加密
    en_string_end = Encrypt(exclusive_string, key)
    # 加密结果存入列表
    append_data(encrypt_list, en_string_end)

    # 将二进制加密列表转为ASCII码
    encrypt_string = ascii_bit(encrypt_list, 16)

    # 返回初始向量和加密后的结果
    return init_list, encrypt_string


# CBC模式解密
def CBC_decrypt(encrypt_string, key, init_list):
    # 划分原句
    binary = bit_ascll(encrypt_string, 16)
    n = len(binary) // 16
    m = n

    # 初始化存取解密结果的列表
    decrypt_list = []

    # 第0次解密
    string_m = binary[((m - 1) * 16):(m * 16)]
    de_string_m = Decrypt(string_m, key)
    m -= 1

    while m != 0:
        # 逆异或
        string_m = binary[((m - 1) * 16):(m * 16)]
        exclusive_string_m = exclusive_or(de_string_m, string_m)
        # 导入解密结果
        append_data_ni(decrypt_list, exclusive_string_m)

        # 解密
        de_string_m = Decrypt(string_m, key)
        m -= 1

    # 最后与初始向量做一次异或
    de_string_end = exclusive_or(de_string_m, init_list)
    # 导入解密结果
    append_data_ni(decrypt_list, de_string_end)
    # 对解密列表倒序
    decrypt_list_end = list(reversed(decrypt_list))
    # print(decrypt_list_end)
    # 获得解密的ASCII码
    decrypt_ascii = ascii_bit(decrypt_list_end, 16)

    # 返回解密结果的bit值和ASCII码
    return  decrypt_ascii


# 密文替换
def miwen_replace(encrypt_string, key, init_list):
    # 将密文转换为二进制列表
    encrypt_list = bit_ascll(encrypt_string, 16)
    # 列表长度
    n = len(encrypt_list)

    # 随即替换其中的两个部分
    tihuan1 = n // 3
    if encrypt_list[tihuan1] == 0:
        encrypt_list[tihuan1] = 1
    else:
        encrypt_list[tihuan1] = 0

    # tihuan2 = n // 8
    # if encrypt_list[tihuan2] == 0:
    #     encrypt_list[tihuan2] = 1
    # else:
    #     encrypt_list[tihuan2] = 0

    # 将二进制列表转为ASCII码
    encrypt_string = ascii_bit(encrypt_list, 16)


    # 解密修改后的密文
    decrypt_ascii = CBC_decrypt(encrypt_string, key, init_list)

    return decrypt_ascii


class Widget(QWidget):
    def __init__(self):
        super(Widget, self).__init__()
        self.load_ui()
        self.init_background()

    def init_background(self):
        # 保存图片路径
        self.background_image_path = "D:/S-AES/bk1.png"
        self.update_background()

    def update_background(self):
        # 创建一个 QPixmap 并加载图片
        pixmap = QPixmap(self.background_image_path)
        # 调整 QPixmap 到窗口大小
        scaled_pixmap = pixmap.scaled(self.size(), Qt.IgnoreAspectRatio)
        # 设置调整大小后的 QPixmap 为背景
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
        self.setPalette(palette)

    def resizeEvent(self, event):
        # 当窗口大小改变时更新背景
        self.update_background()
        super().resizeEvent(event)

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()

        # 添加按钮点击事件处理逻辑
        self.pushButton_3 = self.findChild(QPushButton, "pushButton_3")
        self.pushButton_2 = self.findChild(QPushButton, "pushButton_2")
        self.pushButton = self.findChild(QPushButton, "pushButton")
        self.pushButton_5 = self.findChild(QPushButton, "pushButton_5")
        self.pushButton_4 = self.findChild(QPushButton, "pushButton_4")
        self.pushButton_6 = self.findChild(QPushButton, "pushButton_6")
        self.pushButton_7 = self.findChild(QPushButton, "pushButton_7")
        self.pushButton_8 = self.findChild(QPushButton, "pushButton_8")
        self.pushButton_9 = self.findChild(QPushButton, "pushButton_9")
        self.pushButton_10 = self.findChild(QPushButton, "pushButton_10")
        self.pushButton_11 = self.findChild(QPushButton, "pushButton_11")
        self.pushButton_12 = self.findChild(QPushButton, "pushButton_12")
        self.pushButton_35 = self.findChild(QPushButton, "pushButton_35")
        self.pushButton_36 = self.findChild(QPushButton, "pushButton_36")
        self.pushButton_37 = self.findChild(QPushButton, "pushButton_37")
        self.pushButton_38 = self.findChild(QPushButton, "pushButton_38")
        self.pushButton_39 = self.findChild(QPushButton, "pushButton_39")
        self.pushButton_40 = self.findChild(QPushButton, "pushButton_40")
        self.pushButton_41 = self.findChild(QPushButton, "pushButton_41")
        self.pushButton_34 = self.findChild(QPushButton, "pushButton_34")
        self.pushButton_33 = self.findChild(QPushButton, "pushButton_33")
        self.pushButton_32 = self.findChild(QPushButton, "pushButton_32")
        self.pushButton_31 = self.findChild(QPushButton, "pushButton_31")
        self.pushButton_13 = self.findChild(QPushButton, "pushButton_13")
        self.stackedWidget = self.findChild(QStackedWidget, "stackedWidget")
        self.lineEdit_34 = self.findChild(QLineEdit, "lineEdit_34")
        self.lineEdit_35 = self.findChild(QLineEdit, "lineEdit_35")
        self.lineEdit_36 = self.findChild(QLineEdit, "lineEdit_36")
        self.lineEdit_37 = self.findChild(QLineEdit, "lineEdit_37")
        self.lineEdit_38 = self.findChild(QLineEdit, "lineEdit_38")
        self.lineEdit_39 = self.findChild(QLineEdit, "lineEdit_39")
        self.lineEdit_40 = self.findChild(QLineEdit, "lineEdit_40")
        self.lineEdit_43 = self.findChild(QLineEdit, "lineEdit_43")
        self.textEdit = self.findChild(QTextEdit, "textEdit")
        self.textEdit_2 = self.findChild(QTextEdit, "textEdit_2")
        self.textEdit_16 = self.findChild(QTextEdit, "textEdit_16")
        self.textEdit_17 = self.findChild(QTextEdit, "textEdit_17")
        self.textEdit_18 = self.findChild(QTextEdit, "textEdit_18")
        self.textEdit_19 = self.findChild(QTextEdit, "textEdit_19")
        self.textEdit_20 = self.findChild(QTextEdit, "textEdit_20")
        self.textEdit_21 = self.findChild(QTextEdit, "textEdit_21")
        self.textEdit_22 = self.findChild(QTextEdit, "textEdit_22")
        self.textEdit_23 = self.findChild(QTextEdit, "textEdit_23")
        self.textEdit_24 = self.findChild(QTextEdit, "textEdit_24")
        self.lineEdit = self.findChild(QLineEdit, "lineEdit")
        self.lineEdit_2 = self.findChild(QLineEdit, "lineEdit_2")
        self.lineEdit_3 = self.findChild(QLineEdit, "lineEdit_3")
        self.lineEdit_4 = self.findChild(QLineEdit, "lineEdit_4")
        self.lineEdit_5 = self.findChild(QLineEdit, "lineEdit_5")
        self.lineEdit_6 = self.findChild(QLineEdit, "lineEdit_6")


        self.pushButton_31.clicked.connect(self.on_pushButton_31_clicked)
        self.pushButton_32.clicked.connect(self.on_pushButton_32_clicked)
        self.pushButton_33.clicked.connect(self.on_pushButton_33_clicked)
        self.pushButton_34.clicked.connect(self.on_pushButton_34_clicked)
        self.pushButton_35.clicked.connect(self.on_pushButton_35_clicked)
        self.pushButton_36.clicked.connect(self.on_pushButton_36_clicked)
        self.pushButton_37.clicked.connect(self.on_pushButton_37_clicked)
        self.pushButton_38.clicked.connect(self.on_pushButton_38_clicked)
        self.pushButton_39.clicked.connect(self.on_pushButton_39_clicked)
        self.pushButton_40.clicked.connect(self.on_pushButton_40_clicked)
        self.pushButton_41.clicked.connect(self.on_pushButton_41_clicked)
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        self.pushButton_2.clicked.connect(self.on_pushButton_2_clicked)
        self.pushButton_3.clicked.connect(self.on_pushButton_3_clicked)
        self.pushButton_4.clicked.connect(self.on_pushButton_4_clicked)
        self.pushButton_5.clicked.connect(self.on_pushButton_clicked)
        self.pushButton_6.clicked.connect(self.on_pushButton_2_clicked)
        self.pushButton_7.clicked.connect(self.on_pushButton_3_clicked)
        self.pushButton_10.clicked.connect(self.on_pushButton_clicked)
        self.pushButton_11.clicked.connect(self.on_pushButton_2_clicked)
        self.pushButton_12.clicked.connect(self.on_pushButton_3_clicked)
        self.pushButton_9.clicked.connect(self.on_pushButton_9_clicked)
        self.pushButton_8.clicked.connect(self.on_pushButton_8_clicked)
        self.pushButton_13.clicked.connect(self.on_pushButton_13_clicked)

    # 按钮点击事件处理逻辑
    def on_pushButton_31_clicked(self):
        self.stackedWidget.setCurrentIndex(0)

    def on_pushButton_32_clicked(self):
        self.stackedWidget.setCurrentIndex(1)

    def on_pushButton_33_clicked(self):
        self.stackedWidget.setCurrentIndex(2)

    def on_pushButton_34_clicked(self):
        self.stackedWidget.setCurrentIndex(6)

    def on_pushButton_35_clicked(self):
        self.stackedWidget.setCurrentIndex(3)

    def on_pushButton_clicked(self):
        self.stackedWidget.setCurrentIndex(3)

    def on_pushButton_2_clicked(self):
        self.stackedWidget.setCurrentIndex(4)

    def on_pushButton_3_clicked(self):
        self.stackedWidget.setCurrentIndex(5)

    def on_pushButton_13_clicked(self):
        self.stackedWidget.setCurrentIndex(7)

    def on_pushButton_39_clicked(self):
        key = self.lineEdit_40.text()
        string = self.textEdit_2.toPlainText()
        key = string_list(key)
        global init_list
        init_list, encrypt_string = CBC_encrypt(string, key)
        self.textEdit_22.setText("加密后的密文为：")
        self.textEdit_22.append(encrypt_string)

    def on_pushButton_9_clicked(self):
        key = self.lineEdit_6.text()
        string = self.lineEdit_5.text()
        key = string_list(key)
        miwen = three_encrypt(string, key)
        self.textEdit_21.setText("加密后的密文为：")
        self.textEdit_21.append(str(miwen))

    def on_pushButton_4_clicked(self):
        key = self.lineEdit.text()
        string = self.lineEdit_2.text()
        key = string_list(key)
        miwen = double_encrypt(string, key)
        self.textEdit_19.setText("加密后的密文为：")
        self.textEdit_19.append(miwen)

    def on_pushButton_36_clicked(self):
        key = self.lineEdit_34.text()
        string = self.lineEdit_35.text()
        key = string_list(key)
        string = string_list(string)
        miwen = Encrypt(string,key)
        self.textEdit_16.setText("加密后的密文为：")
        self.textEdit_16.append(str(miwen))

    def on_pushButton_37_clicked(self):
        key = self.lineEdit_36.text()
        string = self.lineEdit_37.text()
        key = string_list(key)
        miwen = change_ASCII(string,key)
        self.textEdit_17.setText("加密后的密文为：")
        self.textEdit_17.append(str(miwen))

    def on_pushButton_38_clicked(self):
        key = self.lineEdit_38.text()
        miwen = self.lineEdit_39.text()
        key = string_list(key)
        mingwen = de_change_ASCII(miwen,key)
        self.textEdit_18.setText("解密后的明文为：")
        self.textEdit_18.append(mingwen)

    def on_pushButton_40_clicked(self):
        global init_list
        key = self.lineEdit_43.text()
        miwen = self.textEdit.toPlainText()
        key = string_list(key)
        mingwen = CBC_decrypt(miwen,key,init_list)
        self.textEdit_23.setText("解密后的明文为：")
        self.textEdit_23.append(mingwen)

    def on_pushButton_41_clicked(self):
        global init_list
        key = self.lineEdit_43.text()
        miwen = self.textEdit.toPlainText()
        key = string_list(key)
        mingwen = miwen_replace(miwen,key,init_list)
        self.textEdit_24.setText("解密后的明文为：")
        self.textEdit_24.append(mingwen)

    def on_pushButton_8_clicked(self):
        miwen = self.lineEdit_3.text()
        mingwen = self.lineEdit_4.text()
        miyao = middle_meet_attack(miwen,mingwen)
        self.textEdit_20.setText("破解得到的密钥为：")
        self.textEdit_20.append(str(miyao))


if __name__ == "__main__":
    app = QApplication([])
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
