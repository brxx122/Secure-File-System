# 安全文件系统


## 基本要求
本系统主要为了实现在不安全的文件服务器上存储数据。在文件服务器上获取不到用户文件的明文数据，也不能损坏数据。同时，该系统需要有相对安全的通信渠道，对于常见的意图破坏和窃取用户信息的网络攻击有一定的抵抗能力。除用户本地之外，其余所有流经网络的信息都需要一定的安全防护措施。



### 文件系统的基本要求
* 用户可以创建、删除、读取、写入、重命名文件（即Linux系统下常见的文件错做命令）

* 文件系统支持目录，可以通过目录寻找文件，文件以层次结构组织

* 用户能够在文件系统内部设置文件和目录的权限，即对于文件系统的用户和文件服务器等设置访问权限

* 文件名和目录名应当被加密，该加密必须在信息离开用户主机之前完成，在传输及存储过程中保持加密状态

* 文件系统需要记录未被授权的“用户修改文件或目录的行为”，即在用户试图访问没有权限的文件时，文件系统需要记录系统日志

* 文件服务器不能读取文件内容，文件名或目录名，这里的不能读取理解为不能够获取明文信息

* 服务器不能从一个文件中获取数据，并且响应多个客户端，不能为不同文件的客户端提供数据，即用户之间保持数据的独立。

* 若文件服务器不是恶意的，未被授权的用户行为不能够损坏文件系统

* 若文件服务器是恶意的，则文件或目录的创建和删除操作均能被检测到，这里要求对服务器进行持续监控，记录不合法行为，或者保存本地备份，定时检测文件服务器是否修改信息

  ​


## 设计思路
1. 文件系统由客户端client和服务器端server组成，server端负责和存储数据的文件服务器之间的通信， client负责文件的加解密。

2. client和server之间需要能够相互验证，一旦验证成功能够在加密的环境下进行通信，并且能够验证传输数据的完整性。

3. 用户通过client端进行登录和注册。用户第一次使用时，将向server端发出注册请求（用户名和密码），并且生成一对RSA通信密钥，将自己的公钥发送给server。server端同意之后将自己的通信公钥发送给用户，并在文件服务器端初始化用户的远程仓库，完成注册流程。此后用户本地保存RSA通信私钥和server通信公钥，并且离线保存用户密码。server保存自己的私钥和用户清单，包含用户名、密码和通信公钥。

4. client和server端使用RSA进行通信加密，分别使用对方的公钥加密。并且用户上传的文件进行签名验证，数据使用自己的私钥加密形成signature，客户端收到信息之后首先验证signature是否损坏，防止通信中信息被篡改。

5. 为了防止server端收到攻击之后导致用户信息泄露，server只保存client端加密之后的密文文件，加解密完全在client实现。为了防止恶意用户窃取用户个人本地保存的私钥，或者假冒合法用户向server申请服务，用户需要密码方能登录文件系统，密码由用户自己离线保存。

6. client在注册时除了生成RSA通信密钥之外，还需要生成文件加密所使用的AES密钥，并且保存在本地根目录下。所有文件和目录名都需要加密之后再发送给server，server负责将其上传到文件服务器。

7. 文件服务器上的存储不完全按照目录进行。目录加密之后长度增加，server负责将其合理划分，增加虚假的目录层次，同时在server端的根目录下保存所有文件的加密之后初始地址层次及用户权限。即server端可以获得用户文件的层次信息（但是无法解密具体目录名），但是文件服务器只能获得虚假的目录名和层次关系。

8. 用户可以设置每个文件和目录的权限，权限控制简单分成4种，不可见（U）、可读（R）、可写（W）、可执行（E），4种权限不相重合，每个文件只能有一种权限（共享文件除外），文件权限按照U、R、W、E的顺序依次增强。默认自己创建的文件可写，不可见文件在设置之后不会在文件夹种显示出现（即ls命令不会显示出来），用户的操作需要对应的权限。

