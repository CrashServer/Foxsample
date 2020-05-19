# Zuper FoxDot Samples Manager- Turbo Edition v0.001
A simple FoxDot samples manager

A Python / Pyqt5 program to manage FoxDot sample directory.
You can copy from external sources, listen to samples, auto rename, add descriptions and more.

Foxdot is a livecoding language. More info http://foxdot.org

## Getting Started

### Prerequisites
```
- Python 3
- Pyqt5 
- ffmpeg (optional for wav conversion)
```

### Installing

clone or copy to whatever directory 

and run with:

```
python3 foxsample.py
```

## How does it work ?

![Alt text](screen.png?raw=true)

1 - When you start the program for the first time, you must choose a foxdot snd directory. This is not necessarily the official directory, it can be any directory, but it must have the same structure (a/upper/, _/+/, ...).
Next time you open the program, this location is saved.

WARNING : as it's still a beta vesion, it's better to work with a copy of the original directory

2 - Navigate through the directory, choose one, and select a sample to listen to it. If not, all the files in the directory will be reindexed.

3 - When you select a sample it show you some informations. For now you can only listen to wav files

4 - A few usefull functions :
  * You can move the postion of the sample with the UP/DOWN buttons
  * The actual postion of the sample is displayed on the lcd
  * You can swap 2 samples postions by selection a new number and click swap.
  * Re-index : rename all files in the selected directory and add index before according to actual order.
  * Rename : rename manually the selected sample file
  * Delete : delete the selected sample file
  * convert to wav : convert the selected file to wav 16bits/44100 (ffmpeg required)

5 - the listen buttons
  * you can easily listen to 10 sample directories using these buttons. The index of the sample played will be the one selected in `sample bank`. This in order to create consistent sample banks (all samples of 808 in sample = 8) 
  * with `ReAssign button`, put a character in the text field, selected the char you wanna switch in the combobox and click `assign`  

6 - `select bank` select the sample index for `listen buttons`.

7 - Show or hide the sample description table. When you select a directory, you can add or modify a description in the `Sample Description` field, when you press RETURN it save to a file `description.cs` in the root of your sample directory. You even have the number of samples per directory and you can edit the description in this window. 

8 - Choose the directory where you store your personnal samples

9 - Copy the selected personnal sample to the selected FoxDot directory. You can copy or move the file. 

10 - You can adjust the volume of the listen samples in the program. Doesn't affect the files.
     You can listen in endless loop the samples.

## Future upgrade
 - trim samples
 - adjust volume of the samples
 - use pydub for playback audio, trim, volume audio ?

## Authors

* **Zbdm**
