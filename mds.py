#! /usr/bin/env python
"""
# By: Charles Brandt [ccbrandt at indiana dot edu] and edited by Tessa Bent
# On: *2014.11.04 15:38:11
# License:  MIT

# Requires: pyglet, areaui

"""
import random, os, codecs
import json
import datetime

import pyglet
# disable error checking for increased performance
pyglet.options['debug_gl'] = False

from pyglet.media import Player

from areaui.area import Area, RootArea
from areaui.widgets import Toggle, WideDialog, OKMessage, Message

from resources.widgets import SetupDialog, Instructions, BlockWait
from resources.ssf import SSF
from resources.waves import add_waves

class Experiment(object):
    def __init__(self, area):
        self.log = None
        self.blocks = []
        self.answers = []
        self.area = area
        self.cur_block = 0
        self.cur_trial = 0

        self.sound_file = None
        self.noise_file = None
        self.answer = ''

        self.sound = None

    def make_orders(self, block):

        #shuffle the order for the block:
        random.shuffle(block)
        #print block

        #now slice it up
        sections = [ block[:20], block[20:40], block[40:60], block[60:], ]

        new_block = []

        #speaker 1 is native and speaker 2 is nonnative
        for index, section in enumerate(sections):
            for item in section:
                #print item
                #print item[0]
                if (index == 0) or (index == 1):
                    speaker = 1
                if (index == 2) or (index == 3):
                    speaker = 2

                full_speaker = "SP" + str(speaker)
                wav = item[0].replace('X', full_speaker)
                full_wav = 'Speaker %s/%s.wav' % (speaker, wav)

                s = os.path.join('resources/sounds', full_wav)

                if (index == 0):
                    n = 'resources/noiseEnergetic70.wav'
                elif (index == 1):
                    n = 'resources/noiseInformational73.wav'
                elif (index == 2):
                    n = 'resources/noiseEnergetic68.wav'
                elif (index == 3):
                    n = ''

                if n:
                    d = os.path.join(self.generated, "%s.wav" % wav)
                    add_waves(s, n, d)
                    self.debug.write("%s: add_waves: %s\n" % (datetime.datetime.now(), d))
                else:
                    d = s

                #print s, n, d
                #s = source, d = destination, n = noise

                item[0] = d
                item.append(n)
                new_block.append(item)
            #print new_section

        random.shuffle(new_block)
        #print new_block
        #exit()

        return new_block


    def setup(self, response):
        #print response
        self.subject_id = response[0]

        #order = response[1]

        if self.subject_id:
            self.generated = "output/%s/generated" % self.subject_id
            if not os.path.exists(self.generated):
                os.makedirs(self.generated)
        else:
            print "NO SUBJECT ID SPECIFIED!"
            exit()

        #make log:
        #log_name = 'DIF-%s-%s.csv' %  (self.subject_id, order)
        log_name = 'MDS-%s.csv' %  (self.subject_id)
        log_file = os.path.join('output', self.subject_id, log_name)
        self.log = codecs.open(log_file, 'a', encoding='utf-8')
        #self.log = codecs.open(log_file, 'w+', encoding='utf-8')
        #print log_file

        #make debug file:
        #debug_name = 'debug-DIF-%s-%s.txt' %  (self.subject_id, order)
        debug_name = 'debug-MDS-%s.txt' %  (self.subject_id)
        debug_file = os.path.join('output', self.subject_id, debug_name)
        self.debug = codecs.open(debug_file, 'a', encoding='utf-8')
        #self.debug.write("%s: starting setup for session: %s, order: %s\n" % (datetime.datetime.now(), self.subject_id, order))
        self.debug.write("%s: starting setup for session: %s\n" % (datetime.datetime.now(), self.subject_id))


        #right now, order == A == Native
        #order == B == NonNative
        #['Native', 'Nonnative']
        #if order == 'A':
        ## if order == 'Native':
        ##     source = 'NativeNew.ssf'
        ## #elif order == 'B':
        ## elif order == 'Nonnative':
        ##     source = 'NonnativeNew.ssf'
        ## else:
        ##     #shouldn't ever get this with radio button
        ##     raise ValueError, "UNKNOWN ORDER: %s" % order
        source = "mds.ssf"

        #position_name = 'DIF-%s-%s-position.json' %  (self.subject_id, order)
        position_name = 'MDS-%s-position.json' %  (self.subject_id)
        self.position_file = os.path.join('output', self.subject_id, position_name)
        if os.path.exists(self.position_file):
            self.debug.write("%s: existing position file found %s\n" % (datetime.datetime.now(), self.position_file))
            position = codecs.open(self.position_file, 'r', encoding='utf-8')
            state = json.loads(position.read())
            position.close()
            self.blocks = state['blocks']
            self.cur_block = state['cur_block']
            self.cur_trial = state['cur_trial']

            self.area.clear()
            lines = []
            lines.append("Resuming session for subject: %s" % (self.subject_id))
            lines.append("block: %s, trial: %s" % (self.cur_block, self.cur_trial))
            lines.append("Press OK to resume")
            complete = OKMessage(self.start_trial, lines,
                                 color=(.5, .5, .5, 1))
            self.area.add(complete)
            self.area.rearrange()
            self.debug.write("%s: resume message shown\n" % (datetime.datetime.now()))

        else:
            self.debug.write("%s: setting up order for new user\n" % (datetime.datetime.now()))
            #initialize order for first run:
            #load blocks
            #fp = os.path.join('resources/ssf/', source)
            fp = os.path.join('resources/', source)
            block = SSF(fp)

            print ''
            print 'showing values read from ssf'
            for i in block:
                print i
            ## print "^^^ PRE  ^^^"
            ## print "vvv POST vvv"

            #get the practice blocks first:
            #first = block[0]
            #block.remove(first)
            #last = block[-1]
            #block.remove(last)

            practice = []

            practice.append( ['resources/sounds/Practice/MDS-SP1Practice1.wav', 'he put on an old baseball glove', 'noise'] )
            practice.append( ['resources/sounds/Practice/MDS-SP1Practice2.wav', 'there was a terrible thunderstorm', 'noise'] )
            practice.append( ['resources/sounds/Practice/MDS-SP2Practice3.wav', 'we should have considered the juice', 'noise' ] )
            practice.append( ['resources/sounds/Practice/MDS-SP2Practice4.wav', 'they had a problem with the bloom', 'quiet' ] )



            print practice
            print
            print block

            self.blocks = [ practice ]
            #then add everything else:
            #main_block = block[4:]
            main_block = block
            print len(main_block)

            orders = False
            attempt = 1
            while not orders:
                print
                print "generating orders, attempt: %s" % attempt
                orders = self.make_orders(block)
                attempt += 1

                print "ORDERS:", orders

            self.blocks.append(orders[:])
            #self.blocks.append(orders[36:])

            ## #now sort orders, then simplify list
            ## orders.sort()
            ## new_block = []
            ## for item in orders:
            ##     #match the original trial that has the answer paired..
            ##     matches = 0
            ##     for trial in block[4:]:
            ##         #print item[1], ' == ', trial[0], '?'
            ##         if item[1] == trial[0]:
            ##             new_block.append( trial )
            ##             matches += 1
            ##     if matches != 1:
            ##         raise ValueError, "found more than one match: %s" % new_block

            ##     #this will only add the wav file
            ##     #new_block.append( [item[1]] )

            ## print new_block
            ## print len(new_block)
            ## assert len(new_block) == 60


            #exit()

            if self.subject_id == "demo":
                #new_blocks = [ self.blocks[0] ]
                new_blocks = []
                for b in self.blocks:
                    new_blocks.append( b[0:2] )
                self.blocks = new_blocks

            position = codecs.open(self.position_file, 'w', encoding='utf-8')
            state = {'blocks': self.blocks, 'cur_block':self.cur_block, 'cur_trial':self.cur_trial}
            position.write(json.dumps(state))
            position.close()
            self.debug.write("%s: new order stored to position file\n" % (datetime.datetime.now()))

            #print self.blocks
            #print len(self.answers)

            #self.start_trial()
            self.show_instructions()

    def show_instructions(self):
        self.area.clear()
        lines = [ 'In this part of the experiment, you will listen to phrases and type in what you hear. Some of these phrases will be presented without noise, some will be mixed with noise, and some will be mixed with other phrases from a competing talker. After the practice trials, the phrases will contain real English words but will not make sense (e.g., tripping down the horses). Your job is to pay close attention to the phrase, and try to figure out what is being said. For the trials with a competing talker, you should pay attention to the talker who starts half a second after the first talker. After each phrase, you should type what you heard. If you are unsure, type your best guess. Press Next to begin.' ]
        instructions = Instructions(self.area.window, lines, action=self.start_trial)
        self.area.add(instructions)
        self.area.rearrange()
        #self.area.window.push_handlers(self.layout)

    def start_trial(self, gx=0, gy=0, button=None, modifiers=None):
        self.debug.write("%s: start_trial\n" % (datetime.datetime.now()))
        self.area.clear()
        play = Toggle('Play', 'Playing...', 'Play', w=200, h=50,
                      on_action=self.play_next, color=(.5, .5, .5, 1))
        self.area.add(play)
        self.area.rearrange()

        #get current sound
        #print self.cur_block
        #print self.cur_trial
        #print self.blocks[self.cur_block]
        print self.blocks[self.cur_block][self.cur_trial]
        self.sound_file = self.blocks[self.cur_block][self.cur_trial][0]
        self.noise_file = self.blocks[self.cur_block][self.cur_trial][2]

        #print self.sound_file
        self.debug.write("%s: using sound_file: %s\n" % (datetime.datetime.now(), self.sound_file))

        cur_trial = self.blocks[self.cur_block][self.cur_trial]
        if len(cur_trial) > 1:
            self.answer = self.blocks[self.cur_block][self.cur_trial][1]
        else:
            self.answer = ''

        if self.answer is '':
            print "Could not find the answer for file: %s" % self.sound_file
            print "expecting answers, so exiting."
            exit()

        self.debug.write("%s: using answer: %s\n" % (datetime.datetime.now(), self.answer))

        #s = os.path.join('resources/sounds', self.sound_file)

        #TESSA I think I need to uncomment this but when I tried to do this it didn't work. not sure what i need to uncomment and what not
        #n = 'resources/noise.wav'
        ## n = 'resources/8TalkerBabbleNandNN67dB.wav'
        #d = os.path.join(self.generated, self.sound_file)
        #add_waves(s, n, d)
        #self.debug.write("%s: add_waves: %s\n" % (datetime.datetime.now(), d))

        #load
        #self.sound = pyglet.media.StaticSource(pyglet.media.load(d))
        self.sound = pyglet.media.StaticSource(pyglet.media.load(self.sound_file))
        self.debug.write("%s: sound loaded\n" % (datetime.datetime.now()))

    def play_next(self, gx=0, gy=0, button=None, modifiers=None):
        """
        want a small delay after pushing button and hearing sound
        """
        self.debug.write("%s: play_next called\n" % (datetime.datetime.now()))
        pyglet.clock.schedule_once(self.play_after, .5)

    def play_after(self, dt=0):
        self.debug.write("%s: starting play_after\n" % (datetime.datetime.now()))
        #play  sound generated in add_waves
        #on eos, get_response()
        player = Player()
        #self.player.eos_action = 'pause'

        #probably can't use on_eos on windows
        #player.on_eos = self.get_response
        player.queue(self.sound)
        #self.update_layout()

        #self.player.seek(0)
        #player.dispatch_events()
        #Area.on_mouse_press(self, gx, gy, button, modifiers)
        player.play()
        self.debug.write("%s: player.play() called\n" % (datetime.datetime.now()))
        #print "duration: ", self.sound.duration
        #this is instead of player.on_eos:
        pyglet.clock.schedule_once(self.get_response, self.sound.duration)

    def get_response(self, dt=0):
        self.debug.write("%s: get_response called via player.on_eos\n" % (datetime.datetime.now()))
        self.area.clear()
        respond = WideDialog('Response:', action=self.set_response, debug=self.debug,
                             color=(.5, .5, .5, 1))
        self.area.add(respond)

        respond.field.set_focus()
        respond.field.select_all()

        self.area.rearrange()

        #self.area.debug()

    def set_response(self, response):
        self.debug.write("%s: set_response called from WideDialog\n" % (datetime.datetime.now()))
        #print "RESPONSE! %s" % response
        parts = [ self.sound_file, self.answer, response, self.noise_file ]
        #print parts
        self.log.write(','.join(parts) + '\n')

        #increment current trial
        self.cur_trial += 1
        pause = False
        if len(self.blocks[self.cur_block]) <= self.cur_trial:
            #we've reached the end of a block
            self.cur_block += 1
            self.cur_trial = 0
            #either way we want to wait for some amount of time here
            pause = True
            if len(self.blocks) <= self.cur_block:
                self.log.close()
                self.area.clear()
                lines = []
                lines.append("You are finished with this part of the experiment.")
                lines.append("Please exit the booth quietly.")
                complete = Message(lines, color=(.5, .5, .5, 1))
                self.area.add(complete)
                self.area.rearrange()
                self.debug.write("%s: Experiment finished\n" % (datetime.datetime.now()))
                #print "ALL DONE!"
                #exit()
            else:
                self.area.clear()
                if self.cur_block == 1:
                    lines = []
                    lines.append("Practice trials complete.")
                    lines.append("Press OK when you are ready to begin the experiment.")
                    complete = OKMessage(self.start_trial, lines,
                                         color=(.5, .5, .5, 1))
                else:
                    #time to wait in minutes
                    break_wait = 3
                    seconds = break_wait * 60

                    #subtract 1 to get rid of practice block in count
                    complete = BlockWait(self.area.window, self.cur_block-1,
                                         len(self.blocks)-1,
                                         action=self.start_trial)

                    #self.layout.update_layout()
                    #self.push_handlers(self.layout)

                    if self.subject_id == "demo":
                        pyglet.clock.schedule_once(complete.show_button, 5)
                    else:
                        pyglet.clock.schedule_once(complete.show_button, seconds)


                self.area.add(complete)
                self.area.rearrange()
                self.debug.write("%s: Block complete message\n" % (datetime.datetime.now()))
                #print "NEW BLOCK!"

        position = codecs.open(self.position_file, 'w', encoding='utf-8')
        state = {'blocks': self.blocks, 'cur_block':self.cur_block, 'cur_trial':self.cur_trial}
        position.write(json.dumps(state))
        position.close()
        self.debug.write("%s: position saved in set_response()\n" % (datetime.datetime.now()))

        if not pause:
            self.start_trial()


# create a basic pyglet window
window = pyglet.window.Window(800, 500, caption='MDS', vsync=True)
window.set_fullscreen()

#w1 = RootArea(window, align=('center', 'center'), color=(0.5, 0.5, 1.0, 1.0))
w1 = RootArea(window, align=('center', 'center'), color=(0, 0, 0, 1.0))
e = Experiment(w1)

dialog = SetupDialog(window, 'Please enter the Subject ID:', e.setup)
w1.add(dialog)

#print dialog.root().name
dialog.field.set_focus()
dialog.field.select_all()
w1.rearrange(keep_dimensions=True)

window.push_handlers(w1)

def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        if (modifiers & pyglet.window.key.MOD_CTRL) or (modifiers & pyglet.window.key.MOD_SHIFT):
            exit()

#want to override the default so that ESCAPE is not available
window.on_key_press = on_key_press

@window.event
def on_draw():
    window.clear()
    w1.draw()

# finally, run the application...
pyglet.app.run()
