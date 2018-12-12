#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import os.path
from pprint import pformat
import tempfile
import wx
from wxbreads.base import BaseWindow, run_app
import wxbreads.widgets as wxw
import windbreads.utils as wdu

__version__ = "0.1.0"
__author__ = "Lix Xu"
__remark__ = "Python Pickle file viewer"
CONFIG_FILE = os.path.join(tempfile.gettempdir(), "wxpickleviewer.pkl")


class MainWindow(BaseWindow):
    app_title = __remark__
    app_remark = __remark__
    app_version = __version__
    app_website = "https://github.com/lixxu/wxpickleviewer"
    quit_confirm = False
    remember_window = True
    sbar_width = [-1, 100, 130]
    quit_menu_id = wx.NewIdRef()
    about_menu_id = wx.NewIdRef()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        wdu.get_copy_right = self.get_copyright
        self.config = self.load_config()

        self.set_min_size((400, 300))
        self.setup_statusbar()
        self.setup_timers()
        self.setup_ui()
        self.show()

    def get_copyright(self):
        return "(C) 爱已随风去"

    def setup_ui(self):
        p = wx.Panel(self)
        font = self.GetFont()
        font.SetPointSize(11)
        p.SetFont(font)
        sizer = wx.BoxSizer(wx.VERTICAL)
        lbl, fp, tc, btn = wxw.quick_open_file(
            p,
            sizer,
            ssize=(300, -1),
            label="Pickle File Path",
            value=self.config["pk_file"],
        )
        self.pk_fp = fp
        self.start_btn = wxw.add_start_button(self, p)
        self.rtc = wxw.add_richtext(p, readonly=True, size=(550, 150))

        wxw.pack(self.start_btn, sizer)
        wxw.pack(self.rtc, sizer, prop=1, flag="e,a")

        self.setup_menubar()

        p.SetSizer(sizer)
        sizer.Fit(self)
        p.Layout()

    def setup_menubar(self):
        mb = wx.MenuBar()
        fmenu = wx.Menu()
        fmenu.Append(self.quit_menu_id, "&Exit", "Exit this application")
        mb.Append(fmenu, "&File")

        hmenu = wx.Menu()
        hmenu.Append(self.about_menu_id, "&About", "About this application")
        mb.Append(hmenu, "&Help")
        self.SetMenuBar(mb)

        self.Bind(wx.EVT_MENU, self.on_quit, id=self.quit_menu_id)
        self.Bind(wx.EVT_MENU, self.on_about, id=self.about_menu_id)

    def on_start(self, evt):
        self.rtc.Clear()
        self.is_running = True
        self.start_ts = datetime.now()
        self.start_btn.Enable(False)
        self.start_btn.SetLabel("Loading...")
        self.start_delay_work(self.after_task, self.do_task)

    def after_task(self, delay_result):
        try:
            delay_result.get()
        except Exception as e:
            self.add_echo(e, fg="red", ts=False)

        self.is_running = False
        self.start_btn.Enable(True)
        self.start_btn.SetLabel("Start")

    def do_task(self):
        pk_file = self.pk_fp.GetPath().strip()
        if not (pk_file and os.path.exists(pk_file)):
            return

        self.config["pk_file"] = pk_file
        data = wdu.load_pickle(pk_file, silent=False)
        self.add_echo(pformat(data, indent=4), ts=False)

    def other_clock_work(self):
        self.update_run_ts()

    def load_config(self):
        config = dict(pk_file="")
        config.update(wdu.load_pickle(CONFIG_FILE))
        return config

    def dump_config(self):
        wdu.dump_pickle(self.config, CONFIG_FILE)


if __name__ == '__main__':
    run_app(MainWindow)
