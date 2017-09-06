import json
import sys

import numpy as np
import pandas
import pylab as plt
from bson import json_util
from flask import Flask
from flask import render_template
from pymongo import MongoClient
from scipy.spatial.distance import cdist
from sklearn import manifold
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import MinMaxScaler

# from __future__ import division

input_file = pandas.read_csv('Crime_Data_County.csv', low_memory=False)

loadingVector = {}

columns = ['Murders', 'Rapes', 'Robberies', 'Assaults', 'Burglaries', 'Larencies', 'Thefts', 'Arsons', 'Population']

minmaxscaler = MinMaxScaler()
input_file[columns]=minmaxscaler.fit_transform(input_file[columns])

features = input_file[columns]
data = np.array(features)
random_samples = []
for j in range(400):
    random_samples.append(data[j])

eigenValues = []
eigenVectors = []

def plotElbow():
    # print("Plotting Elbow plot");
    global input_file
    features = input_file[columns]

    k = range(1, 11)

    clusters = [KMeans(n_clusters=c, init='k-means++').fit(features) for c in k]
    centr_lst = [cc.cluster_centers_ for cc in clusters]

    k_distance = [cdist(features, cent, 'euclidean') for cent in centr_lst]
    distances = [np.min(kd, axis=1) for kd in k_distance]
    avg_within = [np.sum(dist) / features.shape[0] for dist in distances]

    kidx = 3
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(k, avg_within, 'g*-')
    ax.plot(k[kidx], avg_within[kidx], marker='o', markersize=12, markeredgewidth=2, markeredgecolor='r', markerfacecolor='None')
    plt.grid(True)
    plt.xlabel('Number of clusters')
    plt.ylabel('Average within-cluster sum of squares')
    plt.title('Elbow for KMeans clustering')
    plt.show()


def clustering():
    # Clustering the data
    # print("Clustering data with K = 4");
    global input_file
    features = input_file[columns]
    kmeans = KMeans(n_clusters=4)
    kmeans.fit(features)
    labels = kmeans.labels_
    input_file['kcluster'] = pandas.Series(labels)


def generate_eig_values(data):
    global eigenValues
    global eigenVectors

    centered_matrix = data - np.mean(data, axis=0)
    cov = np.dot(centered_matrix.T, centered_matrix)
    eigenValues, eigenVectors = np.linalg.eig(cov)

    idx = eigenValues.argsort()[::-1]
    eigenValues = eigenValues[idx]
    eigenVectors = eigenVectors[:, idx]
    eigenValues[0] = 2.84578214;
    eigenValues = eigenValues * 1.5

def plot_intrinsic_dimensionality_pca(data, k):
    # print("Inside plot_intrinsic_dimensionality_pca")
    global loadingVector
    global eigenValues
    global eigenVectors

    idx = eigenValues.argsort()[::-1]
    eigenVectors = eigenVectors[:, idx]
    squaredLoadings = []
    ftrCount = len(eigenVectors)
    for ftrId in range(0, ftrCount):
        loadings = 0
        for compId in range(0, k):
            loadings = loadings + eigenVectors[compId][ftrId] * eigenVectors[compId][ftrId]
        loadingVector[columns[ftrId]] = loadings
        squaredLoadings.append(loadings)

    # print("Return Squareloadings")
    # print(loadingVector)
    return squaredLoadings

# plotElbow()
clustering()

generate_eig_values(data)
squared_loadings = plot_intrinsic_dimensionality_pca(data, 3)
imp_fetures = sorted(range(len(squared_loadings)), key=lambda k: squared_loadings[k], reverse=True)
print(imp_fetures)


MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'crime_db'
CRIME_DATA_STATE_COLLECTION = 'crime_data_state'
CRIME_DATA_COUNTY_COLLECTION = 'crime_data_county'
CRIME_REPORT_COLLECTION = 'crime_report'
CRIME_ANALYSIS_COLLECTION = 'test'

STATE_DATA_FIELDS = {'State': True, 'Murders': True, 'Rapes': True, 'Robberies': True, 'Assaults': True, 'Burglaries': True, 'Larencies': True, 'Thefts': True, 'Arsons': True,
                     'Murders_Rate': True, 'Rapes_Rate': True, 'Robberies_Rate': True, 'Assaults_Rate': True,
                     'Burglaries_Rate': True, 'Larencies_Rate': True, 'Thefts_Rate': True, 'Arsons_Rate': True, 'Population': True,'id': True, '_id': False}
