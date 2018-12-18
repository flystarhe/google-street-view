import os
from src.score.regress import load_gmm, load_svr
from src.score.regress import get_fisher_vectors

base_dir = "/home/hejian/PycharmProjects/google-street-view/models"

gmm_path = "gmm"
svr_path = {'beautiful': 'svr.model.12181152', 'boring': 'svr.model.12181231', 'depressing': 'svr.model.12181251',
            'lively': 'svr.model.12181330', 'safety': 'svr.model.12181410', 'wealthy': 'svr.model.12181432'}

gmm = load_gmm(os.path.join(base_dir, gmm_path))
svr_list = {name: load_svr(os.path.join(base_dir, model_path)) for name, model_path in svr_path.items()}


def inference(image_list):
    # image_list: [image_file_path,..]
    global gmm, svr_list
    X, y = get_fisher_vectors([[image, None] for image in image_list], None, gmm)
    rs = {name: svr.predict(X).clip(0, 10) for name, svr in svr_list.items()}
    return rs
