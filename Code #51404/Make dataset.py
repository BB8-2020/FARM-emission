import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal
from scipy.signal import savgol_filter
import io
import pickle


def data_clean(countryfile, folder):
    """
    Makes the dataset obtaining all the needed raw data and
    puts every second point of them in a new csv file. Changes the
    absorbance value into reflectance values as well.

    Parameters
    ----------
        countryfile (string): landcode to locate the correct file in the folder.

    """
    with open(r"C:\Users\User\Documents\LUCAS2015_spectra\LUCAS2015_Soil_Spectra_EU28\spectra_ " + countryfile + " .csv") as f:
        # maakt csv reader aan
        reader = csv.reader(f)
        # Open
        with open(folder + r"\spectra_ " + countryfile + " .csv", 'w', newline='') as file:
            writer = csv.writer(file)
            for c, row in enumerate(reader):
                if c == 0:
                    writer.writerow(row[:5] + row[205:-200:2])
                else:
                    x = np.array(row[205:-200:2], dtype='float64')
                    reflectance = 10 ** (-x)
                    writer.writerow(row[:5] + list(reflectance))


def make_base_dataframe():
    """
    Makes a base dataframe containing the point id's,
    OC values, landcodes and OC range.

    Returns
    -------
         A pandas dataframe.

    """
    co_data_path = r"C:\Users\User\Documents\LUCAS2015_topsoildata_20200323\LUCAS_Topsoil_2015_20200323.csv"

    col_list = ["Point_ID", "NUTS_0", "OC"]
    df = pd.read_csv(co_data_path, usecols=col_list)
    max_value = df["OC"].max()
    for i in range(20, int(max_value) + 1, 20):
        df.loc[(df['OC'] < i) & (df['OC'] > (i-20)), ['OC_state']] = f'{i-20}-{i}'
    return df


def add_spectogram_images(df, folder, countries):
    """
    Makes all the spectograms with the whole dataset and is added to
    a dataframe. This whole dataframe is saved in a hdf5 file.
    
    Parameters
    ----------
        df (pandas dataframe): base dataframe to add the spectograms to.
        folder (string): folder where the reflectance values are located in
        countries (list): a list of country codes to loop through each csv file in the folder.

    """
    for country in countries:
        print(country)
        # Makes a dataframe subset and adds a column for the spectograms
        df_country = df.loc[df['NUTS_0'] == country]
        df_country["spectogram"] = np.nan
        df_country["spectogram"] = df_country["spectogram"].astype(object)
        data_clean(country, folder)

        with open(folder + r"\spectra_ " + country + " .csv") as fi:
            re = csv.reader(fi)
            np.array(next(re)[5:])

            for c, ro in enumerate(re):
                pointid = ro[2]
                if int(pointid) in df_country['Point_ID'].values:

                    # make spectogram
                    reflectance = np.array(ro[5:])
                    r = savgol_filter(reflectance, 11, 2)
                    f, t, Sxx = signal.spectrogram(r, 1)
                    sxx_sdv = np.array(
                        [[(Sxx[i][j] - np.mean(Sxx[i])) / np.std(Sxx[i]) for j in range(Sxx.shape[1])] for i in
                         range(Sxx.shape[0])])
                    fig, ax = plt.subplots()
                    ax.axis('off')
                    ax.pcolormesh(t, f, sxx_sdv, shading='gouraud')  # , shading='gouraud'

                    # save spectogram in RAM for faster saving
                    io_buf = io.BytesIO()
                    fig.savefig(io_buf, format='rgba', dpi=72)
                    io_buf.seek(0)
                    img_arr = np.reshape(np.frombuffer(io_buf.getvalue(), dtype=np.uint8),
                                         newshape=(int(fig.bbox.bounds[3]), int(fig.bbox.bounds[2]), -1))
                    io_buf.close()
                    plt.close()

                    # cut white edges off image
                    array = img_arr[35:-36]
                    array = array[:, 54:-43]
                    array = np.delete(array[:], -1, -1)
                    # add spectogram do dataframe
                    df_country.loc[df_country['Point_ID'] == int(pointid), ['spectogram']] = [array]

        # save dataframe in hdf5 file
        df_country = df_country.dropna()
        df_country.to_hdf(folder + r"\labeled_data.hdf5", country)


def change_pickle_protocol(folder, countries):
    """
    Converts hdf5 file into a hdf5 file with pickle 4 protocol for
    python 3.7 compatibility

    Parameters
    ----------
        folder (string): folder where the reflectance values are located in
        countries (list): a list of country codes to loop through each csv file in the folder.

    """
    pickle.HIGHEST_PROTOCOL = 4
    for country in countries:
        temppd = pd.read_hdf(folder + r"\labeled_data.hdf5", key=country)
        temppd.to_hdf(folder + r"\labeled_data_pickle4.hdf5", country)
    print('done')


if __name__ == "__main__":
    folder = r"C:\Users\User\Documents\LUCAS2015_spectra\LUCAS2015_Soil_Spectra_EU28_v2"
    countries = ["AT", "BE", "NL", "UK", "EL", "EE", "DK", "CZ", "CY", "BG",
                 "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU",
                 "LV", "MT", "PL", "PT", "RO", "SE", "SI", "SK"]
    dataframe = make_base_dataframe()
    add_spectogram_images(dataframe, folder, countries)
    change_pickle_protocol(folder, countries)
