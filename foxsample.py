#coding: utf8
#!/usr/bin/env python3

from PyQt5  import QtWidgets, QtCore
from PyQt5.QtMultimedia import QSoundEffect

from layout import Ui_MainWindow
#from pydub import AudioSegment
#from pydub.playback import play
#import simpleaudio as sa
import wave
import sys
import os
import shutil
import pickle
from subprocess import call 
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
        
        with open("file_path.cs", "rb") as file:
	        self.dict_file = pickle.load(file)

        self.folder_path = self.dict_file["destination"]
        self.file_path = ""
        self.library_path = self.dict_file["source"]
        self.library_file_path = ""
        if os.path.isdir(self.folder_path):
            pass
        else:
            self.browse_sample_path()
        self.init_path = self.folder_path    
        if os.path.isfile(os.path.join(self.folder_path, "description.cs")):
            with open(os.path.join(self.folder_path, "description.cs"), "rb") as file:
                self.dict_description = pickle.load(file)  

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
        self.file_filters = ["*.wav", "*.aif", "*.ogg"]
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
        
        ### Buttons click
        self.ui.copy_button.clicked.connect(self.copy_file)
        self.ui.delete_button.clicked.connect(self.delete_file)
        self.ui.rename_all_button.clicked.connect(self.rename_all)
        self.ui.move_to_bank_button.clicked.connect(self.move_to_bank)
        
        self.ui.rename_button.clicked.connect(self.rename_file)
        self.ui.unrename_button.clicked.connect(self.uname_all)
        self.ui.convert_button.clicked.connect(self.convert_to_wav)

        self.ui.sample_description.returnPressed.connect(self.update_dict_description)
        self.ui.checkBox_sample_window.toggled.connect(self.show_sample_window)
        self.ui.loop_checkbox.stateChanged.connect(self.play_audio)

        # Samples button
        self.list_button_sample = [self.ui.sampleButton1, self.ui.sampleButton2, self.ui.sampleButton3, self.ui.sampleButton4,
        self.ui.sampleButton5,self.ui.sampleButton6,self.ui.sampleButton7,self.ui.sampleButton8, self.ui.sampleButton9,self.ui.sampleButton10]
        for sampleButton in self.list_button_sample:
            sampleButton.clicked.connect(self.listen_sample_bank)
     
        #assign button
        self.update_combo_button()
        self.ui.assign_button.clicked.connect(self.assign_combo_button)
        self.ui.copy_to_bank_no_button.clicked.connect(self.copy_to_bank)

        ### create sample  windows
        self.sample_window = Sample_Window(len(self.dict_description))
        self.create_sample_window()
        self.sample_window.tableWidget.cellChanged.connect(self.update_dict_from_table)      

    def browse_sample_path(self):
        ## Select the Foxdot sample directory
        self.folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Open FoxDot Sample Folder (./FoxDot/snd/ by default) ", self.folder_path, QtWidgets.QFileDialog.ShowDirsOnly)
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
        self.dict_file = {"destination": self.folder_path, "source": self.library_path}
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
        self.file_path = self.fileModel.fileInfo(index).absoluteFilePath()
        self.file_name = str(self.fileModel.fileInfo(index).fileName())
        #self.sound = AudioSegment.from_file(self.file_path)
        self.sample_info(self.file_path)
        self.play_audio(self.file_path)
        

    def on_clicked_folder_library(self, index):
        self.library_path = self.dirModelLibrary.fileInfo(index).absoluteFilePath()
        self.ui.listView_library.setRootIndex(self.libraryModel.setRootPath(self.library_path))

    def on_clicked_file_library(self, index):
        self.library_file_path = self.libraryModel.fileInfo(index).absoluteFilePath()
        #self.sound_library = AudioSegment.from_file(self.library_file_path)
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
        except:
            pass        
        if os.path.isfile(filepath):
            self.sound = QSoundEffect(self)
            self.sound.setSource(QtCore.QUrl.fromLocalFile(filepath))
            self.sound.setVolume(self.ui.volume_slider.value()/100)
            if self.ui.loop_checkbox.isChecked():
                self.sound.setLoopCount(QSoundEffect.Infinite)               
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
            
            if char in keys_available:
                self.sample_window.tableWidget.setItem(x,0, QtWidgets.QTableWidgetItem(self.dict_description[char]))
            else:
                self.sample_window.tableWidget.setItem(x,0, QtWidgets.QTableWidgetItem("-"))
            x += 1

        self.sample_window.tableWidget.move(0,0)

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

    def rename_all(self):
        ''' rename all files from active destination'''
        listfile = self.get_sorted_files()
        self.rename_list_file(listfile)

    def rename_list_file(self, list_of_file):
        ''' Rename the file with index added if not present '''
        start_with_number = False    
        # test if begin with number_
        for file in list_of_file:
            if file[:1].isdigit() and file[1:2] == "_":
                start_with_number = True
            else:
                start_with_number = False    
        if not start_with_number:
            # add index_ to each files
            for number, file in enumerate(list_of_file):
                path_to_file = os.path.join(self.folder_path, file)
                path_to_new_file = os.path.join(self.folder_path, str(number) + "_" + str(file))
                os.rename(path_to_file, path_to_new_file)

    def uname_all(self):
        ''' remove the index_ of all active destination files '''
        listfile = self.get_sorted_files()
        self.unrename_list(listfile)

    def unrename_list(self, list_of_file):
        self.start_with_number = False
        # test if all begin with number         
        for file in list_of_file:
            if file[:1].isdigit() and file[1:2] == "_":
                self.start_with_number = True
            else:
                self.start_with_number = False    
        if self.start_with_number:
            i=1
            for file in list_of_file:
                path_to_file = os.path.join(self.folder_path, file)
                path_to_new_file = os.path.join(self.folder_path, str(file[2:]))
                if os.path.exists(path_to_new_file):
                    bef, sep, after = path_to_new_file.partition(".")
                    path_to_new_file = bef + str(i) + sep + after
                    i += 1
                os.rename(path_to_file, path_to_new_file)        

    def copy_file(self):
        ''' copy the selected source file to active destination directory '''
        if os.path.isfile(self.library_file_path) and os.path.isdir(self.folder_path):
            shutil.copy(self.library_file_path, self.folder_path)
        self.create_sample_window()    

    def delete_file(self):
        ''' delete the selected destination file '''
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)
        self.create_sample_window()

    def convert_to_wav(self):
        if os.path.isfile(self.file_path):
            file, sep, extension = self.file_path.partition(".")
            if extension == "wav":
                file += "_convert" 
            try:
                call(["ffmpeg", "-y", "-i", self.file_path, file+".wav"])
                self.delete_file()
            except:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setText("FFMPEG problem !")
                msg.setInformativeText('Make sure you have ffmpeg installed')
                msg.setWindowTitle("ffmpeg error")
                msg.exec_()
                
    def rename_file(self, index):
        new_name, ok = QtWidgets.QInputDialog.getText(self, 'Rename the file', 'Rename the file:', QtWidgets.QLineEdit.Normal, self.file_name)
        if ok:
            path_to_file = os.path.join(self.folder_path, self.file_name)
            path_to_new_file = os.path.join(self.folder_path, new_name)
            os.rename(path_to_file, path_to_new_file)
            
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
        if self.file_name in init_listfile:
            self.unrename_list(init_listfile)
            if self.start_with_number:
                init_listfile = [file[2:] for file in init_listfile]
                self.file_name = self.file_name[2:]
            else:
                init_listfile = [file for file in init_listfile]
            init_listfile.remove(self.file_name)
            init_listfile.insert(self.ui.bank.value(), self.file_name)
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
                self.ui.sample_description.setText(currentQTableWidgetItem.text())
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
        self.height = 800
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
