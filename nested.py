class Utility:
    def outer(self, outer: str):
        def inner():
            print(outer*2)
            print('inner')
        print(outer*4)
        inner()


class Utility2:
    @staticmethod
    def outer(outer: str):
        def inner():
            print(outer*2)
            print('inner')
        print(outer*4)
        inner()

u = Utility()
u.outer('o')

u2 = Utility2()
u2.outer('o')