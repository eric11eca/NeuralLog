import os
import argparse

datasets = ["gold", "diagnostic",
            "monotonicity_hard", "monotonicity_simple",
            "boolean", "conditional", "counting", "negation"]


def parse_dataset_path(dataset):
    if dataset == "gold":
        dataset_path = "gold"
    elif dataset == "diagnostic":
        dataset_path = "GLUE/glue_data/diagnostic"
    elif dataset == "monotonicity_hard":
        dataset_path = "SEG/monotonicity_hard"
    elif dataset == "monotonicity_simple":
        dataset_path = "SEG/monotonicity_simple"
    elif dataset == "boolean":
        dataset_path = "SEG/boolean"
    elif dataset == "conditional":
        dataset_path = "SEG/conditional"
    elif dataset == "counting":
        dataset_path = "SEG/counting"
    elif dataset == "negation":
        dataset_path = "SEG/negation"

    in_name = "{}.txt".format(dataset)
    val_name = "{}.label.txt".format(dataset)
    out_name = "{}.polarized.txt".format(dataset)
    incorrect_log_name = "{}.incorrect.txt".format(dataset)
    unmatched_log_name = "{}.unmatched.txt".format(dataset)
    unmatched_val_name = "{}.unmatched.ccg.txt".format(dataset)
    except_log_name = "{}.exception.txt".format(dataset)
    pos_name = "{}.pos.txt".format(dataset)

    path = os.path.join("../data", dataset_path)
    in_path = os.path.join(path, in_name)
    val_path = os.path.join(path, val_name)
    out_path = os.path.join(path, out_name)
    incorrect_log_path = os.path.join(path, incorrect_log_name)
    unmatched_log_path = os.path.join(path, unmatched_log_name)
    unmatched_val_path = os.path.join(path, unmatched_val_name)
    exception_log_path = os.path.join(path, except_log_name)
    pos_path = os.path.join(path, pos_name)

    return {
        "in_path": in_path,
        "val_path": val_path,
        "out_path": out_path,
        "incorrect_log_path": incorrect_log_path,
        "unmatched_log_path": unmatched_log_path,
        "unmatched_val_path": unmatched_val_path,
        "exception_log_path": exception_log_path,
        "pos_path": pos_path
    }


def polarize_dataset(dataset, add_pos=0, mode="polarize", parser="stanza"):
    path = parse_dataset_path(dataset)

    if mode == "polarize":
        with open(path['in_path'], "r") as data:
            sentences = data.readlines()
            annotations, exceptioned = run_polarize_pipeline(
                sentences,
                verbose=2,
                parser=parser)

            with open(path['out_path'], "w") as correct:
                for sent in annotations:
                    correct.write("%s\n" % sent[0])

    elif mode == "eval":
        with open(path['in_path'], "r") as data:
            with open(path['val_path'], "r") as annotation:
                lines = data.readlines()
                annotations_val = annotation.readlines()
                annotations, exceptioned, incorrect = polarize_eval(
                    lines, annotations_val,
                    verbose=2,
                    parser="stanford")

                with open(path['out_path'], "w") as correct:
                    for sent in annotations:
                        correct.write("%s\n" % sent["annotated"])

                with open(path['incorrect_log_path'], "w") as incorrect_log:
                    with open(path['unmatched_val_path'], "w") as unmatched_val:
                        for sent in incorrect:
                            incorrect_log.write(sent[0])
                            unmatched_val.write(sent[2])

                with open(path['exception_log_path'], "w") as except_log:
                    for sent in exceptioned:
                        except_log.write(sent[0])
                        except_log.write(sent[1])

                if add_pos == 1:
                    with open(path['pos_path'], "w") as postag:
                        for sent in annotations:
                            postag.write(sent["orig"])
                            postag.write("%s\n" % sent["postag"])

        with open(path['incorrect_log_path'], "r") as incorrect_log:
            with open(path['unmatched_val_path'], "r") as annotation:
                lines = incorrect_log.readlines()
                annotations_val = annotation.readlines()
                annotations, exceptioned, incorrect = polarize_eval(
                    lines, annotations_val, verbose=2, parser="stanza"
                )

                with open(path['out_path'], "a") as correct:
                    for sent in annotations:
                        correct.write("%s\n" % sent["annotated"])

                with open(path['unmatched_log_path'], "w") as unmatched_log:
                    for sent in incorrect:
                        unmatched_log.write(sent[0])
                        unmatched_log.write("%s\n" % sent[1])
                        unmatched_log.write(sent[2])
                        if add_pos == 1:
                            unmatched_log.write("%s\n" % sent[3])
                        unmatched_log.write("\n")

                with open(path['exception_log_path'], "a") as except_log:
                    for sent in exceptioned:
                        except_log.write(sent[0])
                        except_log.write(sent[1])

                if add_pos == 1:
                    with open(path['pos_path'], "a") as postag:
                        for sent in annotations:
                            postag.write(sent["orig"])
                            postag.write("%s\n" % sent["postag"])


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset", help="The name of a working or evaluation dataset", type=str, default="gold")
    parser.add_argument(
        "--pos", help="Print part-of-speech tags also", type=int, default=0)
    parser.add_argument(
        "--mode", help="The pipeline mode: [1] polarize [2] eval", type=str, default="polarize")
    parser.add_argument(
        "--parser", help="The dependency parser used: [1] stanford [2] stanza", type=str, default="stanza")
    args = parser.parse_args()

    from polarization import polarize_eval, run_polarize_pipeline
    polarize_dataset(args.dataset, args.pos, args.mode, args.parser)
