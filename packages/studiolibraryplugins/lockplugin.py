#!/usr/bin/python
"""
"""
import re
import studiolibrary


class Plugin(studiolibrary.Plugin):

    def __init__(self, *args):
        """
        @type args: 
        """
        studiolibrary.Plugin.__init__(self, *args)
        self.setName("lock")  # Must set a name for the plugin
        self.setIcon(self.dirname() + "/images/lock.png")

        # Check what kwargs were used in the studiolibrary.main() function
        self._superusers = self.window().kwargs().get("superusers", [])
        self._lockFolder = re.compile(self.window().kwargs().get("lockFolder", ""))
        self._unlockFolder = re.compile(self.window().kwargs().get("unlockFolder", ""))

    # Override the load method so that it doesn't show in the "+" new menu
    def load(self):
        """
        """
        self.updateLock()

    def folderSelectionChanged(self, itemSelection1, itemSelection2):
        """
        @type itemSelection1: 
        @type itemSelection2: 
        """
        self.updateLock()

    # Unlock for all superusers
    def updateLock(self):    
        """
        @rtype: None
        """
        if studiolibrary.user() in self._superusers or []:
            self.window().setLocked(False)
            return

        if self._lockFolder.match("") and self._unlockFolder.match(""):
            if self._superusers:  # Lock if only the superusers arg is used
                self.window().setLocked(True)
            else:  # Unlock if no keyword arguments are used
                self.window().setLocked(False)
            return

        folders = self.window().selectedFolders()

        # Lock the selected folders that match the self._lockFolder regx
        if not self._lockFolder.match(""):
            for folder in folders or []:
                if self._lockFolder.search(folder.dirname()):
                    self.window().setLocked(True)
                    return
            self.window().setLocked(False)

        # Unlock the selected folders that match the self._unlockFolder regx
        if not self._unlockFolder.match(""):
            for folder in folders or []:
                if self._unlockFolder.search(folder.dirname()):
                    self.window().setLocked(False)
                    return
            self.window().setLocked(True)


if __name__ == "__main__":

    import studiolibrary
    #root = "P:/figaro/studiolibrary/anim"
    #name = "Figaro Pho - Anim"
    superusers = ["kurt.rathjen"]
    plugins = ["examplePlugin"]

    # Lock all folders unless you're a superuser.
    studiolibrary.main(superusers=superusers, plugins=plugins, add=True)

    # This command will lock only folders that contain the word "Approved" in their path.
    #studiolibrary.main(name=name, root=root, superusers=superusers, lockFolder="Approved")

    # This command will lock all folders except folders that contain the words "Users" or "Shared" in their path.
    #studiolibrary.main(name=name, root=root, superusers=superusers, unlockFolder="Users|Shared")
