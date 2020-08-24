import logging
from timeit import default_timer as timer

import numpy as np

from opensfm import dataset
from opensfm import io
from opensfm import log
from opensfm import matching
from opensfm import pairs_selection
from opensfm.context import parallel_map
import os 


logger = logging.getLogger(__name__)


class Command:
    name = 'match_features'
    help = 'Match features between image pairs'

    def add_arguments(self, parser):
        parser.add_argument('dataset', help='dataset to process')
        # parser.add_argument('--localize', default=False, action="store_true")

    def run(self, args):
        data = dataset.DataSet(args.dataset)
        queryImages = None
        if(args.localize):
            localizeDir = os.path.join(args.dataset, "localize")
            print("Localization - creating matches: ")
            queryImages = [x for x in os.listdir(localizeDir) if x.endswith(".jpg")]
            [print(os.path.join(localizeDir, str(x))) for x in queryImages]
        
        else:
            queryImages = data.images()

        start = timer()
        pairs_matches, preport = matching.match_images(data, queryImages, data.images()) #2nd Argument, ref_images will be those images that are query. 
        matching.save_matches(data, queryImages, pairs_matches)
        end = timer()

        with open(data.profile_log(), 'a') as fout:
            fout.write('match_features: {0}\n'.format(end - start))
        self.write_report(data, preport, list(pairs_matches.keys()), end - start)

    def write_report(self, data, preport, pairs, wall_time):
        report = {
            "wall_time": wall_time,
            "num_pairs": len(pairs),
            "pairs": pairs,
        }
        report.update(preport)
        data.save_report(io.json_dumps(report), 'matches.json')
