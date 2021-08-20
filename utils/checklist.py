from discord.ext import commands
import discord
import asyncio


import kotutil as kutil
from kotjson import responses


def list_embed(user_id, todo_or_done, range) -> discord.Embed:

    msg = ''
    chklist = kutil.give_checklist(_user_id=user_id, todo_or_done=todo_or_done)
    # key_list = [key for key in chklist]
    which_response_longer = responses.checklist_show_todo
    if len(which_response_longer) < len(responses.checklist_show_done):
        which_response_longer = responses.checklist_show_dosne

    for no, value in enumerate(chklist):
        if no <= range:
            value = value.strip()

            index = no
            # 2000 being discord's message character limit
            if len(msg + f"**[{index}]** {value}  \n") < 2000 - len(which_response_longer):
                msg += "**[{}]** {}\n".format(index, value)
            else: break  # character limit exceeded
        else: break  # range exceeded

    if todo_or_done == "todo":
        if msg == "":
            msg = responses.checklist_todo_empty
        embed = discord.Embed(description=msg, title=responses.checklist_show_todo)
        return embed

    elif todo_or_done == "done":
        if msg == "":
            msg = responses.checklist_done_empty
        embed = discord.Embed(description=msg, title=responses.checklist_show_done)
        return embed


async def list_add(ctx, name, todo_or_done) -> None:
    if name.isdigit():
        await ctx.send(responses.common_error)
        return None

    user_id = ctx.author.id
    if name:
        try:
            new_item_added = kutil.add_to_checklist(user_id,
                                                    task_name=name,
                                                    todo_or_done=todo_or_done)

        except ValueError:  # there's already an item of that name
            todo_list = kutil.give_checklist(user_id, todo_or_done=todo_or_done)
            items_with_the_name = []

            for filename in todo_list:
                stripped_filename = ''

                if filename.startswith(name):
                    stripped_filename = filename[len(name):]  # extract the '(number)' string

                if not stripped_filename: continue  # prevents trying to append ''

                # if only brackets and a number remain
                if      (stripped_filename[0] == "(" and stripped_filename[-1] == ")" and
                         stripped_filename[1:-1].isdigit()):
                    items_with_the_name.append(stripped_filename)

            next_name = kutil.next_name(elements=todo_list,
                                        range=100)  # max 100 chechlist items with the same name

            if not next_name:
                await ctx.send(responses.common_error)
                return None
            else:
                new_item_added = kutil.add_to_checklist(_user_id=user_id,
                                                        task_name=f"{name}({next_name})",
                                                        todo_or_done=todo_or_done)

        if new_item_added:
            await ctx.send(responses.checklist_item_added.format(name))
        else:
            await ctx.send(responses.common_error)


async def list_check(ctx, name, nuke=False) -> None:
    todo_list = kutil.give_checklist(ctx.author.id, "todo")

    if name not in todo_list:
        if name.isdigit() and len(todo_list) > int(name):
            name = todo_list[int(name)]
        else:
            await ctx.send(responses.checklist_item_noexist)
            return None

    done_list = kutil.give_checklist(ctx.author.id, "done")
    try:
        name_to_assign = name
        if name in done_list:
            
            name_numbers = set()
            for item_name in done_list:
                if item_name.startswith(name):
                    try:
                        # attempting to extract ({number}) from the end of the string
                        strip_ = item_name[len(name):]
                        if strip_[0] == "(" and strip_[-1] == ")":
                            number = strip_[1:-1]  # removing parenthesies
                            int(number)  # 'brute force' checking if it's indeed a number (raising exception if not)
                    except Exception: pass
                    else:
                        name_numbers.add(number)  # to use kutil.next_name on it later

            if name_numbers:
                name_to_assign = f"{name}({kutil.next_name(name_numbers, range_=99, fill=True)})"

        if name_to_assign:
            kutil.add_to_checklist(ctx.author.id, name_to_assign, todo_or_done="done")
            kutil.remove_from_checklist(ctx.author.id, name, 'todo')
            await ctx.send(responses.checklist_item_checked.format(name_to_assign))

        else:
            await ctx.send(responses.common_error)
            return None
    except Exception as e:
        print("Exception raised: " + str(e))
        await ctx.send(responses.common_error)
        return None


