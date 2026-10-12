# Actual pilot evidence

Values below are read from the saved metric JSONs. Scale 0–1; same held-out data within each task.

## tfidf

```json
{
  "subset_accuracy": 0.9700499168053245,
  "hamming_loss": 0.0037437603993344427,
  "threshold": 0.7500000000000002,
  "rows": 2404,
  "negative_rows": 2340,
  "micro": {
    "precision": 0.43548387096774194,
    "recall": 0.421875,
    "f1": 0.42857142857142855
  },
  "macro": {
    "precision": 0.41875,
    "recall": 0.3857007575757576,
    "f1": 0.3852564102564102
  },
  "weighted": {
    "precision": 0.42500000000000004,
    "recall": 0.421875,
    "f1": 0.4088942307692308
  },
  "per_class": {
    "Governing Law": {
      "precision": 0.9,
      "recall": 0.9,
      "f1": 0.9,
      "support": 10,
      "average_precision": 0.9354545454545454,
      "confusion_matrix_tn_fp_fn_tp": [
        2393,
        1,
        1,
        9
      ]
    },
    "Non-Compete": {
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "support": 12,
      "average_precision": 0.26063324976571245,
      "confusion_matrix_tn_fp_fn_tp": [
        2385,
        7,
        12,
        0
      ]
    },
    "Exclusivity": {
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "support": 3,
      "average_precision": 0.07096266306792623,
      "confusion_matrix_tn_fp_fn_tp": [
        2401,
        0,
        3,
        0
      ]
    },
    "Anti-Assignment": {
      "precision": 0.5333333333333333,
      "recall": 0.7272727272727273,
      "f1": 0.6153846153846154,
      "support": 11,
      "average_precision": 0.7319979241031873,
      "confusion_matrix_tn_fp_fn_tp": [
        2386,
        7,
        3,
        8
      ]
    },
    "Termination For Convenience": {
      "precision": 0.5,
      "recall": 0.3333333333333333,
      "f1": 0.4,
      "support": 6,
      "average_precision": 0.2993160369776065,
      "confusion_matrix_tn_fp_fn_tp": [
        2396,
        2,
        4,
        2
      ]
    },
    "Cap On Liability": {
      "precision": 0.4166666666666667,
      "recall": 0.625,
      "f1": 0.5,
      "support": 8,
      "average_precision": 0.573408777213125,
      "confusion_matrix_tn_fp_fn_tp": [
        2389,
        7,
        3,
        5
      ]
    },
    "Audit Rights": {
      "precision": 1.0,
      "recall": 0.5,
      "f1": 0.6666666666666666,
      "support": 6,
      "average_precision": 0.7173525377229081,
      "confusion_matrix_tn_fp_fn_tp": [
        2398,
        0,
        3,
        3
      ]
    },
    "Post-Termination Services": {
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "support": 8,
      "average_precision": 0.04812819640930351,
      "confusion_matrix_tn_fp_fn_tp": [
        2385,
        11,
        8,
        0
      ]
    }
  },
  "inference_seconds": 0.11445029999958933,
  "test_document_count": 10,
  "dataset": "CUAD-derived eight-label segments; non-Indian contracts"
}
```

## legalbert