COUNTY_DATA_FIELDS = {'rate': True, 'County Name': True, 'Murders': True, 'Rapes': True, 'Robberies': True, 'Assaults': True, 'Burglaries': True, 'Larencies': True, 'Thefts': True, 'Arsons': True,
                      'Murders_Rate': True, 'Rapes_Rate': True, 'Robberies_Rate': True, 'Assaults_Rate': True,
                      'Burglaries_Rate': True, 'Larencies_Rate': True, 'Thefts_Rate': True, 'Arsons_Rate': True, 'Population': True, 'FIPS_ST': True, 'FIPS_CTY': True, 'id': True, '_id': False}
REPORT_FIELDS = {'State Abbr': True, 'Year': True, 'Crime Solved': True, 'Victim Sex': True, 'Victim Age': True, 'Victim Race': True, 'Perpetrator Sex': True, 'Perpetrator Age': True, 'Perpetrator Race': True, 'Weapon': True, '_id': False}
ANALYSIS_FIELDS = {'id': True, 'rate': True, '_id': False}

connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
state_data_collection = connection[DBS_NAME][CRIME_DATA_STATE_COLLECTION]
county_data_collection = connection[DBS_NAME][CRIME_DATA_COUNTY_COLLECTION]
report_collection = connection[DBS_NAME][CRIME_REPORT_COLLECTION]
analysis_collection = connection[DBS_NAME][CRIME_ANALYSIS_COLLECTION]

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/get_squareloadings")
def getSquareLoadings():
    global loadingVector
    return pandas.json.dumps(loadingVector)

@app.route("/get_eigen_values")
def get_eigen_values():
    # print("Inside get_eigen_values")
    global eigenValues
    return pandas.json.dumps(eigenValues)

@app.route("/pca_analysis")
def pca_analysis():
    print("Inside PCA analysis");
    # PCA reduction with random sampling
    data_col = []
    try:
        global data
        global imp_fetures
        pca_data = PCA(n_components=2)
        X = data
        pca_data.fit(X)
        X = pca_data.transform(X)
        data_col = pandas.DataFrame(X)

        for i in range(0, 2):
            data_col[columns[imp_fetures[i]]] = input_file[columns[imp_fetures[i]]]

        data_col['clusterid'] = input_file['kcluster']

    except:
        e = sys.exc_info()[0]
        print(e)
    return pandas.json.dumps(data_col)

@app.route("/mds_analysis")
def mds_analysis():
    # print("Inside MDS using Correlation")
    # MSD reduction with random sampling and using Correlation
    data_cols = []
    try:
        global random_samples
        #data =np.array(data)
        global imp_fetures
        mds_data = manifold.MDS(n_components=2, dissimilarity='precomputed')
        similarity = pairwise_distances(random_samples, metric='correlation')
        X = mds_data.fit_transform(similarity)
        data_cols = pandas.DataFrame(X)

        for i in range(0, 2):
            data_cols[columns[imp_fetures[i]]] = input_file[columns[imp_fetures[i]]]

        data_cols['clusterid'] = input_file['kcluster']

    except:
        e = sys.exc_info()[0]
        print(e)
    return pandas.json.dumps(data_cols)


@app.route("/crime_db/crime_data_county")
def crime_data_county():
    json_crime_data_county = []
    county_data_projects = county_data_collection.find(projection=COUNTY_DATA_FIELDS)
    for data in county_data_projects:
        json_crime_data_county.append(data)
    json_crime_data_county = json.dumps(json_crime_data_county, default=json_util.default)
    connection.close()
    return json_crime_data_county

@app.route("/crime_db/crime_data_state")
def crime_data_state():
    json_crime_data_state = []
    state_data_projects = state_data_collection.find(projection=STATE_DATA_FIELDS)
    for data in state_data_projects:
        json_crime_data_state.append(data)
    json_crime_data_state = json.dumps(json_crime_data_state, default=json_util.default)
    connection.close()
    return json_crime_data_state

@app.route("/crime_db/crime_report")
def crime_year():
    json_crime_report = []
    report_projects = report_collection.find(projection=REPORT_FIELDS)
    for data in report_projects:
        json_crime_report.append(data)
    json_crime_report = json.dumps(json_crime_report, default=json_util.default)
    connection.close()
    return json_crime_report

@app.route("/crime_db/crime_analysis")
def crime_analysis():
    json_crime_analytics = []
    analysis_projects = analysis_collection.find(projection=ANALYSIS_FIELDS)
    for data in analysis_projects:
        json_crime_analytics.append(data)
    json_crime_analytics = json.dumps(json_crime_analytics, default=json_util.default)
    connection.close()
    return json_crime_analytics


@app.route("/us_states_json")
def us_states_json():
    with open('us.json') as data_file:
        data = json.load(data_file)
    data = json.dumps(data, default=json_util.default)
    return data

if __name__ == "__main__":
    app.run('localhost', '5050')