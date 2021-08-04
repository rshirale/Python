import sys
import os
import collections
import re
from hashlib import md5

args = sys.argv
if len(args) != 2:
    print("Directory is not specified")

else:
    counter = 0
    total_size = 0
    size_after_file_del = 0
    size = {}
    d = collections.defaultdict(dict)
    file_number = {}
    # foldername = args[1]
    # path = r"C:\Users\rahul\PycharmProjects\DuplicateFileHandlersProject1of1\module\root_folder"

    path = args[1]

        #r"C:\Users\rahul\PycharmProjects\DuplicateFileHandlersProject1of1\module\root_folder"
    print('Enter file format:')
    file_format = input()
    print()
    print('Size sorting options:\n1. Descending\n2. Ascending\n')

    while True:
        print("Enter a sorting option:")
        sorting_option = int(input())
        print()
        if sorting_option != 1 and sorting_option != 2:
            print()
            print('Wrong option')
            continue
        else:
            break

    # os.chdir(foldername)
    os.chdir(path)

    # for root, dirs, files in os.walk(foldername, topdown=True):
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:

            if name.endswith(file_format):
                size[os.path.join(root, name)] = os.path.getsize(os.path.join(root, name))
                d[os.path.getsize(os.path.join(root, name))][os.path.join(root, name)] = md5(
                    open(os.path.join(root, name), 'rb').read()).hexdigest()
                total_size += os.path.getsize(os.path.join(root, name))

    if sorting_option == 2:
        set_of_values = collections.OrderedDict(sorted(d.items()))
        for i in set_of_values:

            print(i, 'bytes')
            for key, value in size.items():
                if value == i:
                    print(key)
            print()


    else:
        set_of_values = collections.OrderedDict(sorted(d.items(), reverse=True))

        for i in set_of_values:
            print(i, 'bytes')
            for key, value in size.items():
                if value == i:
                    print(key)
            print()


    def compute_hash(si, i):
        global counter

        res = collections.Counter(si.values())
        temp = []
        count = 0

        for a, b in res.items():
            if b > 1:
                if count != 1:
                    print()
                    print(i, 'bytes')

                    count += 1

                print("Hash: ", a)

                for key, value in si.items():

                    if a == value:
                        counter += 1
                        print(f'{counter}. {key}')
                        file_number[counter] = key


    while True:
        print('Check for duplicates?')
        check_dup = input()
        print()
        if check_dup == 'yes':
            for i in set_of_values:
                compute_hash(set_of_values[i], i)

            break
        elif check_dup == 'no':
            break
        else:
            print()
            print('Wrong option')
            continue


    def members(dictarg, keyslistarg):

        count = 0
        for list_item in keyslistarg:
            if int(list_item) in dictarg:
                count += 1

        return len(keyslistarg) == count


    while True:
        delete_files = input('\nDelete files?\n')

        if delete_files == 'yes':

            while True:
                try:
                    print('\nEnter file numbers to delete:')
                    file_sequence = input().split()

                    for item in file_sequence:
                        if re.match(r'[\D?\.]+', item):

                            pass

                        elif '.' in item:
                            # print(item)
                            pass

                    if not file_sequence:
                        print('\nWrong format')
                        continue

                    elif members(file_number, file_sequence):
                        
                        for number in file_sequence:
                            size_after_file_del += os.path.getsize(file_number.get(int(number)))
                            print("Deleting:", file_number.get(int(number)))

                        print('\nTotal freed up space:', total_size - size_after_file_del, ' bytes')
                        sys.exit()

                    else:
                        print('\nWrong format')
                        # print("All files Dictionary", d)
                        # print("Size Dictionary", size)
                        # print("File Number Dictionary", file_number)

                except ValueError:
                    print('\nWrong format')



        elif delete_files == 'no':
            break

        else:
            print()
            print('Wrong option')
            continue
