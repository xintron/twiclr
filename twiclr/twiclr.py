# Copyright (c) 2012, Marcus Carlsson <carlsson.marcus@gmail.com>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Marcus Carlsson nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os

import urwid
from twython.twython import Twython, TwythonError

import command
from messages import messages as _

command_handler = None

class EditHandler(urwid.Edit):


    def keypress(self, size, key):
        if key == 'enter':
            data = self._edit_text.split(None, 1)
            cmd = data[0]
            args = data[1].split() if len(data) > 1 else []
            command_handler.parse_command(cmd, args)
            return 'esc'
        if key == 'tab':
            if len(self._edit_text.split()) == 1:
                command_handler.tab_completion(self, self._edit_text)
            return
        return super(EditHandler, self).keypress(size, key)

class MainHandler:


    palette = [
        ('status', 'white,bold', 'dark gray'),
        ('error', 'dark red,bold', 'black'),
        ('info', 'white,bold', 'default'),
    ]

    def __init__(self):
        global command_handler
        command_handler = command.CommandHandler(self)

        self.t = None

        if os.environ['XDG_CONFIG_HOME']:
            path = os.environ['XDG_CONFIG_HOME']
        else:
            path = os.environ['HOME']
        self.basepath = os.path.join(path, 'twiclr')
        if not os.path.isdir(self.basepath):
            os.mkdir(self.basepath)

        self.test_login()

    def run(self):
        self.screen = urwid.raw_display.Screen()
        self.screen.tty_signal_keys(*['undefined'] * 5)

        self.footer = {
                'edit': EditHandler(),
                'error': urwid.Text(('error', '')),
                'list': urwid.ListBox(urwid.SimpleListWalker([])),
        }

        if self.t:
            msg = _['welcome_login'].format(**self.user)
        else:
            msg = _['welcome_guest']
        self.body = urwid.SimpleListWalker([
            urwid.Text('twiclr\nTerminal twitter client.', align='center'),
            urwid.Text(msg, align='center')
        ])

        self.statusbar = urwid.Text(('status', ''))
        self.inner = urwid.Frame(urwid.Filler(urwid.Pile(self.body)),
            footer=urwid.AttrMap(self.statusbar, 'status')
        )
        self.outer = urwid.Frame(self.inner,
                footer=self.footer['edit'])

        self.loop = urwid.MainLoop(self.outer, self.palette, self.screen,
                unhandled_input=self.unhandled_input, handle_mouse=False)
        self.loop.run()

    def test_login(self):
        if not os.path.isfile(os.path.join(self.basepath, 'keys.txt')):
            return
        with open(os.path.join(self.basepath, 'keys.txt')) as f:
            data = f.readlines()
        self.oauth_data = {}
        for d in data:
            key, value = d.split('=', 1)
            self.oauth_data[key] = value.rstrip('\n')

        try:
            self.t = Twython(command.konsumer_ceys[0],
                    command.konsumer_ceys[1],
                    self.oauth_data['oauth_token'],
                    self.oauth_data['oauth_token_secret'])
            self.user = self.t.verifyCredentials()
        except TwythonError:
            self.t = None
        
    def unhandled_input(self, key):
        # Set focus to status-edit
        if key == ':':
            self.outer.set_footer(self.footer['edit'])
            self.footer['edit'].set_caption(':')
            self.outer.set_focus('footer')
        elif key == 'esc':
            self.footer['edit'].set_caption('')
            self.footer['edit'].set_edit_text('')
            self.outer.set_focus('body')

    def error(self, msg):
        self.footer['error'].set_text(('error', msg))
        self.outer.set_footer(self.footer['error'])

    def show_info(self, msg):
        self.footer['error'].set_text(('info', msg))
        self.outer.set_footer(self.footer['error'])
