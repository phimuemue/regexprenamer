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
        self.vbox1.set_property("spacing", 2)
        # toolbar
        self.toolbar = gtk.Toolbar()
        self.vbox1.pack_start(self.toolbar, False, True, 0)
        iconw = gtk.Image()
        iconw.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON)
        self.toolbar.append_item("Add file", "Add another file to be renamed.", "Private info", iconw, self.on_add_file)
        iconw = gtk.Image()
        iconw.set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_BUTTON)
        self.toolbar.append_item("Remove file", "Remove selected file from list.", "Private info", iconw, self.on_remove_file)
        # tree-view with scroller
        self.tvscroll = gtk.ScrolledWindow()
        self.vbox1.pack_start(self.tvscroll, True, True, 0)
        self.tv = gtk.TreeView()
        self.tvscroll.add(self.tv)
        self.tv.connect("drag_data_received", self.on_drag_data_received)
        self.tv.enable_model_drag_dest([("text/uri-list",0,80)],
                                       gtk.gdk.ACTION_DEFAULT |
                                       gtk.gdk.ACTION_COPY)
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
        # statusbar
        self.statusbar = gtk.Statusbar()
        self.statusbar.set_property("has-resize-grip", False)
        self.vbox1.pack_end(self.statusbar, False, True)
        self.pb = gtk.ProgressBar()
        self.statusbar.pack_start(self.pb)
        cid = self.statusbar.get_context_id("Renamer")
        self.statusbar.push(cid, "Renamer")
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
                self.add_file(f)
        self.onpreview(self, None)

    def on_remove_file(self, widget, event=None):
        selection = self.tv.get_selection()
        model, s_iter = selection.get_selected()
        if (s_iter):
            item = self.liststore.remove(s_iter)
            print "Selection!"
        print selection

    def on_add_file(self, widget, event=None):
        chooser = gtk.FileChooserDialog(title="Add files",
                                        action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_OK,
                                                 gtk.RESPONSE_OK))
        chooser.set_select_multiple(True)
        response = chooser.run()
        if (response==gtk.RESPONSE_OK):
            files = chooser.get_filenames()
            for f in files:
                self.add_file(f)
        chooser.destroy()

    def add_file(self, f):
        self.liststore.append(
                    [os.path.basename(f).strip(),
                     "",
                     os.path.dirname(f),
                     gio.File(f).query_info("standard::icon").get_icon().get_names()[0]])        

    def onpreview(self, widget, event=None):
        for i in self.liststore:
            i[1]=re.sub(self.txtregex.get_text(),
                        self.txtreplacement.get_text(),
                        i[0])
        return False

    def onrename(self, widget, event=None):
        self.onpreview(widget, event)
        c = 0
        for i in self.liststore:
            if not os.path.exists(i[0]):
                print "Warning: %s does not exist. Skipping."%(i[0])
            else:
                print "Renaming %s to %s"%(i[0], i[1])
                os.rename(os.path.join(i[2],i[0]), os.path.join(i[2],i[1]))
            c = c + 1
            frac = float(c)/len(self.liststore)
            print "Fraction %f"%(frac)
            self.pb.set_fraction(float(c)/len(self.liststore))
        return True

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def main(self):
        gtk.main()

print __name__
if __name__ == "__main__":
    regexprenamer = RegexpRenamer()
    regexprenamer.main()
