#!/usr/bin/python3 -u
from asyncore import write
from ssl import _create_unverified_context
import subprocess
import sys
import json
import chess
import chess.pgn
import chess.polyglot
import re
from re import search
from datetime import datetime

# Initialize variables 
engMove = ""
side = "W"
moveList = ""
moveIndex = 1
pIndex = 0
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# LaTex ouput
tex = open('report.tex','w')

def outputTexHeader():
    texHeader = ("\\documentclass[a4paper]{article}\n"
"\\usepackage[utf8]{inputenc}\n"
"\\usepackage[english]{babel}\n"
"\\usepackage{geometry}\n"
"\\usepackage{adjustbox}\n"
"\\usepackage[ps]{skak}\n"
"\\usepackage{enumitem}\n"
"\\usepackage{multicol}\n"
"\\usepackage{fancyhdr}\n"
"\\pagestyle{fancy}\n"
"\\fancyhf{}\n"
"\\lhead{AnnotateT Analysis Report}\n"
"\\rhead{"+dt_string+"}\n"
"\\fancyfoot[CE,CO]{Page \\thepage}\n"
"\\begin{document}\n"
"\\setlength{\\parindent}{0pt}\n"
"\\begin{multicols}{2}\n"
"\\newpage\n")
    tex.write(texHeader)

def outputFooter():
    texFooter = ("\\end{multicols}\n"
"\end{document}\n")
    tex.write(texFooter)
    
# Engine parameters
#prefFile = open('prefs.json')
#prefs = json.load(prefFile)
#engine = prefs['engine']

# ? depth: use n-depth, if it's -1 just go till its done
# allow each of these params  to have a corresponding cli args options

# ? Parse cli args to overwrite defaults

# ?? ECO.pgn use to determine what opening line is used ??
# ?? used eco based polyglot book ??
reader = chess.polyglot.open_reader('book.bin')

# Create engine process
threads=4
depth=24
engine = "./dragon"
proc = subprocess.Popen([engine],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='ascii')

# Fire up engine
proc.stdin.write("uci\n")	
proc.stdin.flush()

# Get info
for line in iter(proc.stdout.readline,''):
	if search("id name", line):
		nameList = line.split('id name')
		eVersion = nameList[1].rstrip()
		#print(eVersion)
	if search("uciok", line):
		break

print(eVersion)

# Set engine parameters
proc.stdin.write("setoption name Threads value {}\n".format(threads))	
proc.stdin.flush()


# ?? Start of by parsing a game move by move and get a fen on each position for passing to the
# ?? Engiune
board = chess.Board()
pgn = open("sample.pgn")
game = chess.pgn.read_game(pgn)

outputTexHeader()

# Get Headers
h_event = game.headers["Event"]
h_site = game.headers["Site"]
h_date = game.headers["Date"]
h_round = game.headers["Round"]
h_white = game.headers["White"]
h_black = game.headers["Black"]
h_result = game.headers["Result"]

tex.write("\\newpage\n")
tex.write("Event: "+h_event+"\n")
tex.write("Site: "+h_site+"\n")
tex.write("Date: "+h_date+"\n")
tex.write("Round: "+h_round+"\n")
tex.write(h_white+ " vs. " + h_black + "\n")
tex.write("Result: " + h_result)

# For report you want at the top info from the game itself like the player names
# Date, White, Black, Result, Engine Name

# Ok time to fire up the engine!
proc.stdin.write("ucinewgame\n")
proc.stdin.flush()

# Parse the game
for move in game.mainline_moves():
    curFen = board.fen()

    if(side == "W"):
        moveList = moveList + str(moveIndex) + ". " + board.san(move) + " "
    elif(moveList == ""):
        moveList = moveList + str(moveIndex-1) + "... " + board.san(move) + " "
    else:
        moveList = moveList + board.san(move) + " "

    # Is this in opening book? If so move on
    inBook = sum(1 for _ in reader.find_all(board))
    
    if(inBook == 0):

        # Parse bestmove, if the same as move move on, else get PV for report
        fenline = 'position fen {}\n'.format(curFen)
        proc.stdin.write(fenline)
        proc.stdin.flush()
        proc.stdin.write("go depth {}\n".format(depth))
        proc.stdin.flush()

        for line in iter(proc.stdout.readline,''):
            if search("info depth", line):
                if re.search(r'[^i]pv(.*)', line): # regex fu  
                    pv = re.search(r'[^i]pv(.*)', line).group(1)
            if search("bestmove", line):
                engResult = line.split(' ')
                engMove = engResult[1]
                engMove = engMove.strip()
                if(str(engMove) != str(move)):
                    print(moveList)
                    print("Engine Recommends->   Move: ", move, " Engine move: ", engMove, " PV: ", pv)
                    ##tex.write(moveList)
                    #tex.write("\n\\linebreak\n")
                    tex.write("\\newgame\n\n")
                    tex.write(moveList+"\n\n")
                    if(side == 'W'):
                        tex.write("\\textbf{"+str(moveIndex)+" "+board.san(chess.Move.from_uci(engMove))+"}\n\n")
                    else:
                        tex.write("\\textbf{"+str(moveIndex-1)+"... "+board.san(chess.Move.from_uci(engMove))+"}\n\n")
                    tex.write("PV: "+pv+"\n\n")
                    tex.write("\\fenboard{"+curFen+"}\n")
                    tex.write("\\showboard\n")
                    tex.write("\\linebreak\n")
                    moveList = ""
                    pIndex += 1
                    # use 2nd game, use curFen make computer move, get new fen and use for report
                if(pIndex==4):
                    tex.write("\\end{multicols}\n")
                    tex.write("\\pagebreak\n")
                    tex.write("\\begin{multicols}{2}\n")
                    pIndex=0
                break

    #print(curFen)
    #print(board.san(move)) 
    #print(move)
    #print(engMove)
    #print("Master->   Move: ", move, " Engine move: ", engMove)

    # Flip sides
    if(side=="W"):
        side="B"
        moveIndex += 1
    else:
        side="W"

    board.push(move)

outputFooter()
# Cleanup
tex.close
proc.terminate()
