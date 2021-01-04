#!/usr/bin/env python3
import os
import sys
import re

print("--- enchant")
import enchant

d = enchant.Dict("en_US")

def check(text):
    ret = d.check(text)
    print("check string : " + text)
    print(ret)
    return ret

with open('file.txt', 'w') as txt:
    txt.write("enchant result\n")

# get flist
with open('flist.log', 'r') as flist:
    # get fname
    for fname in flist:
        fname = fname.replace('\n', '')
        with open(fname, 'r') as md:
            # get line
            for line in md:
                # split to word
                line = line.lower()
                words = line.split()
                for word in words:
                    # replace
                    word = word.replace('!', '')
                    word = word.replace('.', '')
                    word = word.replace('#', '')
                    word = word.replace(',', '')
                    word = word.replace('\n', '')
                    word = word.replace(':', '')
                    word = word.replace('"', '')
                    word = word.replace(']', '')
                    word = word.replace('[', '')
                    word = word.replace('*', '')
                    word = word.replace('`', '')
                    word = word.replace('\'', '')
                    word = word.replace('(', '')
                    word = word.replace(')', '')
                    word = word.replace('|', '')
                    NG_list = ["openembedded"]
                    #word = word.replace('-', '')
                    #word = word.replace('/', '')
                    #check string
                    SKIP = False
                    for item in NG_list:
                        if word == item:
                            SKIP = True
                    if SKIP == True:
                        continue
                    # skip empty
                    if not word:
                        continue

                    # check word
                    ret = check(word)
                    # save
                    if ret == False:
                        with open('file.txt', 'a') as txt:
                            txt.write(str(ret) + " : " + word)
                            txt.write("\n")

os._exit(0)

print("--- speller")

from autocorrect import Speller

spell = Speller(lang='en')

print(spell('caaaar'))
print(spell('mussage'))
print(spell('survice'))
print(spell('hte'))

from spellchecker import SpellChecker

spell = SpellChecker()

# find those words that may be misspelled
misspelled = spell.unknown(['something', 'is', 'hapenning', 'here'])

for word in misspelled:
    # Get the one `most likely` answer
    print(spell.correction(word))

    # Get a list of `likely` options
    print(spell.candidates(word))

