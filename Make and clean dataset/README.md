# Make dataset
These files contain code that creates the dataset with spectrograms

## Make dataset.py
* Get all spectral data with steps of 1 from 500nm - 2400nm
* Makes base dataframe with all the needed data in it
* Make spectrograms 
* Creates spectrograms for every spectral sample and adds to dataframe
* Saves dataframe into a HDF5 file with pickle 4 protocol

### Usage
- Change on line 22 the path to where your spectral files from LUCAS dataset are located
- Change on line 47 the path to where your LUCAS topsoil file is located
- Change on line 136 the path where you want to save the created files that are needed to run the models later on.

## make_dataset.ipynb
* Get all spectral data with steps of 1 from 500nm - 2400nm
* Makes base dataframe with all the needed data in it
* Make spectrograms 
* Creates spectrograms for every spectral sample and adds to dataframe
* Saves dataframe into a HDF5 file with pickle 4 protocol

### Usage
Change variable "folder" in code block 1 to where you want your created files to be saved
Change variable "folder_raw" in code block 1 where you get LUCAS data spectral files are located.

# Usage command
After you have changed the folder locations described above. You can run the files.

OS X & Linux:

```sh
python <filename.py>
```

Windows:

```sh
python <filename.py>

```
