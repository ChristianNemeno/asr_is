import evaluate

_wer = evaluate.load("wer")
_cer = evaluate.load("cer")


def compute_metrics(predictions: list[str], references: list[str]) -> dict:
    wer = 100 * _wer.compute(predictions=predictions, references=references)
    cer = 100 * _cer.compute(predictions=predictions, references=references)
    return {"wer": round(wer, 2), "cer": round(cer, 2)}


def error_breakdown(prediction: str, reference: str) -> dict:
    from jiwer import process_words

    output = process_words(reference, prediction)
    return {
        "substitutions": output.substitutions,
        "deletions": output.deletions,
        "insertions": output.insertions,
        "hits": output.hits,
    }
