# S-AES
第1关：基本测试
  根据S-AES算法编写和调试程序，提供GUI解密支持用户交互。输入可以是16bit的数据和16bit的密钥，输出是16bit的密文。
 ![image](https://github.com/gujiprogram/S-AES/assets/118802992/58a651f4-5ad6-439c-a050-b0b6c001c30c)
 
第2关：交叉测试
  考虑到是"算法标准"，所有人在编写程序的时候需要使用相同算法流程和转换单元(替换盒、列混淆矩阵等)，以保证算法和程序在异构的系统或平台上都可以正常运行。
设有A和B两组位同学(选择相同的密钥K)；则A、B组同学编写的程序对明文P进行加密得到相同的密文C；或者B组同学接收到A组程序加密的密文C，使用B组程序进行解密可得到与A相同的P。
![image](https://github.com/gujiprogram/S-AES/assets/118802992/49b3c14b-3481-423c-a9e8-fc9c09f12672)
![image](https://github.com/gujiprogram/S-AES/assets/118802992/df1da09f-4405-4d85-848d-d2e2dd224569)

第3关：扩展功能
考虑到向实用性扩展，加密算法的数据输入可以是ASII编码字符串(分组为2 Bytes)，对应地输出也可以是ACII字符串(很可能是乱码)。
![image](https://github.com/gujiprogram/S-AES/assets/118802992/9400752b-229c-4aff-a412-5c20d70f2b96)
![image](https://github.com/gujiprogram/S-AES/assets/118802992/f49cef09-6d68-4f39-a302-9c68ce7a49ff)

第4关：多重加密
双重加密
  将S-AES算法通过双重加密进行扩展，分组长度仍然是16 bits，但密钥长度为32 bits。
![image](https://github.com/gujiprogram/S-AES/assets/118802992/1050d102-1b25-4d92-98a4-de309b8461cc)

中间相遇攻击
  假设你找到了使用相同密钥的明、密文对(一个或多个)，请尝试使用中间相遇攻击的方法找到正确的密钥Key(K1+K2)。
![image](https://github.com/gujiprogram/S-AES/assets/118802992/b0b9f46d-d30a-4a95-989c-0a3e8f4b0064)

三重加密
  将S-AES算法通过三重加密进行扩展，下面两种模式选择一种完成：
  使用48bits(K1+K2+K3)的模式进行三重加解密。
![image](https://github.com/gujiprogram/S-AES/assets/118802992/580a2ab9-5da8-42bc-bd55-a5b43984afac)

第5关：工作模式
  基于S-AES算法，使用密码分组链(CBC)模式对较长的明文消息进行加密。注意初始向量(16 bits) 的生成，并需要加解密双方共享。
在CBC模式下进行加密，并尝试对密文分组进行替换或修改，然后进行解密，请对比篡改密文前后的解密结果。
![image](https://github.com/gujiprogram/S-AES/assets/118802992/350a9f9a-4e2c-4510-b9bb-27e2a63ff52f)
![image](https://github.com/gujiprogram/S-AES/assets/118802992/4fbda076-d71b-4926-94d9-cff476d0616d)








