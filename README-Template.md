# FoxSample
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
Tips : work with a copy of the original directory

2 - Navigate through the directory and choose one, and select a sample to listen to it.

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
  * 

## Authors

* **Zbdm**

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

