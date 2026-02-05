import argparse
import os
import pandas as pd
from tqdm import tqdm
from utils import find_files, concatenate_results_genre, concatenate_results_random, concatenate_results_maetest
from metrics.standard_benchmark import compute_standard_benchmark_metrics as compute_ir_metrics
from metrics.musically_informed import compute_musically_informed_metrics as compute_mi_metrics


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Calculates the selected group of metrics based on pairs of ground truth and transcription MIDI files.')
    parser.add_argument(
        '--path_mds', type=str, default=os.path.dirname(os.path.abspath(__file__)),
        help='Path to the MDS repo with data and results directories.')
    parser.add_argument(
        '--which', type=str, default='both', choices=['IR', 'MI', 'both'],
        help='Which set of metrics to compute: Information Retrieval (IR), Musically Informed (MI), or both.'
    )
    parser.add_argument(
        '--backend_ir', type=str, default='partitura', choices=['partitura', 'pretty_midi'],
        help='Which backend to use for MIDI processing: partitura or pretty_midi. Affects only the IR metrics.'
    )
    args = parser.parse_args()
    
    path_mds = args.path_mds
    if args.which == 'both':
        metrics_groups = ['IR', 'MI']
    else:
        metrics_groups = [args.which]
    if args.backend_ir == 'pretty_midi':
        print('Using pretty_midi backend to compute the IR metrics.')
        from metrics.standard_benchmark import compute_standard_benchmark_metrics_pm as compute_ir_metrics
    metric_functions = {'IR': compute_ir_metrics, 'MI': compute_mi_metrics}

    for metrics_group in metrics_groups:
        compute_metrics = metric_functions[metrics_group]
        path_results = f'{path_mds}/results/{metrics_group}Ms'
        os.makedirs(path_results, exist_ok=True)

        midisets = ['1_genre', '2_random', '3_maetest']
        audiosets = ['dk'] # disklavier audio
        transcription_models = ['oaf', 'kong', 'T5', 'toyama', 'edwards']

        for midiset in midisets:
            path_true = f'{path_mds}/data/{midiset}'
            sorted_paths_true = find_files(path_true, '*.mid')
            total = len(sorted_paths_true)
            
            if midiset == '3_maetest':
                audiosets += ['mae'] # add maestro audio

            for audioset in audiosets:
                path_pred = f'{path_mds}/data/transcriptions/{midiset}_{audioset}'

                for model in transcription_models:
                    path_csv_out = f'{path_results}/{midiset}_{audioset}_{model}.csv'

                    df = pd.DataFrame()

                    sorted_paths_pred = find_files(path_pred, f'*_{model}.mid')
                    assert len(sorted_paths_true) == len(sorted_paths_pred), f'{len(sorted_paths_true)} != {len(sorted_paths_pred)}'
                    desc = f'{midiset}/{audioset}/{model}'
                    for true_MIDI, pred_MIDI in tqdm(zip(sorted_paths_true, sorted_paths_pred), desc=desc, total=total):
                        metrics = compute_metrics(true_MIDI, pred_MIDI)
                        df = df._append(metrics, ignore_index=True)
                    df.to_csv(path_csv_out, index=False)
        
        print('Concatenating results...')
        # concatenate all models results and save to a single csv file per midiset
        genre_all = f'{path_results}/1_genre_all.csv'
        concatenate_results_genre(genre_all, path_results=path_results)

        random_all = f'{path_results}/2_random_all.csv'
        concatenate_results_random(random_all, path_results=path_results)

        maetest_all = f'{path_results}/3_maetest_all.csv'
        concatenate_results_maetest(maetest_all, path_results=path_results)
