#!/usr/bin/env python

import pygtk
pygtk.require("2.0")
import gtk

class RegexpRenamer:
    def __init__(self):
        # the window itself
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)
        self.window.set_title("RegexpRenamer")
        # general layout
        self.vbox1 = gtk.VBox(False)
        self.window.add(self.vbox1)
        # tree-view
        self.tv = gtk.TreeView()
        self.vbox1.pack_start(self.tv, True, True, 0)
        self.tv.connect("drag_data_received", self.on_drag_data_received)
        self.tv.enable_model_drag_dest([("text/uri-list",0,80)],
                                       gtk.gdk.ACTION_DEFAULT |
                                       gtk.gdk.ACTION_COPY)
        # self.tv.drag_dest_set(gtk.DEST_DEFAULT_MOTION |
        #                       gtk.DEST_DEFAULT_HIGHLIGHT |
        #                       gtk.DEST_DEFAULT_DROP,
        #                       [("text/uri-list",0,0)], gtk.gdk.ACTION_COPY)
        # bottom "navigation"
        self.inputgrid = gtk.HBox(2)
        self.vbox1.pack_start(self.inputgrid, False, False)
        self.labelbox = gtk.VBox(2)
        self.txtbox = gtk.VBox(2)
        self.inputgrid.pack_start(self.labelbox, False, False)
        self.inputgrid.pack_start(self.txtbox, False, False)
        # labels 
        self.lblregexp = gtk.Label("Regexp")
        self.labelbox.pack_start(self.lblregexp, False, False)
        self.lblreplacement = gtk.Label("Replacement")
        self.labelbox.pack_start(self.lblreplacement, False, False)
        # input fields
        self.txtregex = gtk.Entry()
        self.txtbox.pack_start(self.txtregex, True, True)
        self.txtreplacement = gtk.Entry()
        self.txtbox.pack_start(self.txtreplacement, True, True)
        # button
        self.btnRename = gtk.Button("Rename")
        self.vbox1.pack_start(self.btnRename, False, False)
        # the liststore
        self.liststore = gtk.ListStore(str, str)
        self.tv.set_model(self.liststore)
        self.tv.append_column(
            gtk.TreeViewColumn("Original name", gtk.CellRendererText()))
        self.tv.append_column(
            gtk.TreeViewColumn("New name", gtk.CellRendererText()))
        # show window with all its widgets
        self.window.resize(320,240)
        self.window.show_all()

    def on_drag_data_received(self, 
                              widget,
                              context,
                              x,
                              y,
                              selection,
                              target_type,
                              timestamp):
        print target_type
        print selection.data
        if target_type == 80:
            uri = selection.data.strip('\r\n\x00')
            print uri

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def main(self):
        gtk.main()

print __name__
if __name__ == "__main__":
    regexprenamer = RegexpRenamer()
    regexprenamer.main()
