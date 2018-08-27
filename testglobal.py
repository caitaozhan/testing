import myglobal

def main():
    '''main
    '''
    print(myglobal.local_size)
    myglobal.local_size = 3
    print(myglobal.local_size)

if __name__ == '__main__':
    main()
