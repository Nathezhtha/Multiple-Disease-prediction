def find_overlap(s1, s2):
    for i in range(len(s1)):
        test1, test2 = s1[i:], s2[:len(s1) - i]
        if test1 == test2:
            return test1

s1, s2 = "My name is Bogdan", "Bogdan and I am from Russia"
dd=find_overlap(s1, s2)
print(dd)
# 'Bogdan'
s1, s2 = "mynameisbogdan", "bogdanand"
pp=find_overlap(s1, s2)
print(pp)