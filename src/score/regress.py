import os
import sys
import glob
import cv2 as cv
import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal
from sklearn import svm

sift = cv.xfeatures2d.SIFT_create()


def dictionary(descriptors, N):
    em = cv.EM(N)
    em.train(descriptors)
    return np.float32(em.getMat("means")), np.float32(em.getMatVector("covs")), np.float32(em.getMat("weights"))[0]


def image_descriptors(file):
    img = cv.imread(file, 0)
    img = cv.resize(img, (256, 256))
    _, descriptors = sift.detectAndCompute(img, None)
    return descriptors


def folder_descriptors(folder):
    files = glob.glob(os.path.join(folder, "*.png"))
    print("Calculating descriptos. Number of images is", len(files))
    return np.concatenate([image_descriptors(file) for file in files])


def likelihood_moment(x, ytk, moment):
    x_moment = np.power(np.float32(x), moment) if moment > 0 else np.float32([1])
    return x_moment * ytk


def likelihood_statistics(samples, means, covs, weights):
    gaussians, s0, s1, s2 = {}, {}, {}, {}
    samples = zip(range(0, len(samples)), samples)

    g = [multivariate_normal(mean=means[k], cov=covs[k]) for k in range(0, len(weights))]
    for index, x in samples:
        gaussians[index] = np.array([g_k.pdf(x) for g_k in g])

    for k in range(0, len(weights)):
        s0[k], s1[k], s2[k] = 0, 0, 0
        for index, x in samples:
            probabilities = np.multiply(gaussians[index], weights)
            probabilities = probabilities / np.sum(probabilities)
            s0[k] = s0[k] + likelihood_moment(x, probabilities[k], 0)
            s1[k] = s1[k] + likelihood_moment(x, probabilities[k], 1)
            s2[k] = s2[k] + likelihood_moment(x, probabilities[k], 2)

    return s0, s1, s2


def fisher_vector_weights(s0, s1, s2, means, covs, w, T):
    return np.float32([((s0[k] - T * w[k]) / np.sqrt(w[k])) for k in range(0, len(w))])


def fisher_vector_means(s0, s1, s2, means, sigma, w, T):
    return np.float32([(s1[k] - means[k] * s0[k]) / (np.sqrt(w[k] * sigma[k])) for k in range(0, len(w))])


def fisher_vector_sigma(s0, s1, s2, means, sigma, w, T):
    return np.float32(
        [(s2[k] - 2 * means[k] * s1[k] + (means[k] * means[k] - sigma[k]) * s0[k]) / (np.sqrt(2 * w[k]) * sigma[k]) for
         k in range(0, len(w))])


def normalize(fisher_vector):
    v = np.sqrt(abs(fisher_vector)) * np.sign(fisher_vector)
    return v / np.sqrt(np.dot(v, v))


def fisher_vector(samples, means, covs, w):
    s0, s1, s2 = likelihood_statistics(samples, means, covs, w)
    T = samples.shape[0]
    covs = np.float32([np.diagonal(covs[k]) for k in range(0, covs.shape[0])])
    a = fisher_vector_weights(s0, s1, s2, means, covs, w, T)
    b = fisher_vector_means(s0, s1, s2, means, covs, w, T)
    c = fisher_vector_sigma(s0, s1, s2, means, covs, w, T)
    fv = np.concatenate([np.concatenate(a), np.concatenate(b), np.concatenate(c)])
    fv = normalize(fv)
    return fv


def generate_gmm(data_dir, N, sub_dirs=["train", "test"]):
    words = np.concatenate([folder_descriptors(os.path.join(data_dir, i)) for i in sub_dirs])

    print("Training GMM of size", N)
    means, covs, weights = dictionary(words, N)

    # Throw away gaussians with weights that are too small
    th = 1.0 / N
    means = np.float32([m for k, m in enumerate(means) if weights[k] > th])
    covs = np.float32([m for k, m in enumerate(covs) if weights[k] > th])
    weights = np.float32([m for k, m in enumerate(weights) if weights[k] > th])

    np.save(os.path.join(data_dir, "means.gmm.npy"), means)
    np.save(os.path.join(data_dir, "covs.gmm.npy"), covs)
    np.save(os.path.join(data_dir, "weights.gmm.npy"), weights)
    return means, covs, weights


def get_fisher_vectors_from_folder(folder, gmm):
    """if folder is train, then return the fisher feature for the pictures in this folder as well as their scores
       else return the fisher feature as well as their file name"""
    files = glob.glob(os.path.join(folder, "*.png"))
    if "train" in folder:
        with open(os.path.join(folder, "score.txt")) as f:
            score = {l.split()[0]: l.split()[1] for l in f}

        ff = np.float32([fisher_vector(image_descriptors(file), *gmm) for file in files])
        ss = np.float32([score[os.path.basename(file)] for file in files])
    else:
        ff = np.float32([fisher_vector(image_descriptors(file), *gmm) for file in files])
        ss = [os.path.basename(file) for file in files]
    return ff, ss


def fisher_features(data_dir, gmm, sub_dirs=["train", "test"]):
    features = dict()
    score = dict()
    for sub_dir in sub_dirs:
        fv, sc = get_fisher_vectors_from_folder(os.path.join(data_dir, sub_dir), gmm)
        features[sub_dir] = fv
        score[sub_dir] = sc
    return features, score


def load_gmm(data_dir):
    files = ["means.gmm.npy", "covs.gmm.npy", "weights.gmm.npy"]
    return [np.load(os.path.join(data_dir, file)) for file in files]


"""
tree -L 2 data_dir

"""


def main(data_dir, gmm_existing=False, gmm_number=5):
    gmm = load_gmm(data_dir) if gmm_existing else generate_gmm(data_dir, gmm_number)

    ff, ss = fisher_features(data_dir, gmm)

    # TBD, split the features into training and validation
    # TBD, user full connected neural network train the data and score
    svr = svm.SVR(kernel="linear")
    svr.fit(ff["training"], ss["training"])
    Y = svr.predict(ff["test"])

    rs = []
    for s_t, s_p in zip(ss["test"], Y):
        rs.append([s_t, s_p])
    return rs


if __name__ == "__main__":
    args = sys.argv
    data_dir = args[1]
    gmm_existing = args[2].lower() == "true" if len(args) > 2 else False
    gmm_number = int(args[3]) if len(args) > 3 else 5
    print(data_dir, gmm_existing, gmm_number)
    rs = main(data_dir, gmm_existing, gmm_number)
    pd.DataFrame(rs, columns="targ,pred".split(","))
