# TODO: Exclude option
import fnmatch
import logging
import os
import re
import sys
import unicodedata


log = logging.getLogger("fileops")


def configure_logger(loglevel=2, quiet=False):
    "Creates the logger instance and adds handlers and formatting."
    logger = logging.getLogger()

    # Set the loglevel.
    if loglevel > 3:
        loglevel = 3  # Cap at 3 to avoid index errors.
    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    logger.setLevel(levels[loglevel])

    logformat = "%(asctime)-14s %(levelname)-8s %(name)-8s %(message)s"

    formatter = logging.Formatter(logformat, "%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.info("Added logging console handler.")

    if quiet:
        log.info("Quiet mode: logging disabled.")
        logging.disable(logging.ERROR)


class FileOps(object):

    def __init__(self, quiet=False, verbosity=1,
                 dirsonly=False, filesonly=False, recursive=False,
                 hidden=False, simulate=False, interactive=False, prompt=False,
                 noclobber=False, keepext=True, count=None, regex=False,
                 exclude=None, accents=False, upper=False, lower=False,
                 nowords=False, media=False):
        # Universal options:
        self._dirsonly = dirsonly  # Only edit directory names.
        self._filesonly = False if dirsonly else filesonly  # Only file names.
        self._recursive = recursive  # Look for files recursively
        self._hidden = hidden  # Look at hidden files and directories, too.
        self._simulate = simulate  # Simulate renaming and dump result to stdout.
        self._interactive = interactive  # Confirm before overwriting.
        self._prompt = prompt  # Confirm all rename actions.
        self._noclobber = noclobber  # Don't overwrite anything.
        self._keepext = keepext  # Don't modify extensions.
        self._count = count  # Adds numerical index at position count in target.
        self._regex = regex  # Use regular expressions instead of glob/fnmatch.
        self._exclude = exclude  # List of strings to exclude from targets.
        self._accents = accents
        self._lower = lower
        self._upper = upper
        # Initialize GUI options.
        self._autostop = False
        self._mirror = False
        self._insertpos = 0
        self._inserttext = ""
        # Create the logger.
        configure_logger(verbosity, quiet)
        self.history = []  # History of commited operations, useful to undo.

    @property
    def dirsonly(self):
        return self._dirsonly

    @dirsonly.setter
    def dirsonly(self, boolean):
        log.debug("Dirsonly: {}".format(boolean))
        self._dirsonly = boolean
        if self.dirsonly:
            self.filesonly = False

    @property
    def filesonly(self):
        return self._filesonly

    @filesonly.setter
    def filesonly(self, boolean):
        log.debug("Filesonly: {}".format(boolean))
        self._filesonly = boolean
        if self.filesonly:
            self.dirsonly = False

    @property
    def recursive(self):
        return self._recursive

    @recursive.setter
    def recursive(self, boolean):
        log.debug("Setting recursive to {}.".format(boolean))
        self._recursive = boolean

    @property
    def hidden(self):
        return self._hidden

    @hidden.setter
    def hidden(self, boolean):
        log.debug("Setting hidden to {}.".format(boolean))
        self._hidden = boolean

    @property
    def simulate(self):
        return self._simulate

    @simulate.setter
    def simulate(self, boolean):
        log.debug("Setting simulate to {}.".format(boolean))
        self._simulate = boolean

    @property
    def interactive(self):
        return self._interactive

    @interactive.setter
    def interactive(self, boolean):
        log.debug("Setting interactive to {}.".format(boolean))
        self._interactive = boolean

    @property
    def prompt(self):
        return self._prompt

    @prompt.setter
    def prompt(self, boolean):
        log.debug("Setting simulate to {}.".format(boolean))
        self._prompt = boolean

    @property
    def noclobber(self):
        return self._noclobber

    @noclobber.setter
    def noclobber(self, boolean):
        log.debug("Setting noclobber to {}.".format(boolean))
        self._noclobber = boolean

    @property
    def keepext(self):
        return self._keepext

    @keepext.setter
    def keepext(self, boolean):
        log.debug("Setting keepext to {}.".format(boolean))
        self._keepext = boolean

    @property
    def regex(self):
        return self._regex

    @regex.setter
    def regex(self, boolean):
        log.debug("Setting regex to {}.".format(boolean))
        self._regex = boolean

    @property
    def accents(self):
        return self._accents

    @accents.setter
    def accents(self, boolean):
        log.debug("Setting accents to {}.".format(boolean))
        self._accents = boolean

    @property
    def exclude(self):
        return self._exclude

    @exclude.setter
    def exclude(self, names):
        log.debug("Excluding {}.".format(names))
        self._exclude = names

    @property
    def autostop(self):
        return self._autostop

    @autostop.setter
    def autostop(self, boolean):
        log.debug("Setting autostop to {}.".format(boolean))
        self._autostop = boolean

    @property
    def mirror(self):
        return self._mirror

    @mirror.setter
    def mirror(self, boolean):
        log.debug("Setting mirror to {}.".format(boolean))
        self._mirror = boolean

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, index):
        log.debug("Setting count index to {}.".format(index))
        self._count = index

    @property
    def insertpos(self):
        return self._insertpos

    @count.setter
    def count(self, index):
        log.debug("Setting insertpos to {}.".format(index))
        self._insertpos = index

    @property
    def inserttext(self):
        return self._inserttext

    @inserttext.setter
    def inserttext(self, text):
        log.debug("Setting inserttext to {}.".format(text))
        self._inserttext = text

    def stage(self, srcpat, destpat, path=None):
        """Initialize the rename operation. Returns list of targets and their
        preview."""
        if not path:
            path = os.getcwd()
        print path

        targets = self.find_targets(srcpat, path)
        print targets
        modtargets = self.modify_targets(targets, srcpat, destpat)
