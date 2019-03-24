'''
运行方式：直接跑此脚本  python lucyTestProfiler.py 
'''

'''
from memory_profiler import profile

# 函数前加装饰器
@profile(precision=4,stream=open('lucyTestMemoryProfiler.log','a'))
def testPlus():
    c=0
    for item in range(100000):
        c+=1
    print(c)

@profile(precision=4,stream=open('lucyTestMemoryProfiler.log','w+'))
def my_func():
    a = [1] * (10**6)
    b = [2] * (2*10**7)
    del b
    return a
                
if __name__ == '__main__':
    my_func()
    testPlus()
    
'''

'''
使用memory_profiler检测内存使用情况， 检测报告输出到lucyTestMProfiler.log
运行方式：直接跑此脚本  python lucyTestMProfiler.py 

@author yhqian 03/23/2019
'''

# 导入
from memory_profiler import profile

# 函数前加装饰器
@profile(precision=4,stream=open('lucyTestMProfiler.log', 'w+', encoding='UTF-8'))
def testPlus():
    c=0
    for item in range(100000):
        c+=1
    print(c)

@profile(precision=4,stream=open('lucyTestMProfiler.log', 'a', encoding='UTF-8'))  #追加日志
def my_func():
    a = [1] * (10**6)   # 10^6 = 1M, 一个float 8B,  估算共8M
    b = [2] * (2*10**7)
    del b
    return a
                
if __name__ == '__main__':
    testPlus()
    my_func()
   




