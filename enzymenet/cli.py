import os
import glob
from Bio.SeqIO import parse
import pandas as pd
import argparse

from enzymenet.utils import create_dict, arrange_predict, separate_fasta, merge_pred_table, remove_files, clean_len_exaa
from enzymenet.preprocess import run_preprocess
from enzymenet.predict import run_predict


DEFAULT_MODEL_PATH = os.path.expanduser("/root/.enzymenet/model")


def resolve_model_path(user_path: str) -> str:
    """Resolve the model path from user input with fallback to default."""
    if user_path and os.path.isdir(os.path.expanduser(user_path)):
        return os.path.expanduser(user_path)

    if os.path.isdir(DEFAULT_MODEL_PATH):
        return DEFAULT_MODEL_PATH

    raise FileNotFoundError(
        f"Model path not found: {user_path} and default {DEFAULT_MODEL_PATH}. "
        "`--model_path` で正しいモデルディレクトリを指定してください。"
    )


def validate_model_path(model_path: str) -> None:
    """Ensure required EC model files are present."""
    required_dirs = ["EC_1d", "EC1_4d", "EC2_4d", "EC3_4d", "EC4_4d", "EC5_4d", "EC6_4d"]
    missing = []

    for dir_ in required_dirs:
        base = os.path.join(model_path, dir_)
        if not os.path.isdir(base):
            missing.append(base)
            continue

        if not os.path.exists(os.path.join(base, f"{dir_}_model_config.json")):
            missing.append(os.path.join(base, f"{dir_}_model_config.json"))
        if not os.path.exists(os.path.join(base, "ckpt")):
            missing.append(os.path.join(base, "ckpt"))
        if not os.path.exists(os.path.join(base, f"{dir_}_label_pair.tsv")):
            missing.append(os.path.join(base, f"{dir_}_label_pair.tsv"))

    if missing:
        raise FileNotFoundError(
            f"Missing model files or directories: {missing[:5]}...\n"
            "Ensure model path contains EC_1d, EC1_4d..EC6_4d and required config/ckpt/label files."
        )


def build_parser():
    parser = argparse.ArgumentParser(
        prog = "EC_Predictor",
        description = "This program is to predict EC number",
        add_help=True
    )

    parser.add_argument("input_path", type=str)
    parser.add_argument("output_path", nargs="?", default="result", help="Output directory path (default: result)")
    parser.add_argument("--model_path", default=DEFAULT_MODEL_PATH, help="Path to model directory (default: ~/.enzymenet/model)")
    return parser


def main(argv=None):
    # ユーザの入力が必要な変数
    parser = build_parser()
    args = parser.parse_args(argv)
    #fasta_name = args.fasta_file
    model_path = resolve_model_path(args.model_path)
    validate_model_path(model_path)
    origin_fasta_f = args.input_path

    # ユーザ入力が不要な変数
    tar_ec1d = "EC_1d"
    tar_ec4d_b = "EC{}_4d"
    ec_nums = ["1", "2", "3", "4", "5", "6"]
    pp_batchsize = 50000
    maxlength = 1024
    maxseqlen = 1000
    pred_batchsize = 128

    
    vocab_f = os.path.join(*["enzymenet","asset", "vocab_no_exAA_no_ClsEos.json"])

    outdir = args.output_path
    if not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)
    if not os.path.exists(os.path.join(outdir, "EC_1d")):
        os.mkdir(os.path.join(outdir, "EC_1d"))
    for i in ec_nums:
        ec4d_dir = os.path.join(outdir, "EC{}_4d".format(i))
        if not os.path.exists(ec4d_dir):
            os.mkdir(ec4d_dir)

    fasta_dic_f = os.path.join(*[outdir, "name_seq_dic.pkl"])
    tfrecord_base = os.path.join(*[outdir, "{}", "batch_v"])
    config_base = os.path.join(*[model_path, "{}", "{}_model_config.json"])
    weight_base = os.path.join(*[model_path,"{}", "ckpt", "ckpt-{}"])
    lb_base = os.path.join(*[model_path,"{}", "{}_label_pair.tsv"])
    pred_arg_base = os.path.join(*[outdir, "{}", "{}_arrange_pred.tsv"])
    separate_base = os.path.join(*[outdir, "EC{}_4d", "EC_1d_select.fasta"])
    final_output = os.path.join(*[outdir, "EC_predict_final_result.tsv"])


    try:
        # maxlength を超える　または　例外文字を含む配列は削除　もし削除後に配列が 0 になった場合はerror として処理を終了する
        clean_fasta_f = os.path.join(*[outdir,origin_fasta_f.replace(".fasta", "_clean.fasta")])
        flag = clean_len_exaa(origin_fasta_f, maxseqlen, clean_fasta_f)
        assert flag == True, "All sequences are length > 1000 or containing BJOUXZ."

        # name, sequence の辞書を作成
        create_dict(clean_fasta_f, fasta_dic_f)

        # preprocess によるtfrecor の作成
        ec1d_tfrecord_base = tfrecord_base.format(tar_ec1d)
        run_preprocess(clean_fasta_f, vocab_f, pp_batchsize, maxlength, ec1d_tfrecord_base)

        # predict
        ec1d_tfs = glob.glob(os.path.join(*[outdir, tar_ec1d, "*.tfrecord"]))
        run_predict(tar_ec1d, ec1d_tfs, config_base, weight_base, pred_batchsize)

        # 予測結果の整理
        arrange_predict(tar_ec1d, outdir, lb_base)

        # EC_1d 結果をもとにfasta ファイルのseparate
        ec1d_pred_f = pred_arg_base.format(tar_ec1d, tar_ec1d)
        separate_fasta(fasta_dic_f, ec1d_pred_f, separate_base)

        # EC_4d  4桁目までの予測
        for ec in ec_nums:
            ec4d_fasta_f = glob.glob(separate_base.format(ec))
            if len(ec4d_fasta_f) == 0:
                continue
            else:
                ec4d_fasta_f = ec4d_fasta_f[0]

            tar_ec4d = tar_ec4d_b.format(ec)
            # preprocess によるtfrecor の作成
            ec4d_tfrecord_base = tfrecord_base.format(tar_ec4d)
            run_preprocess(ec4d_fasta_f, vocab_f, pp_batchsize, maxlength, ec4d_tfrecord_base)

            # predict
            ec4d_tfs = glob.glob(os.path.join(*[outdir, tar_ec4d, "*.tfrecord"]))
            run_predict(tar_ec4d, ec4d_tfs, config_base, weight_base)

            # 予測結果の整理
            arrange_predict(tar_ec4d, outdir, lb_base)

        # EC_1d, EC_4d 結果のマージ
        pred_1d_f = pred_arg_base.format(tar_ec1d, tar_ec1d)
        pred_4d_fs = glob.glob(os.path.join(*[outdir, "EC*_4d", "*_arrange_pred.tsv"]))
        merge_pred_table(pred_1d_f, pred_4d_fs, final_output)

        # 不要なファイルの削除
        del_fas = glob.glob(os.path.join(*[outdir, "*", "*.fasta"]))
        del_tfds = glob.glob(os.path.join(*[outdir, "*", "*.tfrecord"]))
        remove_files(del_fas) 
        remove_files(del_tfds)

    except AssertionError as err:
        print(err)
