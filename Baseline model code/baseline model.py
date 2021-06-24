import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import sklearn.metrics as metrics
from sklearn import tree


def obtain_data():
    """
    Reads all csv files of the LUCAS 2015 dataset. Reads the reflectance
    values and OC values of all given location points and gets put in a pandas dataframe.

    Returns
    -------
         A pandas dataframe with all the raw data.

    """
    # Every land code, each code is a csv file.
    LC = ["AT", "BE", "NL", "DE", "UK", "EL", "EE", "DK", "CZ", "CY", "BG", "FI", "FR",
          "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "PL", "PT", "RO", "SE", "SI", "SK"]

    result = pd.DataFrame()
    spec = pd.read_csv(r'C:/Users/User/Documents/LUCAS2015_topsoildata_20200323/LUCAS_Topsoil_2015_20200323.csv')

    for c in LC:
        df = pd.read_csv(
            r"C:/Users/User/Documents/LUCAS2015_spectra/LUCAS2015_Soil_Spectra_EU28/spectra_ " + c + " .csv")
        columns = df.columns[5:]
        columns = columns.insert(0, 'PointID')
        left = df[columns]
        right = spec[['Point_ID', 'OC']]
        right = right.rename(columns={'Point_ID': 'PointID'})
        r = pd.merge(left, right, on="PointID")
        result = pd.concat([result, r], axis=0)

    return result


def remove_outliers(result):
    """
    Remove all strong outliers of the OC values in the dataset.

    Parameters
    ----------
        result (pandas dataframe): complete dataset.

    Returns
    -------
         A pandas dataframe with its outliers removed.

    """
    Q1 = result['OC'].quantile(0.25)
    Q3 = result['OC'].quantile(0.75)
    IQR = Q3 - Q1

    result = result[result['OC'] < Q3 + IQR * 1.5]
    result = result[result['OC'] > Q1 - IQR * 1.5]
    result = result.reset_index()
    return result


def split_data(result, test_size=0.20, random_state=3):
    """
    Seperate the dataset into its label (y) and input data (X), and
    split the data into train and test data, the test data is test_size% of the entire dataset.

    Parameters
    ----------
        result (pandas dataframe): complete dataset.
        test_size (float): How much of the dataset becomes the test set.
        random_state (int): The seed that splits the dataset for consistent outputs.

    Returns
    -------
         4 variables containing the feature test and train set, and
         target train and test set.

    """
    X = result[result.columns[2:-1]].values
    y = result[result.columns[-1]].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    return X_train, X_test, y_train, y_test


def linear_regression_model(X_train, X_test, y_train, y_test):
    """
    The linear regression model, build and fitted. Here the
    results also get printed.

    Parameters
    ----------
        X_train (numpy list): The features the model gets trained on
        X_test (numpy list): The features the model gets tested on
        y_train (numpy list): The targets the model gets trained on
        y_test (numpy list): The targets the model gets tested on

    """
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
    print(model.score(X_test, y_test))


def decision_tree_model(X_train, X_test, y_train, y_test):
    """
    The decision tree model, build and fitted. Here the
    results also get printed.

    Parameters
    ----------
        X_train (numpy list): The features the model gets trained on
        X_test (numpy list): The features the model gets tested on
        y_train (numpy list): The targets the model gets trained on
        y_test (numpy list): The targets the model gets tested on

    """
    DT = tree.DecisionTreeRegressor()
    DT.fit(X_train, y_train)
    y_predDT = DT.predict(X_test)
    print(np.sqrt(metrics.mean_squared_error(y_test, y_predDT)))
    print(DT.score(X_test, y_test))
