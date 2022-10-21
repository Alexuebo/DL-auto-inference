from model.CT_Renal.nnunet.training.network_training import nnUNetTrainerV2
import matplotlib

matplotlib.use("agg")


class MYtrainer(nnUNetTrainerV2):
    def __init__(self, plans_file, fold, output_folder=None, dataset_directory=None, batch_dice=True, stage=None,
                 unpack_data=True, deterministic=True, previous_trainer="nnUNetTrainerV2", fp16=False):
        super().__init__(plans_file, fold, output_folder, dataset_directory,
                         batch_dice, stage, unpack_data, deterministic, fp16)
        self.init_args = (plans_file, fold, output_folder, dataset_directory, batch_dice, stage, unpack_data,
                          deterministic, previous_trainer, fp16)
        self.max_num_epochs = 200

    def initialize(self, training=True, force_load_plans=False):
        super(MYtrainer, self).initialize()
