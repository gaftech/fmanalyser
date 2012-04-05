# -*- coding: utf-8 -*-
from fmanalyser.utils.command import BaseCommand
from fmanalyser.gui.controller import Controller
import sys

class Command(BaseCommand):
    
    def execute(self):
        controller = Controller(client_worker=self.worker)
        controller.run()

def main():
    sys.exit(Command().run())

if __name__ == '__main__':
    main()