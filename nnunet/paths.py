#    Copyright 2020 Division of Medical Image Computing, German Cancer Research Center (DKFZ), Heidelberg, Germany
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from batchgenerators.utilities.file_and_folder_operations import maybe_mkdir_p, join

# do not modify these unless you know what you are doing
# my_output_identifier = "model"
default_plans_identifier = "nnUNetPlansv2.1"
default_data_identifier = 'nnUNetData_plans_v2.1'
default_trainer = "nnUNetTrainerV2"
default_cascade_trainer = "nnUNetTrainerV2CascadeFullRes"

# @todo 这里先这样写，到时候要改成用户输入的
base = "F:\\MedData\\kidney"
preprocessing_output_dir = "F:\\MedData\\kidney"
network_training_output_dir_base = "F:\\MedData\\kidney\\model"
# network_training_output_dir_base = "F:\\MedData\\Task004_Hippocampus"
nnUNet_raw_data = join(base, "")
nnUNet_cropped_data = join(base, "")
network_training_output_dir = join(network_training_output_dir_base)


# nnunet的文件类，自动推理的话每次都要修改路径的
# 创建path对象来修改路径,还有创建文件夹
class mypath:
    def __init__(self, b, p, n):
        self.base = b
        self.preprocessing_output_dir = p
        self.network_training_output_dir_base = n

    def makepathdirs(self):
        if base is not None:
            maybe_mkdir_p(nnUNet_raw_data)
            maybe_mkdir_p(nnUNet_cropped_data)

        if preprocessing_output_dir is not None:
            maybe_mkdir_p(preprocessing_output_dir)

        if network_training_output_dir_base is not None:
            maybe_mkdir_p(network_training_output_dir)
