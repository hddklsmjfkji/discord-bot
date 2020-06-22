import regex as re
import discord
import random
import os
from dotenv import load_dotenv
import tmdbv3api 

load_dotenv()

DISC_TOKEN = os.getenv('DISCORD_TOKEN')
TMDB_TOKEN = os.getenv('TMDB_API_KEY')
client = discord.Client()
movie = tmdbv3api.Movie()
person = tmdbv3api.Person()


#below regex formatting function taken from https://stackoverflow.com/a/38832133. Trims the biography# to one sentence
def format_string(input_string):
    keywords = set(['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Rev.', 'Capt.', 'Lt.-Col.', 
            'Col.', 'Lt.-Cmdr.', 'The Hon.', 'Cmdr.', 'Flt. Lt.', 'Brgdr.', 'Wng. Cmdr.', 
            'Group Capt.' ,'Rt.', 'Maj.-Gen.', 'Rear Admrl.', 'Esq.', 'Mx', 'Adv', 'Jr.'] )
    regexes = '|'.join(keywords)  # Combine all keywords into a regex.
    split_list = re.split(regexes, input_string)  # Split on keys.
    removed = re.findall(regexes, input_string)  # Find removed keys.
    newly_joined = split_list + removed  # Interleave removed and split.
    newly_joined[::2] = split_list
    newly_joined[1::2] = removed
    space_regex = '\.\s*'

    for index, section in enumerate(newly_joined):
        if '.' in section and section not in removed:
            newly_joined[index] = re.sub(space_regex, '.\n', section)
    return ''.join(newly_joined).strip()


#console notif for the user
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


#main bot working here
@client.event
async def on_message(msg) :
    if msg.author == client.user :
        return

#calling name (bhendi)
    if msg.content.startswith('bhendi'):
        userip = msg.content

        #movie recommendation
        if 'rec' in userip :
            movie_name = userip[userip.index('rec') + 4 :]
            search = movie.search(movie_name)
            mov_id = 0
            for res in search :
                mov_id = res.id
                break
            try:
                recommend = movie.similar(movie_id = mov_id)
                if recommend :
                    await msg.channel.send('__PEHLE 10 ICH DIKHAARA__')
                    for r in range(0,min(len(recommend),10)) :
                        title = '**' + recommend[r].title + '**'
                        await msg.channel.send(title)
                else :
                    await msg.channel.send('Bahut unique movie hai ye.')
            except :
                await msg.channel.send('KYA TUTUL PUTUL')


        #get details of a person
        if 'whois' in userip :
            person_name = userip[userip.index('whois') + 6 :]
            search_res = person.search(person_name,1)
            for celeb in search_res :
                pid = person.details(celeb.id)
                bio = pid.biography
                biolist = format_string(bio)
                biolist = biolist[:biolist.find('.')+1]
                name = '**' + pid.name + '**'
                await msg.channel.send(name)
                if(biolist) :
                    await msg.channel.send(biolist)
                else :
                    await msg.channel.send('Mereko nahi pata')


        #get ratings of a movie
        if 'howis' in userip :
            movie_name = userip[userip.index('howis') + 6 :]
            search = movie.search(movie_name)
            if len(search) > 1  and movie_name != search[0].title :
                await msg.channel.send('Specify the movie dumdum. Type again with the correct name')
                for res in search :
                    await msg.channel.send(res.title)
            elif len(search) == 0 :
                await msg.channel.send('Chutiya mat bana bhendi.')
            else :
                await msg.channel.send(search[0].title + ' has rating of ' + str(100 - movie.details(search[0].id).popularity) + '%')


        #send love
        if 'gib-pyaar' in userip :
            msg1 = 'Hey ' + msg.mentions[0].mention.format(msg) + '. I love you <3'
            await msg.channel.send(msg1)

client.run(DISC_TOKEN)