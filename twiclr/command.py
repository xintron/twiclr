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
import urlparse
import inspect

import oauth2 as oauth
import urwid
from twython.twython import TwythonError, TwythonRateLimitError

from messages import messages as _

commands = [
    ('login',),
    ('new',),
    ('pincode',),
    ('quit',),
]

class CommandHandler(object):


    columns = []

    def __init__(self, main):
        self.main = main

    def add_column(self, column):
        if column not in self.columns:
            self.columns.append(column)

    def remove_column(self, column):
        if column in self.columns:
            self.columns.remove(column)

    def tab_completion(self, widget, command):
        for cmd in commands:
            if cmd[0].startswith(command):
                widget.set_edit_text(cmd[0]+' ')
                widget.set_edit_pos(len(cmd[0])+1)

    def parse_command(self, command, args):
        for cmd in commands:
            if cmd[0].startswith(command):
                if hasattr(self, 'on_'+cmd[0]):
                    func = getattr(self, 'on_'+cmd[0])
                    fargs, vargs, keywords, defaults = inspect.getargspec(func)
                    minimum = len(fargs)-(len(defaults) if defaults else 0)-1
                    if minimum > len(args):
                        self.main.error('Arguments needed: {}. Only {} '\
                                'given.'.format(minimum, len(args)))
                    else:
                        func(*args)
                return
        self.main.error(_['command_not_found'].format(command))

    def on_quit(self):
        raise urwid.ExitMainLoop()

    def on_login(self, username):
        self.request = authorize_user(username)
        self.request['username'] = username
        self.main.body[1].set_text(_['login_instructions'].format(
                    'https://api.twitter.com/oauth/authorize',
                    self.request['oauth_token'])
        )

    def on_pincode(self, pincode):
        self.request['oauth_verifier'] = pincode
        keys = authorize_user(self.request['username'], self.request)
        with open(os.path.join(self.main.basepath, 'keys.txt'), 'a') as f:
            f.write('oauth_token={}\noauth_token_secret={}'.format(
                keys['oauth_token'], keys['oauth_token_secret']))

        self.main.test_login()
        if self.main.t:
            self.main.body[1].set_text(
                    _['welcome_login_new'].format(**self.main.user))

    def on_new(self, *msg):
        try:
            content = self.main.t.updateStatus(status=' '.join(msg))
            self.main.show_info(' '.join([_['post_success'],
                'Your post has id: {id}'.format(**content)]))
        except (TwythonError, TwythonRateLimitError):
            self.main.error('Could not update status')

konsumer_ceys = ('gP11VW0dsGsFROtuyrSAxw',
        '6QnHYOvwdk10gOARfWa7l2zGCljnEp5PPT6y1i5e54')

def authorize_user(nickname, request=None):
    consumer = oauth.Consumer(*konsumer_ceys)
    
    if not request:
        client = oauth.Client(consumer)

        resp, content = client.request(
                'https://api.twitter.com/oauth/request_token', 'GET')

        if resp['status'] != '200':
            raise Exception('Invalid response {}'.format(resp['status']))
        
        request_data = dict(urlparse.parse_qsl(content))
        return request_data
    else:
        try:
            token = oauth.Token(request['oauth_token'],
                    request['oauth_token_secret'])
            token.set_verifier(request['oauth_verifier'])
        except (KeyError):
            print('The following keys need to be provided in the \
            request-object: "oauth_token", "oauth_token_secret" \
            "oauth_verifier"')

        client = oauth.Client(consumer, token)

        resp, content = client.request(
                'https://api.twitter.com/oauth/access_token', 'POST')
        if resp['status'] != '200':
            raise Exception('Invalid response {}'.format(resp['status']))
        access_token = dict(urlparse.parse_qsl(content))

        return access_token
