from discord import message
from discord.ext.commands.bot import Bot
from discord.ext import commands
import discord
import asyncio

import random

players=[]

class Player:
    def __init__(self, id, name):
        self.hand = []
        self.id = id
        self.name = name
        self.card_shown=False
        self.stack = [] # won cards to be shuffled if hand runs out
        self.played = [] # played (on table) cards
    
    def play_card(self):
        "removes a card from hand and returns it as string"

        if self.hand == []:
            if self.stack == []: # player's out
                return None 
            else: # put all cards from stack in hand 
                self.hand = self.stack
                random.shuffle(self.hand)
                del self.stack[:]
        card = self.hand[0]
        self.played.append(card)
        self.hand = self.hand[1:]

        return card

    def take_cards(self, cards:list):
        "reverse of play_card() (appends cards to the player's stack)"
        self.stack.append(cards)



class Card_deck:
    def __init__(self):
        self.deck = [
            '1c','2c','3c','4c','5c','6c','7c','8c','9c','10c','11c','12c','13c','14c',
            '1d','2d','3d','4d','5d','6d','7d','8d','9d','10d','11d','12d','13d','14d',
            '1h','2h','3h','4h','5h','6h','7h','8h','9h','10h','11h','12h','13h','14h',
            '1s','2s','3s','4s','5s','6s','7s','8s','9s','10s','11s','12s','13s','14s',
            'joker','joker'
        ]

    def shuffle(self):
        if self.deck:
            random.shuffle(self.deck)

    def deal(self,players):
        which_player=0
        # distributing one card at a time
        for card in self.deck:
            players[which_player].hand.append(card)

            # if it was the last player, give the following card to the firts one
            if which_player == len(players)-1: which_player=0
            else: which_player+=1
        
        #hopefully it managed to deal every card
        del self.deck[:]
        return None

class Games:
    def __init__(self) -> None:
        self.allgames = []   

    def gameadd(self, players) -> dict:
        "add a new game and return it as dict"
        game_ = {
            "players": players
        }    
        self.allgames.append(game_)
        return game_  
    
    def gamerm(self,players) -> None:
        self.allgames[:] = (x for x in self.allgames if x['players']!=players)

games=Games()

class Wojna(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    # editing the 'main' bot message - getting updates on whose turn it is etc
    async def msg_update(self,fields,msg) -> None:

        embed = discord.Embed()
        for _field in fields: 
            field = fields[_field]

            # inserting an invisible value to monkey patch an error
            if not field['value'].strip(): 
                field['value'] = "__ __"

            embed.add_field(name=field['name'],
                            value=field['value'],
                            inline=field['inline'])
        await msg.edit(embed=embed)
    

    async def get_winner(self,game):
        "Returns more than one winner if war"
        
        cards = {}
        for player in game['players']:
            cards[player.name] = player.played[-1] 


        ## check what player has the highest card, and if anyone has the same card as them
        highest_card = 0
        highest_card_players=''

        # highest card
        for player in cards.items():
            name,card = player
            # removing the house sign (useless here)
            if card == "joker": card = 15
            else: card = card[:-1]

            if card > highest_card:
                highest_card = card
                highest_card_players = name

        # check if only this player has a high card
        for player in cards.items():
            name,card = player
            if name == highest_card_players: continue 
            
            # removing the house sign (useless here)
            if card == "joker": card = 15
            else: card = card[:-1]

            
            if card == highest_card:
                if type(highest_card_players) != 'list':
                    highest_card_players = list(highest_card_players)
                    highest_card_players.append(name)
        
        return highest_card_players 

    @commands.command()
    async def start(self, ctx, pl1,pl2):
        args = [pl1, pl2]

        # ensuring the player count is <2:2>
        if not args or len(ctx.message.mentions) < 2:
            await ctx.send("Za mało graczy (oznacz też siebie)")
            return None
        elif len(ctx.message.mentions) > 2:
            await ctx.send("Panie, talii nie starczy. Weź mniej ludzi")
            return None


        # create a list of Player objects assigning each an id
        if not players:
            for member in ctx.message.mentions:
                players.append(Player(id=member.id, name=member.name))

        embed = discord.Embed()
        deck=Card_deck()
        deck.shuffle()
        curr_game = games.gameadd(players=players) # creates and remembers the created game
        deck.deal(players=players)

        embed.add_field(name="**Wojna Rozpoczęta.**",value="__ __", inline=False)
        msg = await ctx.send(embed=embed)
        embed.clear_fields()

        # following embeds' structure
        fields = {"main_field":{
            "name": "**Wojna Trwa.**",
            "value":" ",
            "inline": False,
        }}
        for _player in curr_game['players']:
            fields[_player.name] = {'name':_player.name,'value':' ','inline':True}

        
        # user input loop    
        while curr_game and not any(_player.hand==[] for _player in curr_game['players']):
            for _player in curr_game['players']:
                
                # default message (before any action)
                fields['main_field']['value'] = f"Tura: <@{_player.id}>"
                await self.msg_update(fields=fields, msg=msg)
                
                try: # getting the next player's message
                    player_response = await self.bot.wait_for(
                        event="message", 
                        check= lambda message: message.author.id == _player.id, 
                        timeout=10,
                        )
                except asyncio.TimeoutError: 
                    await ctx.send(f"<@{_player.id}> nie odpowiedział i przegrał walkowerem. Koniec gry")
                    del(curr_game)
                    break
                except Exception as e:
                    await ctx.send(e)


                else: # Processing user input
                    if player_response:

                        if player_response.content in ('myk'):
                            # if no cards on table yet
                            if fields[_player.name]['value'] == '__ __':
                                fields[_player.name]['value']=_player.play_card()

                            await self.msg_update(fields=fields, msg=msg)
                            pass # MYK
                        elif player_response.content in ('blef'):
                            pass #BLEF (przetasowanie ręki (xd) )
                        elif player_response.content in ('kant'):
                            pass #KANT (pierdoła typu podmienienie następnej ('zerowej') karty z kolejną)
                
                #await self.get_table(fields=fields)
            try: curr_game
            except: break
            #TODO taking cards from _player.name['value'] to determine whether to make war or declare a winner

def setup(bot):
    bot.add_cog(Wojna(bot))