async def list_remove(ctx, name, todo_or_done, nuke=False) -> list or None:
    '''returns task-name and its index, or None if it was not found'''
    if nuke:
        kutil.remove_from_checklist(ctx.author.id, task_name=name, which_list=todo_or_done, nuke=True)
        await ctx.send(responses.checklist_nuked.format(todo_or_done))
        return todo_or_done

    check_list = kutil.give_checklist(ctx.author.id, todo_or_done=todo_or_done)
    if name.isdigit():
        try:
            index = int(name)
            task_name = check_list[index]
        except Exception:
            await ctx.send(responses.checklist_item_noexist)
            return None
    else:
        try:
            task_name = name
            # index = (no for no, key in check_list if key == name)
            for no, key in enumerate(check_list):
                if key == name:
                    index = no
                    break
        except Exception as e:
            await ctx.send(responses.checklist_item_noexist + e)
            return None
    try:
        kutil.remove_from_checklist(ctx.author.id, task_name=task_name, which_list=todo_or_done)
        return task_name, index
    except Exception:
        await ctx.send(responses.checklist_item_noexist)
        return None


@commands.command(aliases=['chlist'])
async def checklist(ctx, *args):
    '''everything after "--" is treated like a proper argument
    short options for mode
    long options for type of list [todo or done]
    dont specify long option for todo or use "--"
    '''

    possible_short_options = ('r', 'd', 'l', 'c')
    possible_special_options = ('a', 'x')
    possible_long_options = ('todo', 'done')
    possible_options = possible_special_options + possible_short_options + possible_long_options
    # # catching options etc.
    argsjoined = (' ').join(args)
    # allowing the use of words beggining with "-" (opportunity to bypass the option sniff thingy)
    quoted_args = set(argsjoined[argsjoined.find('"'): argsjoined.rfind('"')].split())
    argsjoined.replace(' '.join(quoted_args), '')
    args = argsjoined.split()  # converting it back to make manipulating the words easier

    long_options = []  # list(word for word in args if word.startswith('--'))
    short_options = set()  # list(word for word in args if word.startswith('-') and word not in long_options)
    proper_args = []

    do_for_all = False  # variable deciding whether or not to use the 'nuke' version of the command

    for word in args:
        if word == '--': continue
        if word.startswith('---'): raise ValueError

        elif word.startswith('--'):
            if word[2:] not in possible_long_options:
                raise NameError
            if not long_options:
                long_options.append(word)  # double dashes (options)

        elif word.startswith('-') and word[1] != '-':
            if len(word) > 1 and not word[1:].isalpha(): raise NameError
            for character in word[1:]:
                if character not in possible_options:
                    raise NameError
                short_options.add(character)  # single dashes (options)

        else: proper_args.append(word)  # words without any dashes

    proper_args += quoted_args

    # debug
    # await ctx.send(f"short: {short_options} \nlong: {long_options} \nproper args: {proper_args}")

    todo_or_done = long_options[0][2:] if long_options else "todo"  # todo, unless specified otherwise

    options = []
    # extracts one normal option (like delete, add, etc) and all special options
    for short_opt in short_options:
        if not options and short_opt in possible_short_options:
            options.append(short_opt)
            for special_opt in short_options:
                if special_opt in possible_special_options:
                    options.append(special_opt)
            break

    if 'a' in options:
        do_for_all = True

    if options[0] == 'l':
        # user_checklist = kutil.give_checklist(_user_id=ctx.author.id, todo_or_done=todo_or_done)
        range = 20 if not do_for_all else 1000
        await ctx.send(embed=list_embed(user_id=ctx.author.id, todo_or_done=todo_or_done, range=range))

    elif options[0] == 'r':
        name_ = (' ').join(proper_args)
        name_and_index = await list_remove(ctx=ctx, name=name_, todo_or_done=todo_or_done, nuke=do_for_all)
        if name_and_index and len(name_and_index) == 2:
            await ctx.send(responses.checklist_item_removed.format(f"{name_and_index[0]} [{name_and_index[1]}]"))

    elif options[0] == 'd':
        name_ = (' ').join(proper_args)
        await list_add(ctx=ctx, name=name_, todo_or_done='todo')

    elif options[0] == 'c':
        name_ = (' ').join(proper_args)
        await list_check(ctx=ctx, name=name_, nuke=do_for_all)

    if 'x' in options:
        await asyncio.sleep(3)
        await ctx.message.delete()
        # await bot_message.delete() # the 'ok, done' information


def setup(bot):
    bot.add_command(checklist)
