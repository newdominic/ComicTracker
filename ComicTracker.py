import os
import requests
import webbrowser
from Tkinter import *
import threading

# To-do
# timer


class ComicTracker(Frame):
    INDEX_SN=0
    INDEX_NAME=1
    INDEX_LATEST_EP=2
    INDEX_CURR_EP=3
    INDEX_KEEP_UP=4
    INDEX_UPDATED=5

    KEEP_UP_SELECTED = 'K'
    KEEP_UP_DESELECTED = ''
    COMIC_NEW = '+'
    COMIC_OLD = ''

    def init_ui(self):
        self.DelBtn.grid(row=0, column=1)
        self.AddBtn.grid(row=0, column=0)
        self.UpBtn.grid(row=0, column=2)
        self.DownBtn.grid(row=0, column=3)

        self.ComicList.grid(row=1, column=0, columnspan=4, rowspan=6)
        self.ComicList.bind('<<ListboxSelect>>', self.select_item)
        self.ComicList.bind('<Double-1>', self.double_click_list)

        self.SNCaptionLabel.grid(row=1, column=4, sticky=NW)
        self.SNValueLabel.grid(row=1, column=5, sticky=NW)
        self.NameCaptionLabel.grid(row=2, column=4, sticky=NW)
        self.NameValueLabel.grid(row=2, column=5, sticky=NE)
        self.LatestEPCaptionLabel.grid(row=3, column=4, sticky=NW)
        self.LatestEPValueLabel.grid(row=3, column=5, sticky=NW)
        self.CurrEPCaptionLabel.grid(row=4, column=4, sticky=NW)
        self.CurrEPEntry.grid(row=4, column=5, sticky=NW)
        self.KeepUpCbx.grid(row=5, column=4, sticky=NW, columnspan=2)
        self.OpenPageBtn.grid(row=6, column=4, sticky=NW, columnspan=2)

        self.UpdateFreqLabel.grid(row=7, column=0, columnspan=3)
        self.UpdateFreqStr.set(self.update_frequency)
        self.UpdateFreqStr.trace('w', self.change_update_frequency)
        self.UpdateFreqEntry.grid(row=7, column=3)
        self.SaveBtn.grid(row=7, column=4, sticky=W)
        self.UpdateBtn.grid(row=7, column=5, sticky=W)
        self.QuitBtn.grid(row=7, column=6, sticky=W)

        self.init_listbox()

        self.update_timer.start()

    def init_listbox(self):
        for data in self.comic_db:
            self.ComicList.insert(END, data[self.INDEX_UPDATED]+data[self.INDEX_NAME].decode('big5'))

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()

        self.AddBtn = Button(self, text='Add', width=5, command=self.click_add_comic)
        self.DelBtn = Button(self, text='Delete', width=5, command=self.del_comic)
        self.UpBtn = Button(self, text='^', width=5, command=self.move_comic_up)
        self.DownBtn = Button(self, text='v', width=5, command=self.move_comic_down)

        self.ComicList = Listbox(self, width=25)

        self.SNCaptionLabel = Label(self, text='SN: ')
        self.SNValueLabel = Label(self, text='')
        self.NameCaptionLabel = Label(self, text='Name: ')
        self.NameValueLabel = Label(self, text='', width=20)
        self.LatestEPCaptionLabel = Label(self, text='Latest EP: ')
        self.LatestEPValueLabel = Label(self, text='')
        self.CurrEPCaptionLabel = Label(self, text='Current EP: ')
        self.CurrEPStr = StringVar()
        self.CurrEPEntry = Entry(self, textvariable=self.CurrEPStr, width=5)
        self.KeepUpCbx = Checkbutton(self, text='Keep up automatically', command=self.keep_up_button)
        self.OpenPageBtn = Button(self, text='Open in Browser', command=self.open_page)

        self.UpdateFreqLabel = Label(self, text='Update Frequency(hrs):')
        self.UpdateFreqStr = StringVar()
        self.UpdateFreqEntry = Entry(self, textvariable=self.UpdateFreqStr, width=3)
        self.SaveBtn = Button(self, text='Save', width=10, command=self.save_database)
        self.UpdateBtn = Button(self, text='Update', width=10, command=self.update_comic_btn)
        self.QuitBtn = Button(self, text='Quit', width=10, command=self.save_and_quit)

        self.AddComicTPL = None
        self.AddComicStr = StringVar()
        self.AddComicEntry = None
        self.AddComicOKBtn = None

        self.url = 'http://www.comicbus.com/html/%s.html'
        self.update_frequency = 3
        self.comic_db = []
        self.current_index = -1

        self.update_thread = None
        self.update_timer = threading.Timer(self.update_frequency * 3600, self.update_comic_timer)

    def update_comic_timer(self):
        self.update_timer = threading.Timer(self.update_frequency * 3600, self.update_comic_timer)
        self.update_timer.start()
        self.update_comic_btn()

    def update_comic(self):
        for i in range(len(self.comic_db)):
            data = self.comic_db[i]
            try:
                r = requests.get(self.url % data[self.INDEX_SN])
                r.encoding = 'big5'
                comic_episode = r.text.split('#Comic')[1].split('</b>')[0].split('<b>')[1].split('-')[1].encode('ascii')
                if int(comic_episode) > int(data[self.INDEX_LATEST_EP]):
                    data[self.INDEX_LATEST_EP] = comic_episode
                    if data[self.INDEX_KEEP_UP] == self.KEEP_UP_SELECTED:
                        data[self.INDEX_CURR_EP] = comic_episode
                    data[self.INDEX_UPDATED] = self.COMIC_NEW
                    self.ComicList.delete(i)
                    self.ComicList.insert(i, '+' + data[self.INDEX_NAME].decode('big5'))
            except Exception as e:
                pass

        self.save_database()

        self.update_thread = None

    def update_comic_btn(self):
        if self.update_thread is None:
            self.update_thread = threading.Thread(target=self.update_comic)
            self.update_thread.start()

    def select_item(self, _):
        self.current_index = self.ComicList.curselection()[0]

        data = self.comic_db[self.current_index]
        self.SNValueLabel['text'] = data[self.INDEX_SN]
        self.NameValueLabel['text'] = data[self.INDEX_NAME].decode('big5')
        self.LatestEPValueLabel['text'] = data[self.INDEX_LATEST_EP]
        self.CurrEPStr.set(data[self.INDEX_CURR_EP])
        if data[self.INDEX_KEEP_UP] == '':
            self.KeepUpCbx.deselect()
        else:
            self.KeepUpCbx.select()

        if data[self.INDEX_UPDATED] == self.COMIC_NEW:
            data[self.INDEX_UPDATED] = self.COMIC_OLD

            self.ComicList.delete(self.current_index)
            self.ComicList.insert(self.current_index, data[self.INDEX_NAME].decode('big5'))
            self.ComicList.select_set(self.current_index)

    def double_click_list(self, *args):
        self.select_item(*args)
        self.open_page()

    def click_add_comic(self):
        # Add Comic
        if self.AddComicTPL is None:
            self.AddComicTPL = Toplevel(self)
            self.AddComicTPL.title('Input Comic SN')
            self.AddComicEntry = Entry(self.AddComicTPL, textvariable=self.AddComicStr, width=5)
            self.AddComicEntry.pack()
            self.AddComicOKBtn = Button(self.AddComicTPL, text='OK', command=lambda: self.add_comic(self.AddComicStr.get()))
            self.AddComicOKBtn.pack()

    def add_comic(self, serial_number):
        try:
            # check duplication
            for data in self.comic_db:
                if data[self.INDEX_SN] == serial_number:
                    raise Exception('')

            r = requests.get(self.url % serial_number)
            r.encoding = 'big5'
            comic_name = r.text.split('"description" ')[1].split('"')[1].split(' ')[0].encode('big5')
            comic_episode = r.text.split('#Comic')[1].split('</b>')[0].split('<b>')[1].split('-')[1].encode('ascii')
            comic_data = [serial_number, comic_name, comic_episode, comic_episode, self.KEEP_UP_SELECTED, self.COMIC_NEW]
            if self.current_index == -1:
                self.comic_db.append(comic_data)
            else:
                self.comic_db.insert(self.current_index, comic_data)

            self.ComicList.insert(END, '+' + comic_name.decode('big5'))
        except:
            pass

        self.AddComicTPL.destroy()
        self.AddComicTPL = None
        self.AddComicEntry = None
        self.AddComicOKBtn = None

    def del_comic(self):
        if len(self.ComicList.curselection()) == 0:
            return

        del self.comic_db[self.ComicList.curselection()[0]]

        self.ComicList.delete(self.ComicList.curselection()[0])

        self.current_index = -1

    def move_comic_up(self):
        if self.current_index <= 0:
            return

        self.comic_db[self.current_index - 1], self.comic_db[self.current_index] = self.comic_db[self.current_index], \
                                                                                   self.comic_db[self.current_index - 1]

        text = self.ComicList.get(self.current_index)
        self.ComicList.delete(self.current_index)
        self.ComicList.insert(self.current_index - 1, text)
        self.ComicList.select_set(self.current_index - 1)

    def move_comic_down(self):
        if self.current_index >= len(self.comic_db) - 1:
            return

        self.comic_db[self.current_index + 1], self.comic_db[self.current_index] = self.comic_db[self.current_index], \
                                                                                   self.comic_db[self.current_index + 1]

        text = self.ComicList.get(self.current_index)
        self.ComicList.delete(self.current_index)
        self.ComicList.insert(self.current_index + 1, text)
        self.ComicList.select_set(self.current_index + 1)

    def change_update_frequency(self, _):
        self.update_frequency = self.UpdateFreqStr.get()

    def open_page(self):
        if self.current_index == -1:
            return

        webbrowser.open(self.url % self.comic_db[self.current_index][0])

    def load_database(self):
        if not os.path.exists('comic.db'):
            return

        with open('comic.db', 'r') as f:
            self.update_frequency = int(f.readline())
            while True:
                line = f.readline()[:-1]
                if line == '':
                    break
                data = line.split(',')
                self.comic_db.append(data)

    def save_database(self):
        with open('comic.db', 'w') as f:
            f.write(str(self.update_frequency) + '\n')
            for data in self.comic_db:
                f.write(','.join(data) + '\n')

    def keep_up_button(self):
        if self.current_index == -1:
            return

        if bool(self.comic_db[self.current_index][-2]):
            self.comic_db[self.current_index][-2] = self.KEEP_UP_DESELECTED
        else:
            self.comic_db[self.current_index][-2] = self.KEEP_UP_SELECTED

    def save_and_quit(self):
        self.update_timer.cancel()
        self.save_database()
        self.quit()

root = Tk()
root.title('Comic Tracker')
CT = ComicTracker(root)

CT.load_database()
CT.init_ui()

CT.mainloop()