#         matches = self.match_targets(targets, expression)
#         print matches
        # [i for i, j in zip(a, b) if i != j]

    def splitext(self, files, root, srcpat):
        """Splits a list of files into filename and extension."""
        target = []
        for f in files:
            fname, ext = os.path.splitext(f)
            if self.match(srcpat, fname, ext):
                target.append([root, fname, ext])
        return target

    def joinext(self, target):
        """Joins a target tuple of (name, extension) back together."""
        if len(target) > 2:
            target = (target[1], target[2])
        name = target[0]
        if not self.keepext:
            try:
                name += target[1]
            except IndexError:
                pass
        return name

    def match(self, srcpat, *target):
        """Searches target for pattern and returns True/False respectively."""
        name = self.joinext(target)
        if self.regex:
            if re.search(srcpat, name):
                return True
        else:
            if fnmatch.fnmatch(name, srcpat):
                return True

        return False

    def find_targets(self, srcpat, path):
        """Creates a list of files and/or directories to work with."""
        targets = []
        for root, dirs, files in os.walk(path):
            root += "/"
            if self.dirsonly:
                target = [[root, d] for d in dirs if self.match(srcpat, d)]
            elif self.filesonly:
                self.splitext(files, root, srcpat)
            else:
                target = [[root, d] for d in dirs if self.match(srcpat, d)]
                target += self.splitext(files, root, srcpat)

            if self.hidden:
                targets.extend(target)
            else:
                targets.extend(i for i in target if not i[1].startswith("."))

            # Do not enter the second loop for non-recursive searches.
            if not self.recursive:
                break

        return targets

    def modify_targets(self, targets, srcpat, destpat):
        # TODO: Handle case sensitivity (re.IGNORECASE)
        print srcpat, destpat
        if not self.regex:
            srcpat = fnmatch.translate(srcpat)
            destpat = fnmatch.translate(destpat)
            print srcpat, destpat
        for target in targets:
            name = self.joinext(target)
            print srcpat, destpat, name
            srcmatch = re.search(target, srcpat).group()
            destmatch = re.search(target, destpat).group()
            print srcmatch, destmatch
            # TODO: Two functions: one to convert a glob into a pattern
            # and another to convert one into a replacement.

    def commit(self, targets):
        if self.simulate:
            print "{} to {}".format(targets[1], targets[2])
        # clean up self.exclude

    def undo(self, action):
        pass

    def get_new_path(self, name, path):
        """ Remove file from path, so we have only the dir"""
        dirpath = os.path.split(path)[0]
        if dirpath != '/': dirpath += '/'
        return dirpath + name

    def replace_spaces(self, name, path, mode):
        name = unicode(name)
        path = unicode(path)

        if mode == 0:
            newname = name.replace(' ', '_')
        elif mode == 1:
            newname = name.replace('_', ' ')
        elif mode == 2:
            newname = name.replace(' ', '.')
        elif mode == 3:
            newname = name.replace('.', ' ')
        elif mode == 4:
            newname = name.replace(' ', '-')
        elif mode == 5:
            newname = name.replace('-', ' ')

        newpath = self.get_new_path(newname, path)
        return unicode(newname), unicode(newpath)

    def replace_capitalization(self, name, path, mode):
        name = unicode(name)
        path = unicode(path)

        if mode == 0:
            newname = name.upper()
        elif mode == 1:
            newname = name.lower()
        elif mode == 2:
            newname = name.capitalize()
        elif mode == 3:
            # newname = name.title()
            newname = " ".join([x.capitalize() for x in name.split()])

        newpath = self.get_new_path(newname, path)
        return unicode(newname), unicode(newpath)

    def replace_with(self, name, path, orig, new):
        """ Replace all occurences of orig with new """
        newname = name.replace(orig, new)
        newpath = self.get_new_path(newname, path)

        return unicode(newname), unicode(newpath)

    def replace_accents(self, name, path):
        name = unicode(name)
        path = unicode(path)

        newname = ''.join(c for c in unicodedata.normalize('NFD', name)
                           if unicodedata.category(c) != 'Mn')

        newpath = self.get_new_path(newname, path)
        return unicode(newname), unicode(newpath)


if __name__ == "__main__":
    fileops = FileOps(hidden=True, recursive=True, keepext=False, regex=False)
    fileops.stage("*.txt", "asdf")
