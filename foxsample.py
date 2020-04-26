#coding: utf8
#!/usr/bin/env python3

from PyQt5  import QtWidgets, QtCore, QtGui
from PyQt5.QtMultimedia import QSoundEffect, QMediaPlayer

from layout import Ui_MainWindow
#from pydub import AudioSegment
#from pydub.playback import play
#import simpleaudio as sa
import wave
import sys
import os
import shutil
import pickle
import platform
import argparse
from subprocess import call, Popen 
from itertools import cycle
from pathlib import Path

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.play_obj = None
        self.sound = None
        self.dict_file = {}
        self.dict_description = {}
        self.file_path = ""
        self.library_file_path = ""

        self.alpha = "abcdefghijklmnopqrstuvwxyz"
        self.nonalpha = {"&" : "ampersand",
            "*" : "asterix",
            "@" : "at",
            "^" : "caret",
            ":" : "colon",
            "$" : "dollar",
            "=" : "equals",
            "!" : "exclamation",
            "/" : "forwardslash",
            "#" : "hash",
            "-" : "hyphen",
            "%" : "percent",
            "+" : "plus",
            "?" : "question",
            "~" : "tilde",
            "\\" :"backslash",
            "1" : "1",
            "2" : "2",
            "3" : "3",
            "4" : "4" }

        ### load the saved directories
        with open("file_path.cs", "rb") as file:
	        self.dict_file = pickle.load(file)

        parser = argparse.ArgumentParser(
            prog="FoxDot Sample Manager", 
            description="A samples manager for FoxDot", 
            epilog="More information: https://foxdot.org/")

        parser.add_argument('-d', '--dir', action='store', help="use a foxdot directory at startup")
        parser.add_argument('-s', '--source', action='store', help="use a source directory at startup")
        args = parser.parse_args()

        if args.dir:
            self.folder_path = args.dir
        else:    
            self.folder_path = self.dict_file["destination"]
        
        if args.source:
            self.library_path = args.source
        else:
            self.library_path = self.dict_file["source"]
        
        if os.path.isdir(self.folder_path):
            ### Test if it's a foxdot snd dir
            if os.path.isdir(os.path.join(self.folder_path,"a","lower")):
                pass
            else:
                self.browse_sample_path()
        else:
            self.browse_sample_path()

        self.init_path = self.folder_path    
        if os.path.isfile(os.path.join(self.folder_path, "description.cs")):
            with open(os.path.join(self.folder_path, "description.cs"), "rb") as file:
                self.dict_description = pickle.load(file)  
        else:
            self.create_dict()

        ### Browse Folders
        self.ui.sample_path_label.setText(self.folder_path)
        self.ui.library_path_label.setText(self.library_path)
        self.ui.browse_sample_path_button.clicked.connect(self.browse_sample_path)
        self.ui.browse_library_path_button.clicked.connect(self.browse_library_path)

        ### The Folder Sample TreeView
        self.dirModel = QtWidgets.QFileSystemModel()
        self.dirModel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Dirs)
        self.dirModelLibrary = QtWidgets.QFileSystemModel()
        self.dirModelLibrary.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        
        self.ui.tree_sample_dir.setModel(self.dirModel)
        for i in range(1,4):
            self.ui.tree_sample_dir.hideColumn(i)
        
        self.ui.tree_library_dir.setModel(self.dirModelLibrary)
        for i in range(1,4):
            self.ui.tree_library_dir.hideColumn(i)
            
        ### The file sample View
        self.file_filters = ["*.wav", "*.aif", "*.ogg", "*.mp3"]
        self.fileModel = QtWidgets.QFileSystemModel()
        self.fileModel.setNameFilters(self.file_filters)
        self.fileModel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Files)
        self.libraryModel = QtWidgets.QFileSystemModel()
        self.libraryModel.setNameFilters(self.file_filters)
        self.libraryModel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Files)
        self.ui.listView_sample.setModel(self.fileModel)
        self.ui.listView_library.setModel(self.libraryModel)
        
        self.load_folder_structure()
        self.load_library_structure()

        self.ui.tree_sample_dir.clicked.connect(self.on_clicked_folder)
        self.ui.listView_sample.clicked.connect(self.on_clicked_file)
        self.ui.tree_library_dir.clicked.connect(self.on_clicked_folder_library)
        self.ui.listView_library.clicked.connect(self.on_clicked_file_library)
        
        ### UP/DOWN move sample order
        self.ui.Up_Button.clicked.connect(self.move_down)
        self.ui.Down_Button.clicked.connect(self.move_up)

        self.ui.swap_Button.clicked.connect(self.swap)

        ### Buttons destination click
        #self.ui.move_to_bank_button.clicked.connect(self.move_to_bank)
        self.ui.reindex_button.clicked.connect(self.reindex)
        self.ui.rename_button.clicked.connect(self.rename_file)
        self.ui.delete_button.clicked.connect(self.delete_file)
        self.ui.convert_button.clicked.connect(self.convert_to_wav)
        #self.ui.rename_all_button.clicked.connect(self.rename_all)
        #self.ui.unrename_button.clicked.connect(self.uname_all)
        
        self.ui.sample_description.returnPressed.connect(self.update_dict_description)
        self.ui.checkBox_sample_window.toggled.connect(self.show_sample_window)

        ### Source buttons
        self.ui.loop_checkbox.stateChanged.connect(self.play_audio)
        self.ui.copy_button.clicked.connect(self.copy_file)
        self.ui.moveto_button.clicked.connect(self.move_to)
        self.ui.openfoxdot_button.clicked.connect(self.open_foxdot)
        self.ui.open_dir_button.clicked.connect(self.open_dir_foxdot)
        self.ui.open_source_dir_pushButton.clicked.connect(self.open_dir_src)
        self.ui.swap_dir_name_Button.clicked.connect(self.swap_dir_name)

        self.ui.exit_button.clicked.connect(self.closeEvent)
        #self.ui.copy_to_bank_no_button.clicked.connect(self.copy_to_bank)

        # Samples button
        self.list_button_sample = [self.ui.sampleButton1, self.ui.sampleButton2, self.ui.sampleButton3, self.ui.sampleButton4,
        self.ui.sampleButton5,self.ui.sampleButton6,self.ui.sampleButton7,self.ui.sampleButton8, self.ui.sampleButton9,self.ui.sampleButton10]
        for sampleButton in self.list_button_sample:
            sampleButton.clicked.connect(self.listen_sample_bank)
     
        #assign button
        self.update_combo_button()
        self.ui.assign_button.clicked.connect(self.assign_combo_button)
        
        ### create sample  windows
        self.sample_window = Sample_Window(len(self.dict_description))
        self.create_sample_window()
        self.sample_window.tableWidget.cellChanged.connect(self.update_dict_from_table)      
        self.show_sample_window()

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, "Quit application", "Are you sure you wan't to quit ?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
        if reply == QtWidgets.QMessageBox.Yes:
            #self.store_sample_path()
            self.sample_window.close()
            self.close()
            event.accept()
        else:
            event.ignore()


    def browse_sample_path(self):
        ## Select the Foxdot sample directory
        self.folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Open FoxDot Sample Folder (./FoxDot/snd/ by default) ", self.folder_path, QtWidgets.QFileDialog.ShowDirsOnly)
        self.init_path = self.folder_path
        self.store_sample_path()
        self.ui.sample_path_label.setText(self.folder_path)
        self.ui.sample_path_label.adjustSize()

    def browse_library_path(self):
        ## Select the custom sample directory
        self.library_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Library Folder", self.library_path, QtWidgets.QFileDialog.ShowDirsOnly)
        self.store_sample_path()
        self.ui.library_path_label.setText(self.library_path)
        self.ui.library_path_label.adjustSize()
        self.load_library_structure()    

    def store_sample_path(self):
        # Store the selected sample path for next session
        self.dict_file = {"destination": self.init_path, "source": self.library_path}
        with open("file_path.cs", "wb") as file:
	        pickle.dump(self.dict_file, file)    
    

    def load_folder_structure(self):
        ## Folder Foxdot structure TreeView
        self.dirModel.setRootPath(self.folder_path)
        self.ui.tree_sample_dir.setRootIndex(self.dirModel.index(self.folder_path))
        self.ui.listView_sample.setRootIndex(self.fileModel.index(self.folder_path))

    def load_library_structure(self):
        ## Folder Library structure TreeView
        self.dirModelLibrary.setRootPath(self.library_path)
        self.ui.tree_library_dir.setRootIndex(self.dirModelLibrary.index(self.library_path))
        self.ui.listView_library.setRootIndex(self.libraryModel.index(self.library_path))

    def on_clicked_folder(self, index):
        self.folder_path = self.dirModel.fileInfo(index).absoluteFilePath()
        self.ui.listView_sample.setRootIndex(self.fileModel.setRootPath(self.folder_path))
        if self.find_path_symbol() in self.dict_description:
            self.ui.sample_description.setText(self.dict_description[self.find_path_symbol()])
        else:
            self.ui.sample_description.clear()    

    def on_clicked_file(self, index):
        self.rename_all()
        self.file_path = self.fileModel.fileInfo(index).absoluteFilePath()
        self.file_name = str(self.fileModel.fileInfo(index).fileName())
        self.list_files = self.get_sorted_files()
        self.index_file = self.list_files.index(self.file_name)
        self.ui.position_label.display(str(self.index_file))
        self.sample_info(self.file_path)
        self.play_audio(self.file_path)
        

    def on_clicked_folder_library(self, index):
        self.library_path = self.dirModelLibrary.fileInfo(index).absoluteFilePath()
        self.ui.listView_library.setRootIndex(self.libraryModel.setRootPath(self.library_path))

    def on_clicked_file_library(self, index):
        self.library_file_path = self.libraryModel.fileInfo(index).absoluteFilePath()
        self.library_file_name = str(self.fileModel.fileInfo(index).fileName())
        self.sample_info(self.library_file_path)
        self.play_audio(self.library_file_path)
            

    def sample_info(self, path):
        ''' Show samples informations '''
        with wave.open(path, "rb") as file:      
            self.ui.label_channel.setText("Audio channel : " + str(file.getnchannels())) 
            self.ui.label_bytepersample.setText("Sample width : " + str(file.getsampwidth())) 
            self.ui.label_samplerate.setText("Frame rate : " + str(file.getframerate())) 
            self.ui.label_duration.setText("Duration : " + str(round(file.getnframes()/float(file.getframerate()), 5)))

    def play_audio(self, filepath):
        try:
            if self.sound.isPlaying():
                self.sound.setLoopCount(0)
                self.sound.stop()
                self.sound = None
        except:
            pass        
        if os.path.isfile(filepath):
            try:
                self.sound = QSoundEffect(self)
                self.sound.setSource(QtCore.QUrl.fromLocalFile(filepath))
                self.sound.setVolume(self.ui.volume_slider.value()/100)
                if self.ui.loop_checkbox.isChecked():
                    self.sound.setLoopCount(QSoundEffect.Infinite)               
                self.sound.play()
            except:
                self.sound = QMediaPlayer(self)
                self.sound.setSource(QtCore.QUrl.fromLocalFile(filepath))
                self.sound.setVolume(self.ui.volume_slider.value()/100)
                self.sound.play()

    def create_sample_window(self):
        self.count_dict = {}
        keys_available = [x for x in self.dict_description.keys()]
        x = 0
        for char in self.alpha:
            self.sample_window.tableWidget.setVerticalHeaderItem(x, QtWidgets.QTableWidgetItem(char.lower()))
            # Nbr of sample lower
            path = os.path.join(self.init_path, char.lower(), "lower")
            nbr = self.count_nbr_sample(path)
            self.sample_window.tableWidget.setItem(x, 1, QtWidgets.QTableWidgetItem(str(nbr)))
            self.sample_window.tableWidget.item(x, 1).setBackground(QtGui.QColor(self.clamp((10+int(nbr)*20),0,255),0,25))

            if char.lower() in keys_available:
                self.sample_window.tableWidget.setItem(x,0, QtWidgets.QTableWidgetItem(self.dict_description[char.lower()]))
            else:
                self.sample_window.tableWidget.setItem(x,0, QtWidgets.QTableWidgetItem("-"))
            x += 1
            
            self.sample_window.tableWidget.setVerticalHeaderItem(x, QtWidgets.QTableWidgetItem(char.upper()))
            
            # Nbr of sample upper
            path = os.path.join(self.init_path, char.lower(), "upper")
            nbr = self.count_nbr_sample(path)
            self.sample_window.tableWidget.setItem(x, 1, QtWidgets.QTableWidgetItem(str(nbr)))
            self.sample_window.tableWidget.item(x, 1).setBackground(QtGui.QColor(self.clamp((10+int(nbr)*20),0,255),0,25))
            
            if char.upper() in keys_available:
                self.sample_window.tableWidget.setItem(x,0, QtWidgets.QTableWidgetItem(self.dict_description[char.upper()]))
            else:
                self.sample_window.tableWidget.setItem(x,0, QtWidgets.QTableWidgetItem("-"))
            x += 1
        
        for char in self.nonalpha:
            self.sample_window.tableWidget.setVerticalHeaderItem(x, QtWidgets.QTableWidgetItem(char))
            # Nbr of sample nonalpha
            path = os.path.join(self.init_path, "_", self.nonalpha[char])
            nbr = self.count_nbr_sample(path)
            self.sample_window.tableWidget.setItem(x, 1, QtWidgets.QTableWidgetItem(str(nbr)))
            self.sample_window.tableWidget.item(x, 1).setBackground(QtGui.QColor(self.clamp((10+int(nbr)*20),0,255),0,25))
            
            if char in keys_available:
                self.sample_window.tableWidget.setItem(x,0, QtWidgets.QTableWidgetItem(self.dict_description[char]))
            else:
                self.sample_window.tableWidget.setItem(x,0, QtWidgets.QTableWidgetItem("-"))
            x += 1

        self.sample_window.tableWidget.move(0,0)
        self.sample_window.tableWidget.resizeColumnsToContents()
        self.sample_window.tableWidget.resizeRowsToContents()

    def clamp(self, x, minn, maxx):
        return x if x > minn and x < maxx else (minn if x < minn else maxx)

    def count_nbr_sample(self, path):
        return len(os.listdir(path))


    def show_sample_window(self):
        if self.ui.checkBox_sample_window.isChecked():
            self.sample_window.show()
        else:
            self.sample_window.hide()

    def get_sorted_files(self):
        ''' return a list of active destination files sorted '''
        sorted_files = sorted(os.listdir(self.folder_path))
        sorted_files.sort(key=str.casefold)
        return sorted_files

    def move_up(self):
        if self.index_file < len(self.list_files):
            self.list_files = self.get_sorted_files()
            self.move_file_name(way=1)

    def move_down(self):
        if self.index_file > 0:
            self.list_files = self.get_sorted_files()
            self.move_file_name(way=-1)

    def move_file_name(self, way):    
            source_old_name = self.file_name
            source_new_name = f"{(self.index_file + way):02d}" + self.file_name[2:]
            dest_old_name = self.list_files[self.index_file + way]
            dest_new_name = f"{self.list_files.index(source_old_name):02d}" + dest_old_name[2:]
        
            source_old_path = os.path.join(self.folder_path, source_old_name)
            source_new_path = os.path.join(self.folder_path, source_new_name)

            dest_old_path = os.path.join(self.folder_path, dest_old_name)
            dest_new_path = os.path.join(self.folder_path, dest_new_name)
        
            if source_old_path != source_new_path:
                os.rename(source_old_path, source_new_path)
            if dest_old_path != dest_new_path:
                os.rename(dest_old_path, dest_new_path)
            self.ui.position_label.display(str(self.index_file+way))

            self.fileModel.layoutChanged.emit()


    def swap(self):
        self.list_files = self.get_sorted_files()
        self.ui.swap_spinBox.setMaximum(len(self.list_files)-1)
        source_old_name = self.file_name
        source_new_name = f"{self.ui.swap_spinBox.value():02d}" + self.file_name[2:]
        dest_old_name = self.list_files[self.ui.swap_spinBox.value()]
        dest_new_name = f"{self.list_files.index(source_old_name):02d}" + dest_old_name[2:]
        
        source_old_path = os.path.join(self.folder_path, source_old_name)
        source_new_path = os.path.join(self.folder_path, source_new_name)

        dest_old_path = os.path.join(self.folder_path, dest_old_name)
        dest_new_path = os.path.join(self.folder_path, dest_new_name)
        
        if source_old_path != source_new_path:
            os.rename(source_old_path, source_new_path)
        if dest_old_path != dest_new_path:
            os.rename(dest_old_path, dest_new_path)

        self.fileModel.layoutChanged.emit()

    def rename_all(self):
        ''' rename all files from active destination'''
        listfile = self.get_sorted_files()
        self.rename_list_file(listfile)
        self.list_files = self.get_sorted_files()

    def rename_list_file(self, list_of_file):
        ''' Rename the file with index'''
        # start_with_number = False    
        # test if begin with number_
        # for file in list_of_file:
        #     if file[:1].isdigit() and file[1:2] == "_":
        #         start_with_number = True
        #     else:
        #         start_with_number = False    
        if not all((f[:2].isdigit() and f[2:3] == "_") for f in list_of_file):
            # add index_ to each files
            for number, file in enumerate(list_of_file):
                path_to_file = os.path.join(self.folder_path, file)
                path_to_new_file = os.path.join(self.folder_path, f"{number:02d}" + "_" + str(file))
                os.rename(path_to_file, path_to_new_file)

    def reindex(self):
        listfile = self.get_sorted_files()
        for number, file in enumerate(listfile):
                    path_to_file = os.path.join(self.folder_path, file)
                    new_name = f"{number:02d}" + file[2:]
                    path_to_new_file = os.path.join(self.folder_path, new_name)
                    os.rename(path_to_file, path_to_new_file)
        self.list_files = self.get_sorted_files()

    def uname_all(self):
        ''' remove the index_ of all active destination files '''
        listfile = self.get_sorted_files()
        self.unrename_list(listfile)

    def unrename_list(self, list_of_file):
        self.start_with_number = False
        # test if all begin with number         
        for file in list_of_file:
            if file[:2].isdigit() and file[2:3] == "_":
                self.start_with_number = True
            else:
                self.start_with_number = False    
        if self.start_with_number:
            i=1
            for file in list_of_file:
                path_to_file = os.path.join(self.folder_path, file)
                path_to_new_file = os.path.join(self.folder_path, str(file[3:]))
                if os.path.exists(path_to_new_file):
                    bef, sep, after = path_to_new_file.partition(".")
                    path_to_new_file = bef + f"{i:02b}" + sep + after
                    i += 1
                os.rename(path_to_file, path_to_new_file)        

    def copy_file(self):
        ''' copy the selected source file to active destination directory '''
        self.list_files = self.get_sorted_files()
        if os.path.isfile(self.library_file_path) and os.path.isdir(self.folder_path):
            newpath = os.path.join(self.folder_path, f"{len(self.list_files):02d}" + "_" + self.library_file_name)
            shutil.copy(self.library_file_path, newpath)
        self.list_files = self.get_sorted_files()    
        self.create_sample_window()    

    def delete_file(self):
        self.list_files = self.get_sorted_files()
        ''' delete the selected destination file '''
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)
            self.reindex()
            self.list_files = self.get_sorted_files()
            self.create_sample_window()

    def move_to(self):
        self.list_files = self.get_sorted_files()
        verif = self.count_nbr_sample(self.folder_path)
        self.copy_file()
        if self.count_nbr_sample(self.folder_path) == verif + 1:
            os.remove(self.library_file_path)
        self.list_files = self.get_sorted_files()    
        self.create_sample_window()

    def convert_to_wav(self):
        if os.path.isfile(self.file_path):
            file, sep, extension = self.file_path.partition(".")
            if extension == "wav":
                file += "_convert" 
            try:
                output = file+".wav"
                call(["ffmpeg", "-y", "-i", self.file_path, "-ar", "44100", output])
                if os.path.isfile(output):
                    self.delete_file()
            except:
                self.msg_box("FFMPEG problem !", 'Make sure you have ffmpeg installed', "ffmpeg error")


    def msg_box(self, text, info, title):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(text)
        msg.setInformativeText(info)
        msg.setWindowTitle(title)
        msg.exec_()

    def rename_file(self, index):
        new_name, ok = QtWidgets.QInputDialog.getText(self, 'Rename the file', 'Rename the file:', QtWidgets.QLineEdit.Normal, self.file_name)
        if ok:
            path_to_file = os.path.join(self.folder_path, self.file_name)
            path_to_new_file = os.path.join(self.folder_path, new_name)
            os.rename(path_to_file, path_to_new_file)    
        self.list_files = self.get_sorted_files()

    def swap_dir_name(self):
        dest_old_path = self.folder_path
        dest_new_path = str(self.folder_path + "_tmp")
        
        reply = QtWidgets.QMessageBox.question(self, "Switch Folder name", "Switch {} --> {}".format(self.library_path, self.folder_path), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
        if reply == QtWidgets.QMessageBox.Yes:
            os.rename(dest_old_path, dest_new_path)
            src_old_path = self.library_path
            os.rename(src_old_path, dest_old_path)
            os.rename(dest_new_path, src_old_path)
            self.fileModel.layoutChanged.emit()
            self.libraryModel.layoutChanged.emit()  
        else:
            pass
        
    def update_dict_description(self):
        description = self.ui.sample_description.text()
        sample = self.find_path_symbol()
        if sample is not None:
            self.dict_description[sample] = description
            with open(os.path.join(self.init_path, "description.cs"), "wb") as file:
                pickle.dump(self.dict_description, file)    
        self.create_sample_window()

    def find_path_symbol(self):
        path = list(Path(self.folder_path).parts)
        if path[-1] == "lower":
            sample = path[-2].lower()
        elif path[-1] == "upper":
            sample = path[-2].upper()       
        else:           
            sample = self.get_key(path[-1])
        if sample is not None:
            return sample    

    def get_key(self, val): 
        for key, value in self.nonalpha.items(): 
            if val == value: 
                return key

    def update_combo_button(self):
        ''' update the selection button list '''
        self.ui.button_selection.clear()
        for b in self.list_button_sample:
            self.ui.button_selection.addItem(b.text())

    def assign_combo_button(self):
        ''' assign a the selected button to a character ''' 
        #find the button
        button_selected = self.list_button_sample[self.ui.button_selection.currentIndex()] 
        button_selected.setText(self.ui.button_text.text())
        self.update_combo_button()

    def copy_to_bank(self):
        ''' copy the selected source file to active directory and rename according to bank number'''
        init_listfile = self.get_sorted_files()
        index_file = init_listfile.index(self.file_name)    
        self.unrename_list(init_listfile)
        if self.start_with_number:
            init_listfile = [file[2:] for file in init_listfile]
        else:
            init_listfile = [file for file in init_listfile]
        self.copy_file()
        after_listfile = self.get_sorted_files()
        file_to_copy = [x for x in after_listfile if x not in init_listfile]
        init_listfile.insert(self.ui.bank.value(), file_to_copy[0])
        self.rename_list_file(init_listfile)
        self.create_sample_window()

    def move_to_bank(self):
        init_listfile = self.get_sorted_files()    
        index_file = init_listfile.index(self.file_name)
        if self.file_name in init_listfile:
            self.unrename_list(init_listfile)
            if self.start_with_number:
                init_listfile = [file[3:] for file in init_listfile]
                self.file_name = self.file_name[3:]
            else:
                init_listfile = [file for file in init_listfile]
            init_listfile[self.ui.bank.value()], init_listfile[index_file] = init_listfile[index_file], init_listfile[self.ui.bank.value()]
            self.rename_list_file(init_listfile)   
        self.create_sample_window()

    def listen_sample_bank(self):
        ''' listen sample button '''   
        sender = self.sender()
        if sender.text().isalpha():
            if sender.text().islower(): 
                upperlower = "lower"
            else:
                upperlower = "upper"    
            txt_sample = str(sender.text().lower())
        else:
            txt_sample = "_"
            upperlower = self.nonalpha[sender.text()]   
        path_listen = os.path.join(self.dict_file["destination"], txt_sample, upperlower)
        list_sample_listen = os.listdir(path_listen)
        list_sample_listen.sort(key=str.casefold)
        self.play_audio(os.path.join(path_listen, list_sample_listen[self.ui.bank.value()]))

    def update_dict_from_table(self):
        for currentQTableWidgetItem in self.sample_window.tableWidget.selectedItems():
            if currentQTableWidgetItem.column() == 0:
                self.dict_description[self.sample_window.tableWidget.verticalHeaderItem(currentQTableWidgetItem.row()).text()] = currentQTableWidgetItem.text()
                #self.ui.sample_description.setText(currentQTableWidgetItem.text())
        with open(os.path.join(self.init_path, "description.cs"), "wb") as file:
                pickle.dump(self.dict_description, file)

    def open_foxdot(self):
        try:
            Popen(["python3", "-m", "FoxDot", "-n", "-d", self.init_path])                     
        except:
            try:
                Popen(["python", "-m", "FoxDot", "-n", "-d", self.init_path])
            except:
                self.msg_box("Couldn't execute Foxdot", "Please install foxdot first", "Foxdot Error !")

    def open_dir_foxdot(self):
        ''' Open selected FoxDot directory'''
        self.open_dir(self.init_path)
    
    def open_dir_src(self):
        ''' Open selected source directory'''
        self.open_dir(self.library_path)

    def open_dir(self, path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            Popen(["open", path])
        else:
            Popen(["xdg-open", path])            
                
    def create_dict(self):
        for ch in self.alpha:
            self.dict_description[ch.lower()] = ""
            self.dict_description[ch.upper()] = ""
        for ch in self.nonalpha:
            self.dict_description[ch] = ""
        with open(os.path.join(self.init_path, "description.cs"), "wb") as file:
                pickle.dump(self.dict_description, file)        


class Sample_Window(QtWidgets.QWidget):
 
    def __init__(self, row, parent=None):
        super(Sample_Window, self).__init__(parent)
        self.row = row + 1
        self.title = 'Sample Dictionnary'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 1000
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.createTable()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout)

    def createTable(self):        
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setRowCount(self.row)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem("Description"))
        self.tableWidget.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem("Nbr of samples"))

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    ret = app.exec_()
    
    app.quit()   
    sys.exit(ret)
