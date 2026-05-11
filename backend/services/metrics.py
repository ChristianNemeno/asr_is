import evaluate

_wer = evaluate.load("wer")
_cer = evaluate.load("cer")


def compute_metrics(predictions: list[str], references: list[str]) -> dict:
    wer = 100 * _wer.compute(predictions=predictions, references=references)
    cer = 100 * _cer.compute(predictions=predictions, references=references)
    return {"wer": round(wer, 2), "cer": round(cer, 2)}


def error_breakdown(prediction: str, reference: str) -> dict:
    output = _process_words(reference, prediction)
    return {
        "substitutions": output.substitutions,
        "deletions": output.deletions,
        "insertions": output.insertions,
        "hits": output.hits,
    }


def word_alignments(reference: str, prediction: str) -> list[dict]:
    import difflib

    if not reference or not prediction:
        return []

    ref_words = reference.strip().split()
    hyp_words = prediction.strip().split()
    alignments = []

    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ref_words, hyp_words).get_opcodes():
        if tag == "equal":
            for k in range(i1, i2):
                alignments.append({"type": "hit", "ref_word": ref_words[k], "hyp_word": hyp_words[j1 + (k - i1)]})
        elif tag == "replace":
            n_ref = i2 - i1
            n_hyp = j2 - j1
            pair_count = min(n_ref, n_hyp)
            for k in range(pair_count):
                alignments.append({"type": "substitution", "ref_word": ref_words[i1 + k], "hyp_word": hyp_words[j1 + k]})
            for k in range(pair_count, n_ref):
                alignments.append({"type": "deletion", "ref_word": ref_words[i1 + k], "hyp_word": None})
            for k in range(pair_count, n_hyp):
                alignments.append({"type": "insertion", "ref_word": None, "hyp_word": hyp_words[j1 + k]})
        elif tag == "delete":
            for k in range(i1, i2):
                alignments.append({"type": "deletion", "ref_word": ref_words[k], "hyp_word": None})
        elif tag == "insert":
            for k in range(j1, j2):
                alignments.append({"type": "insertion", "ref_word": None, "hyp_word": hyp_words[k]})

    return alignments


def _process_words(reference: str, prediction: str):
    from jiwer import process_words
    return process_words(reference, prediction)
