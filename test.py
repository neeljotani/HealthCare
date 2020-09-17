def update_dict_in_list():
    l = [{'id': 1, 'name': "abc"}, {'id': 2, 'name': "xyz"}]
    print('before ', l)
    for ele in l:
        if ele['id'] == 2 :
            ele['name'] = 'pqr'

    print('after ', l)

def check_subset():
    s1 = {'cough', 'headache'}
    s2 = {'cough', 'headache', 'corona'}
    s3 = {'headache', 'corona', 'cough'}
    print("s1 is subset of s2 ?", s1.issubset(s2))
    print("s1 is same s2 ?", s1 == s3)

def get_substr():
    str1 = "Hello Python"
    str2 = str1[:19]
    print("sub string : ", str2)

# update_dict_in_list()
# check_subset()
get_substr()





