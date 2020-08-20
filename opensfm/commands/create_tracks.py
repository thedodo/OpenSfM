import logging
from timeit import default_timer as timer
import os 

from opensfm import dataset
from opensfm import io
from opensfm import tracking

logger = logging.getLogger(__name__)

class Command:
    name = 'create_tracks'
    help = "Link matches pair-wise matches into tracks"

    def add_arguments(self, parser):
        parser.add_argument('dataset', help='dataset to process')
        # parser.add_argument('localize', default=False, action="store_true")

    def run(self, args):
        data = dataset.DataSet(args.dataset)
        queryImages = None
        if(args.localize):
            localizeDir = os.path.join(args.dataset, "../localize")
            print("Localization - creating tracks: ")
            queryImages = [x for x in os.listdir(localizeDir)]
            [print(os.path.join(localizeDir, str(x))) for x in queryImages]
        
        else:
            queryImages = data.images()

        start = timer()
        features, colors = tracking.load_features(data, data.images()) #TODO: Just get those images for which matches have been computed. 
        features_end = timer()
        matches = tracking.load_matches(data, data.images()) #TODO: Just get those images for which matches have been computed.
        matches_end = timer()
        tracks_manager = tracking.create_tracks_manager(features, colors, matches,
                                                        data.config)
        tracks_end = timer()
        data.save_tracks_manager(tracks_manager)
        end = timer()

        with open(data.profile_log(), 'a') as fout:
            fout.write('create_tracks: {0}\n'.format(end - start))

        self.write_report(data,
                          tracks_manager,
                          features_end - start,
                          matches_end - features_end,
                          tracks_end - matches_end)

    def write_report(self, data, tracks_manager,
                     features_time, matches_time, tracks_time):
        view_graph = [(k[0], k[1], v) for k, v in tracks_manager.get_all_pairs_connectivity().items()]

        report = {
            "wall_times": {
                "load_features": features_time,
                "load_matches": matches_time,
                "compute_tracks": tracks_time,
            },
            "wall_time": features_time + matches_time + tracks_time,
            "num_images": tracks_manager.num_shots(),
            "num_tracks": tracks_manager.num_tracks(),
            "view_graph": view_graph
        }
        data.save_report(io.json_dumps(report), 'tracks.json')
