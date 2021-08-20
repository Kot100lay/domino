import os
import imghdr
import kotjson
import json

# midgets
from bs4 import BeautifulSoup
import requests
import random
import re  # next_name

# debugging
import time

wiki_langs = ["en", "es", "ru", "it", "pt", "de", "fr", "pl"]


# checks if every file (pepe) in "path" has a number-name and a valid extension
# invalid name - renames the file to fit the system
# invalid extension - double checks the extension, if it's valid, change it to the true one. otherwise delete
# updates 'highest' number name in pepedata.json
def pepecheck(path='', validext=''):  # checks if every file in a folder has a 'number' name and a valid ext
    bname = kotjson.json_check('bname')
    if os.listdir(path):
        for filename in os.listdir(path):
            (fname, ext) = os.path.splitext(filename)

            # if ext in validext:
            if fname.isdigit:  # if the name is a number
                if int(bname) < int(fname):
                    bname = int(fname)
            else:
                os.rename(path + filename, path + str(bname + 1) + ext)

            if ext not in validext:
                true_ext = extcheck(filename)[1]
                if true_ext in validext:
                    newname = path + fname + true_ext
                    os.rename(path + filename, newname)
                    break
                else:
                    os.remove(path + filename)
    else:
        bname = 0
    kotjson.json_modify('bname', bname)


# check the true extension of a file, [1] being the '.ext' string and [0] being i don't have any idea what
def extcheck(filetocheck):
    ret2 = "." + str(imghdr.what(filetocheck))
    ret1 = False
    if ret2:
        ret1 = True
    return ret1, ret2


# check if string is a numbeer
def is_number(s):
    try:
        int(s)
        return True
    except Exception:
        return False


# deletes the 'queued' file from the buffer-folder
def removepepe(path, filename):
    os.remove(path + filename)


def send_pepe_to_drive(path, filename):
    with open(path + filename):
        pass  # TODO   copy the selected file, send it to google drive, ping it and then remove the original


def random_midget(mode="sfw"):
    if mode == "nsfw":
        site = 'http://www.extremepornpics.com/midgets-images.html'
        response = requests.get(site)
        soup = BeautifulSoup(response.text, 'html.parser')
        center = soup.body.center

        midgets = []

        upper_midgets = center.findAll("ul", class_="exibig")
        for upper_midget in upper_midgets:
            midgets.extend(upper_midget.findAll("img"))

        lower_midgets = center.findAll("ul", class_="exismall")
        for lower_midget in lower_midgets:
            midgets.extend(lower_midget.findAll("img"))

    else:
        page = random.randint(1, 100)
        site = f"https://www.gettyimages.com/photos/dwarf?page={page}&phrase=dwarf&sort=mostpopular"

        response = requests.get(site)
        soup = BeautifulSoup(response.text, 'html.parser')

        midgets = soup.find_all(class_="gallery-asset__thumb gallery-mosaic-asset__thumb")

    midget_index = random.randint(0, len(midgets) - 1)

    return str(midgets[midget_index]['src'])


def add_to_checklist(_user_id, task_name, todo_or_done='todo'):
    # if there's already an item of that name then create another, but add "1" in the end, then "2" etc.
    if task_name.isdigit():
        return None
    user_id = str(_user_id)
    with open("checklist.json", 'r') as f:
        file = json.load(f)

    if user_id in file.keys():
        user_data = file[user_id]
    else:
        user_data = json.loads('''{  "todo": [],  "done":[]}''')

    if task_name in user_data[todo_or_done]:
        raise ValueError("Task with that name already exists")
    else:
        # task_to_add = {task_name:task_desc}
        user_data[todo_or_done].append(task_name)
        file.update({user_id: user_data})
        with open("checklist.json", 'w') as f:
            f.write(json.dumps(file))
        return True


def remove_from_checklist(_user_id, task_name, which_list, nuke=False):

    user_id = str(_user_id)
    task_name = task_name.strip()
    with open("checklist.json", 'r') as f:
        file = json.load(f)

    print(file.keys())
    if user_id in file.keys():
        user_data = file[user_id]
    else:
        user_data = json.loads('''{  "todo": [],  "done":[]}''')

    if not nuke and task_name not in user_data[which_list]:
        raise ValueError("Task with that name does not exist")
    else:
        if nuke:
            file[user_id][which_list] = []
        else:
            file[user_id][which_list].remove(task_name)
        with open("checklist.json", 'w') as f:
            f.write(json.dumps(file))
        return True  # item deleted


# spits out a list of all items on the user's checklist
def give_checklist(_user_id, todo_or_done) -> list:
    # loading data
    user_id = str(_user_id)
    file = None
    try:
        with open("checklist.json", 'r') as f:
            file = json.load(f)
    except FileNotFoundError:
        with open("checklist.json", 'w') as f:
            dict_for_json = {user_id: {'todo': [], 'done': []}}
            shittodump = json.dumps(dict_for_json, indent=4)
            f.write(shittodump)

    if file and user_id in file.keys():
        user_data = file[user_id]
    else:
        user_data = json.loads('''{  "todo": [],  "done":[]}''')

    if todo_or_done not in ['todo', 'done']:
        raise ValueError

    return user_data[todo_or_done]


# TODO: test this shit (should return the highest number from a list of names (or just numbers))
def next_name(elements, range_: int, fill=False):
    """
    returns None if range exceeded
    otherwise returns the (highest 'name number' + 1)
    fill: returns smallest 'not taken' value in range if True
    """
    # extracting only integers
    for element in elements:
        element = int(re.findall(r'\d+', element)[-1])

    elements = set(map(int, elements)) 
    highest_number = ''

    if not fill:
        if (max(elements) < range_):
            highest_number = max(elements)
        else:
            sorted_elements = elements.sort()
            highest_number = ''
            for element in sorted_elements:
                if element > range_: break
                if element > highest_number: highest_number = element
    elif fill:
        for i in range(range_):
            if i not in elements:
                highest_number = i
                break

    return highest_number if fill else (highest_number + 1)



# debugging
if __name__ == "__main__":
    start = time.time()
    print(random_midget("nsfw"))
    executionTime = start - time.time()

    print(f"Executed in:{executionTime}")
