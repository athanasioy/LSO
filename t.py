class ns:
    def __init__(self, l:list):
        self.l = l

fo = ns([1,2,3])

so = ns(fo.l.copy())

print("remove fo", fo.l.pop())
print("list of so", so.l)
print("list of so", fo.l)
print(set.intersection(set(so.l), set(fo.l)))
print(set().intersection(*[fo.l, so.l]))