```json
{
  "subset_accuracy": 0.9721297836938436,
  "hamming_loss": 0.0036397670549084857,
  "threshold": 0.9000000000000002,
  "rows": 2404,
  "negative_rows": 2340,
  "micro": {
    "precision": 0.4642857142857143,
    "recall": 0.609375,
    "f1": 0.527027027027027
  },
  "macro": {
    "precision": 0.43539504477004476,
    "recall": 0.5646780303030303,
    "f1": 0.4470394736842106
  },
  "weighted": {
    "precision": 0.5017798318579569,
    "recall": 0.609375,
    "f1": 0.5091432416267943
  },
  "per_class": {
    "Governing Law": {
      "precision": 0.75,
      "recall": 0.9,
      "f1": 0.8181818181818182,
      "support": 10,
      "average_precision": 0.9384615384615383,
      "confusion_matrix_tn_fp_fn_tp": [
        2391,
        3,
        1,
        9
      ]
    },
    "Non-Compete": {
      "precision": 0.75,
      "recall": 0.5,
      "f1": 0.6,
      "support": 12,
      "average_precision": 0.5663686152792348,
      "confusion_matrix_tn_fp_fn_tp": [
        2390,
        2,
        6,
        6
      ]
    },
    "Exclusivity": {
      "precision": 0.125,
      "recall": 0.3333333333333333,
      "f1": 0.18181818181818182,
      "support": 3,
      "average_precision": 0.17824074074074073,
      "confusion_matrix_tn_fp_fn_tp": [
        2394,
        7,
        2,
        1
      ]
    },
    "Anti-Assignment": {
      "precision": 0.7142857142857143,
      "recall": 0.9090909090909091,
      "f1": 0.8,
      "support": 11,
      "average_precision": 0.65104574289823,
      "confusion_matrix_tn_fp_fn_tp": [
        2389,
        4,
        1,
        10
      ]
    },
    "Termination For Convenience": {
      "precision": 0.5,
      "recall": 0.16666666666666666,
      "f1": 0.25,
      "support": 6,
      "average_precision": 0.22544569260693112,
      "confusion_matrix_tn_fp_fn_tp": [
        2397,
        1,
        5,
        1
      ]
    },
    "Cap On Liability": {
      "precision": 0.25925925925925924,
      "recall": 0.875,
      "f1": 0.4,
      "support": 8,
      "average_precision": 0.635952287066246,
      "confusion_matrix_tn_fp_fn_tp": [
        2376,
        20,
        1,
        7
      ]
    },
    "Audit Rights": {
      "precision": 0.38461538461538464,
      "recall": 0.8333333333333334,
      "f1": 0.5263157894736842,
      "support": 6,
      "average_precision": 0.5285946492843044,
      "confusion_matrix_tn_fp_fn_tp": [
        2390,
        8,
        1,
        5
      ]
    },
    "Post-Termination Services": {
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "support": 8,
      "average_precision": 0.0698646118619547,
      "confusion_matrix_tn_fp_fn_tp": [
        2396,
        0,
        8,
        0
      ]
    }
  },
  "inference_seconds": 50.78700189999836,
  "test_document_count": 10,
  "dataset": "CUAD-derived eight-label segments; non-Indian contracts"
}
```

## extractive

```json
{
  "count": 20,
  "scale": "0 to 1",
  "aggregation": "arithmetic document mean of F1",
  "configuration": "rouge-score 0.1.2; default English alphanumeric tokenizer; Porter stemming; ROUGE-L (not Lsum); full reference",
  "rouge1": 0.21644663256410973,
  "rouge2": 0.12005882639430802,
  "rougeL": 0.14454874669094467,
  "inference_seconds": 3.587858099999721,
  "dataset": "IN-Abs English Indian Supreme Court judgments"
}
```

## t5

```json
{
  "count": 20,
  "scale": "0 to 1",
  "aggregation": "arithmetic document mean of F1",
  "configuration": "rouge-score 0.1.2; default English alphanumeric tokenizer; Porter stemming; ROUGE-L (not Lsum); full reference",
  "rouge1": 0.14946777228044272,
  "rouge2": 0.07973912636398864,
  "rougeL": 0.10456319851510354,
  "inference_seconds": 36.52435780000087,
  "dataset": "IN-Abs English Indian Supreme Court judgments"
}
```

## Qualitative review

IN-Abs test 3542: reference and original ending explicitly allow the appeals and drop contempt proceedings. T5 recounts the letter and deponents’ position but omits disposition and the reasoning on accepting an apology without a contempt finding. This is material omission; the output must not be read as the court’s final holding. The extractive summary retains the apology reasoning but also omits the final order and ends with the fragment “The High.” Sentence splitting at abbreviations/periods is a known source of incomplete units.

LEGAL-BERT: Cap On Liability has 20 false positives, one false negative and seven true positives. Post-Termination Services misses all eight positives. A threshold of 0.90 chosen on small validation support cannot be assumed to work across jurisdictions. The qualitative JSON includes actual passages for inspection. No expert-enforceability or hallucination-rate score was measured.

Always-zero subset accuracy = 2340 / 2404 = 0.9733777, macro F1 = 0. Both trained classifiers have lower subset accuracy but detect real positives. No significance or broad generalization claim is made from ten test contracts and twenty test judgments.