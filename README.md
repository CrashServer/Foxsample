# FoxSample v0.001
A FoxDot sample manager

A Python / Pyqt5 program to manage FoxDot sample directory.
You can add from external sources, listen to samples, auto rename, add descriptions and more.

Foxdot is a livecoding language. More info http://foxdot.org

## Getting Started

### Prerequisites
```
- Python 3
- Pyqt5 
```

### Installing

clone or copy to whatever directory 

and run with:

```
python3 foxsample.py
```

## How does it work ?

![Alt text](screen.png?raw=true)

1 - When you start the program for the first time, you must choose a foxdot snd directory. This is not necessarily the official directory, it can be any directory, but it must have same structure (a/upper/, _/+/, ...).
Next time you open the program, this location is saved.
Tips : work with a copy of the original directory

2 - Navigate through the directory, choose one, and select a sample to listen to it.

3 - When you select a sample it show you some informations. For now you can only listen to wav files (and something is wrong with 24bits files)

4 - A few usefull functions :
  * Move to bank no : rename all files and put the selected file at the active `select bank` position (no 6 in the screenshot).
    eg: if you want to have the selected file in foxdot as sample=2, put 2 in `select bank`. 
  * Rename all : rename all files in the selected directory and add index before according to actual order
  * Unrename all : remove the index
  * Delete : delete the selected sample file
  * Rename : rename manually the selected sample file

5 - the listen buttons
  * you can easily listen to 10 sample directories using these buttons. The index of the sample played will be the one selected in `sample bank`. This in order to create coherent sample banks (all samples of 808 in sample = 8) 
  * with `ReAssign button`, put a character in the text field, selected the char you wanna switch in the combobox and click `assign`  

6 - `select bank` select the sample index for `listen buttons`, `move to bank` and `copy to bank functions`

7 - show or hide the sample description table. When you select a directory, you can add or modify a description in the `Sample Description` field, when you press RETURN it save to a file `description.cs` in the root of your sample directory. You even have the number of samples per repertoire

8 - you can choose a directory where you store your personnal samples

9 - copy the selected personnal sample to the selected FoxDot directory. You can copy to an index or a simple copy 

10 - You can adjust the volume of the listen samples in the program. Doesn't affect the files.
     You can listen in endless loop the samples.

## Future upgrade
 * function to convert files to wav 44000 16 bits
 * auto-update the dictionary when changes
 * possibility to edit the dictionary

## Authors

* **Zbdm**
