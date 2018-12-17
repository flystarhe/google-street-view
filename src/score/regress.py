import os
import time
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal
from sklearn.externals import joblib
from sklearn import svm

cache_dir = "tmps"
sift = cv.xfeatures2d.SIFT_create()

if cache_dir:
    os.makedirs(cache_dir, exist_ok=True)


def dictionary(descriptors, N):
    # https://github.com/opencv/opencv/blob/master/samples/python/gaussian_mix.py
    em = cv.ml.EM_create()
    em.setClustersNumber(N)
    em.trainEM(descriptors)
    # np.float32(em.getMat("means")), np.float32(em.getMatVector("covs")), np.float32(em.getMat("weights"))[0]
    return np.float32(em.getMeans()), np.float32(em.getCovs()), np.float32(em.getWeights()[0])


def image_descriptors(image, keep=True):
    if cache_dir:
        npy_file = os.path.join(cache_dir, "{}.npy".format(os.path.basename(image)))
        if os.path.isfile(npy_file):
            return np.load(npy_file)

    image = cv.imread(image, 0)
    image = cv.resize(image, (256, 256))
    _, descriptors = sift.detectAndCompute(image, None)

    if cache_dir and keep:
        np.save(npy_file, descriptors)

    return descriptors


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


def generate_gmm(gmm_path, N, images):
    print("Calculating descriptos. Number of images is", len(images))
    words = np.concatenate([image_descriptors(image) for image, uid in images])

    print("Training GMM of size", N)
    means, covs, weights = dictionary(words, N)

    # Throw away gaussians with weights that are too small
    th = 1.0 / N
    means = np.float32([m for k, m in enumerate(means) if weights[k] > th])
    covs = np.float32([m for k, m in enumerate(covs) if weights[k] > th])
    weights = np.float32([m for k, m in enumerate(weights) if weights[k] > th])

    np.save(os.path.join(gmm_path, "means.gmm.npy"), means)
    np.save(os.path.join(gmm_path, "covs.gmm.npy"), covs)
    np.save(os.path.join(gmm_path, "weights.gmm.npy"), weights)
    return means, covs, weights


def get_fisher_vectors(images, score, gmm):
    if score:
        X = np.float32([fisher_vector(image_descriptors(image), *gmm) for image, uid in images])
        y = np.float32([score[uid] for image, uid in images])
    else:
        X = np.float32([fisher_vector(image_descriptors(image), *gmm) for image, uid in images])
        y = [uid for image, uid in images]
    return X, y


def save_svr(svr, save_to="."):
    if os.path.isdir(save_to):
        save_to = os.path.join(save_to, "svr.model")
    return joblib.dump(svr, save_to)


def load_svr(svr_path):
    if os.path.isdir(svr_path):
        svr_path = os.path.join(svr_path, "svr.model")
    return joblib.load(svr_path)


def load_gmm(gmm_path):
    if os.path.isfile(gmm_path):
        gmm_path = os.path.dirname(gmm_path)
    npy_list = ["means.gmm.npy", "covs.gmm.npy", "weights.gmm.npy"]
    return [np.load(os.path.join(gmm_path, npy_file)) for npy_file in npy_list]


def train(X, y):
    svr = svm.SVR(kernel="linear")
    svr.fit(X, y)
    return svr


def test(svr, gmm, image, uid=None):
    if isinstance(svr, str):
        svr = load_svr(svr)

    if isinstance(gmm, str):
        gmm = load_gmm(gmm)

    X, y = get_fisher_vectors([[image, uid]], None, gmm)
    y_ = svr.predict(X)
    return y, y_


def eval(targ, pred, bins=10, display=False):
    rs = []
    for t, p in zip(targ, pred):
        rs.append([t, p])

    if display:
        loss = [p - t for t, p in rs]
        plt.hist(loss, bins=bins)
        plt.show()

    return rs


def main(work_dir, score_file, train_file, test_file, gmm_number=5, force=True, batch_size=None):
    os.makedirs(work_dir, exist_ok=True)

    score = {}
    with open(score_file) as file:
        for line in file:
            try:
                uid, val = line.strip().split()
                score[uid] = np.float32(val)
            except:
                pass

    images_train = []
    with open(train_file) as file:
        for line in file:
            try:
                image, uid = line.strip().split()
                images_train.append([image, uid])
            except:
                pass

    images_test = []
    with open(test_file) as file:
        for line in file:
            try:
                image, uid = line.strip().split()
                images_test.append([image, uid])
            except:
                pass

    if batch_size:
        images_train = images_train[:int(batch_size)]
        images_test = images_test[:int(batch_size / 4)]
    print("train_size: {}, test_size: {}".format(len(images_train), len(images_test)))

    print("> load gmm or generate..")
    if force:
        gmm = generate_gmm(work_dir, gmm_number, images_train)
    else:
        gmm = load_gmm(work_dir)

    print("> load dataset..")
    train_X, train_y = get_fisher_vectors(images_train, score, gmm)
    test_X, test_y = get_fisher_vectors(images_test, score, gmm)

    print("> train svr..")
    svr = train(train_X, train_y)

    print("> predict..")
    train_y_ = svr.predict(train_X)
    test_y_ = svr.predict(test_X)

    print("> eval..")
    print("On train:", eval(train_y, train_y_))
    print("On test:", eval(test_y, test_y_))

    return save_svr(svr, os.path.join(work_dir, time.strftime("svr.model.%m%d%H%M")))
