#!/usr/bin/env python

import pygtk
pygtk.require("2.0")
import gtk

import gio

import os
import re

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
        # tree-view with scroller
        self.tvscroll = gtk.ScrolledWindow()
        self.vbox1.pack_start(self.tvscroll, True, True, 0)
        self.tv = gtk.TreeView()
        self.tvscroll.add(self.tv)
        self.tv.connect("drag_data_received", self.on_drag_data_received)
        self.tv.enable_model_drag_dest([("text/uri-list",0,80)],
                                       gtk.gdk.ACTION_DEFAULT |
                                       gtk.gdk.ACTION_COPY)
        # self.tv.drag_dest_set(gtk.DEST_DEFAULT_MOTION |
        #                       gtk.DEST_DEFAULT_HIGHLIGHT |
        #                       gtk.DEST_DEFAULT_DROP,
        #                       [("text/uri-list",0,0)], gtk.gdk.ACTION_COPY)
        # bottom "navigation"
        self.inputgrid = gtk.HBox(False)
        self.vbox1.pack_start(self.inputgrid, False, False)
        self.labelbox = gtk.VBox(2)
        self.labelbox.set_border_width(5)
        self.txtbox = gtk.VBox(2)
        self.txtbox.set_border_width(5)
        self.inputgrid.pack_start(self.labelbox, False, False)
        self.inputgrid.pack_start(self.txtbox, True, True)
        # labels 
        self.lblregexp = gtk.Label("Regexp:")
        self.labelbox.pack_start(self.lblregexp, False, False)
        self.lblregexp.set_alignment(0,0.5)
        self.lblreplacement = gtk.Label("Replacement:")
        self.labelbox.pack_start(self.lblreplacement, False, False)
        self.lblreplacement.set_alignment(0,0.5)
        # input fields
        self.txtregex = gtk.Entry()
        self.txtbox.pack_start(self.txtregex, True, True)
        self.txtregex.set_text("(.*)")
        self.txtregex.connect("focus-out-event", self.onpreview)
        self.txtreplacement = gtk.Entry()
        self.txtbox.pack_start(self.txtreplacement, True, True)
        self.txtreplacement.set_text("\\1")
        self.txtreplacement.connect("focus-out-event", self.onpreview)
        # button
        self.btnRename = gtk.Button("Rename")
        self.vbox1.pack_start(self.btnRename, False, False)
        self.btnRename.connect("pressed",self.onrename)
        # the liststore
        self.liststore = gtk.ListStore(str, str, str, str)
        self.tv.set_model(self.liststore)
        cellpb = gtk.CellRendererPixbuf()
        colorigname = gtk.TreeViewColumn("Original name", text=0)
        cellt = gtk.CellRendererText()
        self.tv.append_column(colorigname)
        colorigname.pack_start(cellpb, False)
        colorigname.pack_start(cellt)
        colorigname.set_attributes(cellt, text=0)
        colorigname.set_attributes(cellpb, icon_name=3)
        self.tv.append_column(
            gtk.TreeViewColumn("New name", gtk.CellRendererText(), text=1))
        self.tv.append_column(
            gtk.TreeViewColumn("Directory", gtk.CellRendererText(), text=2))
        # show window with all its widgets
        self.window.resize(400,300)
        self.window.show_all()

    def on_drag_data_received(self, 
                              widget,
                              context,
                              x,
                              y,
                              selection,
                              target_type,
                              timestamp):
        if target_type == 80:
            uri = selection.data.strip('\r\n\x00')
            files = uri.split("\n")
            files = [f.strip() for f in files]
            files = [f[7:] if f.startswith("file://") else f for f in files]
            print files
            for f in files:
                print "file: " + f
                self.liststore.append(
                    [os.path.basename(f).strip(),
                     "",
                     os.path.dirname(f),
                     gio.File(f).query_info("standard::icon").get_icon().get_names()[0]])
        self.onpreview(self, None)

    def onpreview(self, widget, event=None):
        for i in self.liststore:
            i[1]=re.sub(self.txtregex.get_text(),
                        self.txtreplacement.get_text(),
                        i[0])
        return False

    def onrename(self, widget, event=None):
        self.onpreview(widget, event)
        for i in self.liststore:
            print "Renaming %s to %s"%(i[0], i[1])
            os.rename(os.path.join(i[2],i[0]), os.path.join(i[2],i[1]))
        return True

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def main(self):
        gtk.main()

print __name__
if __name__ == "__main__":
    regexprenamer = RegexpRenamer()
    regexprenamer.main()
