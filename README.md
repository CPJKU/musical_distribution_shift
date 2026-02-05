# Musical Distribution Shift

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17467279.svg)](https://doi.org/10.5281/zenodo.17467279)

This repository contains the code and data used for our evaluation of Automatic (Piano) Music Transcription (AMT) systems under Musical Distribution Shift (MDS), as published in "[Sound and Music Biases in Deep Music Transcription Models: A Systematic Analysis](https://link.springer.com/article/10.1186/s13636-025-00428-z)".

The full MDS Dataset including audio files is available at [https://zenodo.org/records/17467279](https://zenodo.org/records/17467279).

## Contents

 - `data`: MIDI files for the ground truth and transcriptions produced by the evaluated AMT systems + metadata
 - `comp_metrics.py`: computes all relevant metrics using the pairs of MIDI files found in `data`
 - `results`: computed performance metrics stored as CSV files
 - `metrics`: code relevant to the computation of metrics
 - `figures`: code reproducing the figures from our paper based on the results CSVs stored in `results`
 - `results_ref`: reference results (exact numbers reported in the paper's figures)
 - `notebooks`: jupyter notebooks documenting the curation of the MDS dataset and a reproducibility check

## Setup

```bash
conda create -n mds python=3.9
conda activate mds
pip install -r requirements.txt
```

### Dependencies

 - python 3.9
 - mpteval 0.1.4
 - partitura 1.7.0

## Citing

If you build on this work in your research, please cite the relevant [journal article](https://link.springer.com/article/10.1186/s13636-025-00428-z):

```
@article{martak2025biases,
	author = {Luk{\'a}{\v{s}} Samuel Mart{\'a}k and Patricia Hu and Gerhard Widmer},
	title = {{Sound and Music Biases in Deep Music Transcription Models: A Systematic Analysis}},
	journal = {EURASIP Journal on Audio, Speech, and Music Processing},
	year = {2025},
	month = {Dec},
	day = {11},
	volume = {2026},
	number = {1},
	pages = {5},
	issn = {1687-4722},
	doi = {10.1186/s13636-025-00428-z},
	url = {https://doi.org/10.1186/s13636-025-00428-z},
	abstract = {Automatic Music Transcription (AMT) — the task of converting music audio into note representations — has seen rapid progress, driven largely by deep learning systems. Due to the limited availability of richly annotated music datasets, much of the progress in AMT has been concentrated on classical piano music, and even a few very specific datasets. Whether these systems can generalize effectively to other musical contexts remains an open question. Complementing recent studies on distribution shifts in sound (e.g., recording conditions), in this work we investigate the musical dimension—specifically, variations in genre, dynamics, and polyphony levels. To this end, we introduce the MDS corpus, comprising three distinct subsets — (1) genre, (2) random, and (3) MAEtest — to emulate different axes of distribution shift. We evaluate the performance of several state-of-the-art AMT systems on the MDS corpus using both traditional information-retrieval and musically informed performance metrics. Our extensive evaluation isolates and exposes varying degrees of performance degradation under specific distribution shifts. In particular, we measure a note-level F1 performance drop of 20 percentage points due to sound, and 14 due to genre. Generally, we find that dynamics estimation proves more vulnerable to musical variation than onset prediction. Musically informed evaluation metrics, particularly those capturing harmonic structure, help identify potential contributing factors. Furthermore, experiments with randomly generated, non-musical sequences reveal clear limitations in system performance under extreme musical distribution shifts. Altogether, these findings offer new evidence of the persistent impact of the corpus bias problem in deep AMT systems.},
	keywords = {Automatic Music Transcription, AMT, Musical Distribution Shift, MDS corpus, Corpus Bias, Deep Learning, Robustness Evaluation Benchmark, Out-of-Distribution Inference, Generalization, Polyphonic Piano Transcription}
}
```

Related publications:
 * 2025 EURASIP JASM paper "Sound and Music Biases in Deep Music Transcription Models: A Systematic Analysis" (arXiv [preprint](https://arxiv.org/abs/2512.14602))
 * 2024 IWSSPA workshop paper "Quantifying the Corpus Bias Problem in Automatic Music Transcription Systems" (arXiv [preprint](https://arxiv.org/abs/2408.04737))

### Acknowledgments

This work is supported by the European Research Council (ERC) under the EU’s Horizon 2020 research and innovation programme, grant agreement No. 101019375 (["Whither Music?"](https://www.jku.at/en/institute-of-computational-perception/research/projects/whither-music/)), by the LIT AI Lab, and by Johannes Kepler University Open Access Publishing Fund and the Federal State of Upper Austria.

## License

All software provided in this repository is subject to the [CRAPL license](CRAPL-LICENSE.txt).
