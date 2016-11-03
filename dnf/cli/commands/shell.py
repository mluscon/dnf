# shell.py
# Shell CLI command.
#
# Copyright (C) 2016 Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#

from dnf.cli import commands
from dnf.i18n import _


import dnf
import logging
import shlex
import sys


logger = logging.getLogger('dnf')


class ShellCommand(commands.Command):

    aliases = ('shell',)
    summary = _('')

    MAPPING = {'repo': 'repo',
               'repository': 'repo',
               'exit': 'quit',
               'quit': 'quit',
               'run': 'run_ts',
               'ts': 'transaction',
               'transaction': 'transaction',
               'config': 'config',
               'resolvedep': 'resolve'
               }

    @staticmethod
    def set_argparser(parser):
        parser.add_argument('script', nargs='?', metavar=_('SCRIPT'),
                            help=_('Script to run in DNF shell'))

    def configure(self):
        demands = self.cli.demands
        demands.sack_activation = True
        demands.available_repos = True
        demands.resolving = False
        demands.root_user = True

    def run(self):
        if self.opts.script:
            self._run_script(self.opts.script)
        else:
            while True:
                line = dnf.i18n.ucd_input('> ')
                self._command(line)

    def _command(self, line):
        s_line = shlex.split(line)
        opts = self.cli.optparser.parse_main_args(s_line)
        if opts.command in self.MAPPING:
            getattr(self, '_' + self.MAPPING[opts.command])(s_line[1::])
        else:
            cmd_cls = self.cli.cli_commands.get(opts.command)
            if cmd_cls is not None:
                cmd = cmd_cls(self)
                try:
                    opts = self.cli.optparser.parse_command_args(cmd, s_line)
                    cmd.run()
                except:
                    pass

    def _config(self, args):
        pass

    def _repo(self, args):
        cmd = args[0]

        if cmd in ['list', None]:
            return

        if cmd in ['enable', 'disable']:
            repos = self.cli.base.repos
            for repo in args[1::]:
                r = repos.get_matching(repo)
                if r:
                    getattr(r, cmd)()
        self.base.fill_sack()

    def _resolve(self, args):
        if self.cli.base.transaction is None:
            self.cli.base.resolve(self.cli.demands.allow_erasing)

    def _run_script(self, file):
        try:
            with open(file, 'r') as fd:
                lines = fd.readlines()
                for line in lines:
                    if not line.startswith('#'):
                        self._command(line)
        except IOError:
            logger.info(_('Error: Cannot open %s for reading'.format(file)))
            sys.exit(1)

    def _run_ts(self, args):
        self.cli.base.do_transaction()

    def _transaction(self, args):
        pass

    def _quit(self, args):
        logger.info(_('Leaving Shell'))
        sys.exit(0)