9. 用户文件在文件服务器上的信息由server保存，每个用户单独一个file.list文件。用户client的每次请求都需要发送自己的用户名，server端再去根目录下获得，对文件进行修改的操作，需要在响应client端之前进行保存，一个文件每次只能由一个用户获得，即不同线程之间需要通过加锁保证文件的一致性。因为server端使用多线程提供服务，在处理每个client请求的时候才去获取文件，并且在处理完响应之前进行保存，因此在多个用户同时登录时，只要确保线程之间的相对独立，文件之间可以保持一定独立性。

10. 当用户发起共享操作时，他需要指明共享对象的用户名及所赋予的权限。被共享者将在远程获得一个文件备份，该备份的创建者是共享者。每次被共享者对该文件进行请求时，server负责验证被共享者是否拥有对应权限。用户A在对自己文件进行共享操作时，client端将负责处理文件加解密过程，首先从文件服务器上获取该文件并进行解密，之后在生成一个新的AES共享密钥，该密钥将使用被共享者B的RSA通信公钥进行加密，并且传送给server端进行保存。因此将会在A_users.list和B_users.list同时出现该文件。用户在获取共享位为True的文件时，都将使用自己的私钥对共享AES进行解密，再使用解密后的AES密钥进行文件内容的解密。文件系统仅支持两人之间的共享，如果需要多人共享，将由A进行多次贡献操作，并且给每次共享都设置一个不同的AES密钥。

11. 共享者A在共享时需要设置权限，默认权限为可读。当拥有可写权限的用户C对共享文件进行修改之后，仅能够写入自己远程仓库的副本中，但在server端存储了更新信息，共享者A在登录之后server将会检查共享文件信息，如果存在更改（如update.log不为空），将在登录确认中反馈给A。如果A同意修改则该消息存储在其余所有用户的共享文件信息中，如果不同意则将在B处存储文件，并且要求使用A的文件进行覆盖。用户B在收到拒绝之后可以选择下载操作来本地保存。

    ​



## 实现功能
* 实现基本加密文件系统的相关操作，包括创建、删除、读取、写入、重命名文件、上传、下载读写等。

* 尚未实现有关共享文件方面的逻辑

  ​


## 程序运行
### 系统环境
程序开发：
* 64位 Ubuntu 16.04 环境下， 使用python 2.7开发
* 依赖的加密包pyCrypto作为文件夹Crypto存放在工作目录下，也可以通过get-crypto.sh脚本获取

### 项目目录
```
Secure-File-System                         
├── client				# 客户端文件
│   ├── client.py				# 客户端运行脚本
│   ├── client_helper.py		# 用户类及操作
│   ├── client_operation.py		# 一些客户端处理函数
│   └── client_transmit.py      # client和server传输函数
├── server				# 服务器文件
│   ├── _init_					# 服务器初始化及根目录
│   │	├── username_files.list		# 用户文件列表，以用户名区别
│   │	├── server_pk.pem			# 服务器公钥
│	│   ├── server_prk.pem			# 服务器私钥
│	│   └── users.list				# 用户列表
│   ├── server.py			# 服务器运行脚本
│   ├── server_helper.py	# 文件Inode类及操作
│   └── server_operations.py# 与文件服务器传输相关函数
├── Crypto				# pycryto加密库
├── chunk_encrypt.py		# 分块加密函数
├── error.py				# 一些错误定义
├── get-crypto.sh			# 获取pycrypto脚本
└── ReadMe.md			# 本说明文档
```



## 操作说明

1. 分别运行server.py和client.py文件，第一次运行server.py将进行初始化，第一次登录client需要注册用户
2. 在进入文件系统client端之后，可以通过help指令获得相关操作的说明，其中部分操作尚未实现，如递归复制文件夹(cp -r)及share相关的函数(share -f -u)。




## 一些说明

* 用户本地根目录设置为HOME/SFS_local/username，用户远程仓库（文件服务器）设置为HOME/SFS_server/username
* 所有的文件操作均不包括嵌套文件夹
* 由于时间关系关于用户错误操作的测试有限，不符合要求的输入可能引发未知后果
* 该系统的实现参考了github上Aakriti Shroff, Happy Enchill, Quan Nguyen等人的加密文件系统，其中获取pycryto的脚本和用于分块加密的chunk_encrypt.py中encrypt和decrypt是使用的他们的开源代码，可以在[这里](https://github.com/henchill/encrypted_file_system)找到


