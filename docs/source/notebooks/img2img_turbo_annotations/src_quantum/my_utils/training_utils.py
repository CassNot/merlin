from types import SimpleNamespace
import os
import random
import argparse
import json
import torch
from PIL import Image
from torchvision import transforms
import torchvision.transforms.functional as F
import torch.nn.functional as Fu

from glob import glob
from datasets import load_dataset
import h5py
from transformers import AutoTokenizer
import pandas as pd
import numpy as np
from tqdm import tqdm

def parse_args_paired_training(input_args=None):
    """
    Parses command-line arguments used for configuring an paired session (pix2pix-Turbo).
    This function sets up an argument parser to handle various training options.

    Returns:
    argparse.Namespace: The parsed command-line arguments.
   """
    parser = argparse.ArgumentParser()
    # args for the loss function
    parser.add_argument("--gan_disc_type", default="vagan_clip")
    parser.add_argument("--gan_loss_type", default="multilevel_sigmoid_s")
    parser.add_argument("--lambda_gan", default=0.5, type=float)
    parser.add_argument("--lambda_lpips", default=5, type=float)
    parser.add_argument("--lambda_l2", default=1.0, type=float)
    parser.add_argument("--lambda_clipsim", default=5.0, type=float)

    # dataset options
    parser.add_argument("--dataset_folder", required=True, type=str)
    parser.add_argument("--train_image_prep", default="resized_crop_512", type=str)
    parser.add_argument("--test_image_prep", default="resized_crop_512", type=str)

    # validation eval args
    parser.add_argument("--eval_freq", default=100, type=int)
    parser.add_argument("--track_val_fid", default=False, action="store_true")
    parser.add_argument("--num_samples_eval", type=int, default=100, help="Number of samples to use for all evaluation")

    parser.add_argument("--viz_freq", type=int, default=100, help="Frequency of visualizing the outputs.")
    parser.add_argument("--tracker_project_name", type=str, default="train_pix2pix_turbo", help="The name of the wandb project to log to.")

    # details about the model architecture
    parser.add_argument("--pretrained_model_name_or_path")
    parser.add_argument("--revision", type=str, default=None,)
    parser.add_argument("--variant", type=str, default=None,)
    parser.add_argument("--tokenizer_name", type=str, default=None)
    parser.add_argument("--lora_rank_unet", default=8, type=int)
    parser.add_argument("--lora_rank_vae", default=4, type=int)

    # training details
    parser.add_argument("--output_dir", default = None)
    parser.add_argument("--cache_dir", default=None,)
    parser.add_argument("--seed", type=int, default=None, help="A seed for reproducible training.")
    parser.add_argument("--resolution", type=int, default=512,)
    parser.add_argument("--train_batch_size", type=int, default=4, help="Batch size (per device) for the training dataloader.")
    parser.add_argument("--num_training_epochs", type=int, default=10)
    parser.add_argument("--max_train_steps", type=int, default=10_000,)
    parser.add_argument("--checkpointing_steps", type=int, default=500,)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=1, help="Number of updates steps to accumulate before performing a backward/update pass.",)
    parser.add_argument("--gradient_checkpointing", action="store_true",)
    parser.add_argument("--learning_rate", type=float, default=5e-6)
    parser.add_argument("--lr_scheduler", type=str, default="constant",
        help=(
            'The scheduler type to use. Choose between ["linear", "cosine", "cosine_with_restarts", "polynomial",'
            ' "constant", "constant_with_warmup"]'
        ),
    )
    parser.add_argument("--lr_warmup_steps", type=int, default=500, help="Number of steps for the warmup in the lr scheduler.")
    parser.add_argument("--lr_num_cycles", type=int, default=1,
        help="Number of hard resets of the lr in cosine_with_restarts scheduler.",
    )
    parser.add_argument("--lr_power", type=float, default=1.0, help="Power factor of the polynomial scheduler.")

    parser.add_argument("--dataloader_num_workers", type=int, default=0,)
    parser.add_argument("--adam_beta1", type=float, default=0.9, help="The beta1 parameter for the Adam optimizer.")
    parser.add_argument("--adam_beta2", type=float, default=0.999, help="The beta2 parameter for the Adam optimizer.")
    parser.add_argument("--adam_weight_decay", type=float, default=1e-2, help="Weight decay to use.")
    parser.add_argument("--adam_epsilon", type=float, default=1e-08, help="Epsilon value for the Adam optimizer")
    parser.add_argument("--max_grad_norm", default=1.0, type=float, help="Max gradient norm.")
    parser.add_argument("--allow_tf32", action="store_true",
        help=(
            "Whether or not to allow TF32 on Ampere GPUs. Can be used to speed up training. For more information, see"
            " https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices"
        ),
    )
    parser.add_argument("--report_to", type=str, default="wandb",
        help=(
            'The integration to report the results and logs to. Supported platforms are `"tensorboard"`'
            ' (default), `"wandb"` and `"comet_ml"`. Use `"all"` to report to all integrations.'
        ),
    )
    parser.add_argument("--mixed_precision", type=str, default=None, choices=["no", "fp16", "bf16"],)
    parser.add_argument("--enable_xformers_memory_efficient_attention", action="store_true", help="Whether or not to use xformers.")
    parser.add_argument("--set_grads_to_none", action="store_true",)

    if input_args is not None:
        args = parser.parse_args(input_args)
    else:
        args = parser.parse_args()

    return args


def parse_args_unpaired_training():
    """
    Parses command-line arguments used for configuring an unpaired session (CycleGAN-Turbo).
    This function sets up an argument parser to handle various training options.

    Returns:
    argparse.Namespace: The parsed command-line arguments.
   """

    parser = argparse.ArgumentParser(description="Simple example of a ControlNet training script.")

    # fixed random seed
    parser.add_argument("--seed", type=int, default=42, help="A seed for reproducible training.")

    # args for the loss function
    parser.add_argument("--gan_disc_type", default="vagan_clip")
    parser.add_argument("--gan_loss_type", default="multilevel_sigmoid")
    parser.add_argument("--lambda_gan", default=0.5, type=float)
    parser.add_argument("--lambda_idt", default=1, type=float)
    parser.add_argument("--lambda_cycle", default=1, type=float)
    parser.add_argument("--lambda_cycle_lpips", default=10.0, type=float)
    parser.add_argument("--lambda_idt_lpips", default=1.0, type=float)

    # args for dataset and dataloader options
    parser.add_argument("--dataset_folder", required=True, type=str)
    parser.add_argument("--train_img_prep", required=True)
    parser.add_argument("--val_img_prep", required=True)
    parser.add_argument("--dataloader_num_workers", type=int, default=0)
    parser.add_argument("--train_batch_size", type=int, default=4, help="Batch size (per device) for the training dataloader.")
    parser.add_argument("--max_train_epochs", type=int, default=100)
    parser.add_argument("--max_train_steps", type=int, default=None)

    # args for the model
    parser.add_argument("--pretrained_model_name_or_path", default="stabilityai/sd-turbo")
    parser.add_argument("--revision", default=None, type=str)
    parser.add_argument("--variant", default=None, type=str)
    parser.add_argument("--lora_rank_unet", default=128, type=int)
    parser.add_argument("--lora_rank_vae", default=4, type=int)

    # args for validation and logging
    parser.add_argument("--viz_freq", type=int, default=20)
    parser.add_argument("--output_dir", type=str, default = 'a' )#, required=True)
    parser.add_argument("--validation_steps", type=int, default=500,)
    parser.add_argument("--validation_num_images", type=int, default=-1, help="Number of images to use for validation. -1 to use all images.")
    parser.add_argument("--checkpointing_steps", type=int, default=1000)

    # args for the optimization options
    parser.add_argument("--learning_rate", type=float, default=5e-6,)
    parser.add_argument("--adam_beta1", type=float, default=0.9, help="The beta1 parameter for the Adam optimizer.")
    parser.add_argument("--adam_beta2", type=float, default=0.999, help="The beta2 parameter for the Adam optimizer.")
    parser.add_argument("--adam_weight_decay", type=float, default=1e-2, help="Weight decay to use.")
    parser.add_argument("--adam_epsilon", type=float, default=1e-08, help="Epsilon value for the Adam optimizer")
    parser.add_argument("--max_grad_norm", default=10.0, type=float, help="Max gradient norm.")
    parser.add_argument("--lr_scheduler", type=str, default="constant", help=(
        'The scheduler type to use. Choose between ["linear", "cosine", "cosine_with_restarts", "polynomial",'
        ' "constant", "constant_with_warmup"]'
        ),
    )
    parser.add_argument("--lr_warmup_steps", type=int, default=500, help="Number of steps for the warmup in the lr scheduler.")
    parser.add_argument("--lr_num_cycles", type=int, default=1, help="Number of hard resets of the lr in cosine_with_restarts scheduler.",)
    parser.add_argument("--lr_power", type=float, default=1.0, help="Power factor of the polynomial scheduler.")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=1)

    # memory saving options
    parser.add_argument("--allow_tf32", action="store_true",
        help=(
            "Whether or not to allow TF32 on Ampere GPUs. Can be used to speed up training. For more information, see"
            " https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices"
        ),
    )
    parser.add_argument("--gradient_checkpointing", action="store_true",
        help="Whether or not to use gradient checkpointing to save memory at the expense of slower backward pass.")
    parser.add_argument("--enable_xformers_memory_efficient_attention", action="store_true", help="Whether or not to use xformers.")


    # dynamic conditional quantum embeddings with the VAE frozen
    parser.add_argument("--quantum_dynamic",type=bool, default = False,
                        help="Define if quantum embeddings of the fake image embeddings are computed. Set quantum_training to True")
    parser.add_argument("--cl_comp", type=bool, default=False,
                        help="Define if we use an initialized classical model for experiment comparison")
    parser.add_argument("--quantum_start_path", type=str,
                        default="/training-models/all_outputs/exp-84/checkpoints/model_251.pkl",
                        help="Path to pretrained VAE encoder")
    parser.add_argument("--quantum_dims", type=tuple, default=(4, 16, 16), help="Dimensions of the quantum encoder")
    parser.add_argument("--quantum_processes", type=int, default=2,
                        help="Number of threads to use for the Boson Sampler")
    parser.add_argument("--training_images", type = float, default = 1., help="Part of the training images to be used")
    args = parser.parse_args()
    return args


def parse_args_training():
    """
    Parses command-line arguments used for configuring an unpaired session (CycleGAN-Turbo).
    This function sets up an argument parser to handle various training options.

    Returns:
    argparse.Namespace: The parsed command-line arguments.
   """

    
    args = {}
    # fixed random seed
    args["seed"] = 42
 # args for the loss function
    args["gan_disc_type"] = "vagan_clip"
    args["gan_loss_type"] = "multilevel_sigmoid"
    args["lambda_gan"] = 0.5
    args["lambda_idt"] = 1
    args["lambda_cycle"] = 1
    args["lambda_cycle_lpips"] = 10.0
    args["lambda_idt_lpips"] = 1.0

    # args for dataset and dataloader options
    args["dataset_folder"] = 'img2img_turbo_annotations/dataset'
    args["train_img_prep"] = 'resize_128'                                                                  
    args["val_img_prep"] = 'resize_128'                                                                   
    args["dataloader_num_workers"] = 0                                                    
    args["train_batch_size"] = 2                                                                                                                    
    args["max_train_epochs"] = 20                                                       
    args["max_train_steps"] = 20                                                                                                                                                                                           
                          
    args["revision"] = None                                                               
    args["variant"] = None                                                              
    args["lora_rank_unet"] = 128                                                        
    args["lora_rank_vae"] = 4                                                                                                                                                                                  
    # args for validation and logging                                                                                       
    args["viz_freq"] = 20 
    args["output_dir"] = 'img2img_turbo_annotations/outputs'
    args["validation_steps"] = 50              
    args["validation_num_images"] = -1
    args["checkpointing_steps"] = 1000

    # args for the optimization options
    args["learning_rate"] = 1e-5
    args["adam_beta1"] = 0.9
    args["adam_beta2"] = 0.999
    args["adam_weight_decay"] = 1e-2
    args["adam_epsilon"] = 1e-08        
    args["max_grad_norm"] = 10.0
    args["lr_scheduler"] = "constant"                                                                                                                     
    args["lr_warmup_steps"] = 500
    args["lr_num_cycles"] = 1                                                                                                        
    args["lr_power"] = 1.0       
    args["gradient_accumulation_steps"] = 1                                                                                                                                                                    # memory saving options
    args["allow_tf32"] = False
    args["gradient_checkpointing"] = False
    args["enable_xformers_memory_efficient_attention"] = True


    # dynamic conditional quantum embeddings with the VAE frozen
    args["quantum_dynamic"] = True
    args["cl_comp"] = False
    args["pretrained_model_path"] = "model_251.pkl"
    args["quantum_dims"] = (4, 16, 16)
    args["quantum_processes"] = 2
    args["training_images"] = 1.
    return SimpleNamespace(**args)


def build_transform(image_prep):
    """
    Constructs a transformation pipeline based on the specified image preparation method.

    Parameters:
    - image_prep (str): A string describing the desired image preparation

    Returns:
    - torchvision.transforms.Compose: A composable sequence of transformations to be applied to images.
    """
    if image_prep == "resized_crop_512":
        T = transforms.Compose([
            transforms.Resize(512, interpolation=transforms.InterpolationMode.LANCZOS),
            transforms.CenterCrop(512),
        ])
    elif image_prep == "resize_286_randomcrop_256x256_hflip":
        T = transforms.Compose([
            transforms.Resize((286, 286), interpolation=Image.LANCZOS),
            transforms.RandomCrop((256, 256)),
            transforms.RandomHorizontalFlip(),
        ])
    elif image_prep in ["resize_256", "resize_256x256"]:
        T = transforms.Compose([
            transforms.Resize((256, 256), interpolation=Image.LANCZOS)
        ])
    elif image_prep in ["resize_512", "resize_512x512"]:
        T = transforms.Compose([
            transforms.Resize((512, 512), interpolation=Image.LANCZOS)
        ])
    elif image_prep in ["resize_128", "resize_128x128"]:
        T = transforms.Compose([
            transforms.Resize((128, 128), interpolation=Image.LANCZOS)
        ])
    
    elif image_prep in ["resize_64", "resize_64x64"]:
        T = transforms.Compose([
            transforms.Resize((64, 64), interpolation=Image.LANCZOS)
        ])
    elif image_prep == "no_resize":
        T = transforms.Lambda(lambda x: x)
    return T


def load_small_dataset(dataset_name, output_dir):
    print("loading small dataset")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    dataset = load_dataset(dataset_name)
    for split_name, split_data in dataset.items():
        split_dir = os.path.join(output_dir, split_name)
        os.makedirs(split_dir, exist_ok=True)

        for i, example in enumerate(tqdm(split_data, desc=f"Saving {split_name}")):
            image: Image.Image = example["image"]
            save_path = os.path.join(split_dir, f"{i:05d}.jpg")
            image.save(save_path)

    text_a = "Driving in the night"
    file_path = os.path.join(output_dir, "fixed_prompt_a.txt")
    with open(file_path, 'w') as file:
        file.write(text_a)
    text_b = "Driving in the day"
    file_path = os.path.join(output_dir, "fixed_prompt_b.txt")
    with open(file_path, 'w') as file:
        file.write(text_b)
    return "Dataset Loaded"

class PairedDataset(torch.utils.data.Dataset):
    def __init__(self, dataset_folder, split, image_prep, tokenizer):
        """
        Itialize the paired dataset object for loading and transforming paired data samples
        from specified dataset folders.

        This constructor sets up the paths to input and output folders based on the specified 'split',
        loads the captions (or prompts) for the input images, and prepares the transformations and
        tokenizer to be applied on the data.

        Parameters:
        - dataset_folder (str): The root folder containing the dataset, expected to include
                                sub-folders for different splits (e.g., 'train_A', 'train_B').
        - split (str): The dataset split to use ('train' or 'test'), used to select the appropriate
                       sub-folders and caption files within the dataset folder.
        - image_prep (str): The image preprocessing transformation to apply to each image.
        - tokenizer: The tokenizer used for tokenizing the captions (or prompts).
        """
        super().__init__()
        if split == "train":
            self.input_folder = os.path.join(dataset_folder, "train_A")
            self.output_folder = os.path.join(dataset_folder, "train_B")
            captions = os.path.join(dataset_folder, "train_prompts.json")
        elif split == "test":
            self.input_folder = os.path.join(dataset_folder, "test_A")
            self.output_folder = os.path.join(dataset_folder, "test_B")
            captions = os.path.join(dataset_folder, "test_prompts.json")
        with open(captions, "r") as f:
            self.captions = json.load(f)
        self.img_names = list(self.captions.keys())
        self.T = build_transform(image_prep)
        self.tokenizer = tokenizer

    def __len__(self):
        """
        Returns:
        int: The total number of items in the dataset.
        """
        return len(self.captions)

    def __getitem__(self, idx):
        """
        Retrieves a dataset item given its index. Each item consists of an input image, 
        its corresponding output image, the captions associated with the input image, 
        and the tokenized form of this caption.

        This method performs the necessary preprocessing on both the input and output images, 
        including scaling and normalization, as well as tokenizing the caption using a provided tokenizer.

        Parameters:
        - idx (int): The index of the item to retrieve.

        Returns:
        dict: A dictionary containing the following key-value pairs:
            - "output_pixel_values": a tensor of the preprocessed output image with pixel values 
            scaled to [-1, 1].
            - "conditioning_pixel_values": a tensor of the preprocessed input image with pixel values 
            scaled to [0, 1].
            - "caption": the text caption.
            - "input_ids": a tensor of the tokenized caption.

        Note:
        The actual preprocessing steps (scaling and normalization) for images are defined externally 
        and passed to this class through the `image_prep` parameter during initialization. The 
        tokenization process relies on the `tokenizer` also provided at initialization, which 
        should be compatible with the models intended to be used with this dataset.
        """
        img_name = self.img_names[idx]
        input_img = Image.open(os.path.join(self.input_folder, img_name))
        output_img = Image.open(os.path.join(self.output_folder, img_name))
        caption = self.captions[img_name]

        # input images scaled to 0,1
        img_t = self.T(input_img)
        img_t = F.to_tensor(img_t)
        # output images scaled to -1,1
        output_t = self.T(output_img)
        output_t = F.to_tensor(output_t)
        output_t = F.normalize(output_t, mean=[0.5], std=[0.5])

        input_ids = self.tokenizer(
            caption, max_length=self.tokenizer.model_max_length,
            padding="max_length", truncation=True, return_tensors="pt"
        ).input_ids

        return {
            "output_pixel_values": output_t,
            "conditioning_pixel_values": img_t,
            "caption": caption,
            "input_ids": input_ids,
        }


class UnpairedDataset(torch.utils.data.Dataset):
    def __init__(self, dataset_folder, split, image_prep, tokenizer, part = 1):
        """
        A dataset class for loading unpaired data samples from two distinct domains (source and target),
        typically used in unsupervised learning tasks like image-to-image translation.

        The class supports loading images from specified dataset folders, applying predefined image
        preprocessing transformations, and utilizing fixed textual prompts (captions) for each domain,
        tokenized using a provided tokenizer.

        Parameters:
        - dataset_folder (str): Base directory of the dataset containing subdirectories (train_A, train_B, test_A, test_B)
        - split (str): Indicates the dataset split to use. Expected values are 'train' or 'test'.
        - image_prep (str): he image preprocessing transformation to apply to each image.
        - tokenizer: The tokenizer used for tokenizing the captions (or prompts).
        """
        super().__init__()
        print(f"Dataset folder = {dataset_folder}")
        if split == "train":
            self.source_folder = os.path.join(dataset_folder, "train_a")
            self.target_folder = os.path.join(dataset_folder, "train_b")
        elif split == "test":
            self.source_folder = os.path.join(dataset_folder, "test_a")
            self.target_folder = os.path.join(dataset_folder, "test_b")
        self.tokenizer = tokenizer
        with open(os.path.join(dataset_folder, "fixed_prompt_a.txt"), "r") as f:
            self.fixed_caption_src = f.read().strip()
            self.input_ids_src = self.tokenizer(
                self.fixed_caption_src, max_length=self.tokenizer.model_max_length,
                padding="max_length", truncation=True, return_tensors="pt"
            ).input_ids

        with open(os.path.join(dataset_folder, "fixed_prompt_b.txt"), "r") as f:
            self.fixed_caption_tgt = f.read().strip()
            self.input_ids_tgt = self.tokenizer(
                self.fixed_caption_tgt, max_length=self.tokenizer.model_max_length,
                padding="max_length", truncation=True, return_tensors="pt"
            ).input_ids
        # find all images in the source and target folders with all IMG extensions
        self.l_imgs_src = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif"]:
            self.l_imgs_src.extend(glob(os.path.join(self.source_folder, ext)))
        self.l_imgs_tgt = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif"]:
            self.l_imgs_tgt.extend(glob(os.path.join(self.target_folder, ext)))
        self.T = build_transform(image_prep)
        self.part = part

    def __len__(self):
        """
        Returns:
        int: The total number of items in the dataset to be used (part).
        """
        return int((len(self.l_imgs_src) + len(self.l_imgs_tgt))*self.part)

    def __getitem__(self, index):
        """
        Fetches a pair of unaligned images from the source and target domains along with their 
        corresponding tokenized captions.

        For the source domain, if the requested index is within the range of available images,
        the specific image at that index is chosen. If the index exceeds the number of source
        images, a random source image is selected. For the target domain,
        an image is always randomly selected, irrespective of the index, to maintain the 
        unpaired nature of the dataset.

        Both images are preprocessed according to the specified image transformation `T`, and normalized.
        The fixed captions for both domains
        are included along with their tokenized forms.

        Parameters:
        - index (int): The index of the source image to retrieve.

        Returns:
        dict: A dictionary containing processed data for a single training example, with the following keys:
            - "pixel_values_src": The processed source image
            - "pixel_values_tgt": The processed target image
            - "caption_src": The fixed caption of the source domain.
            - "caption_tgt": The fixed caption of the target domain.
            - "input_ids_src": The source domain's fixed caption tokenized.
            - "input_ids_tgt": The target domain's fixed caption tokenized.
        """
        if index < len(self.l_imgs_src):
            img_path_src = self.l_imgs_src[index]
        else:
            img_path_src = random.choice(self.l_imgs_src)
        img_path_tgt = random.choice(self.l_imgs_tgt)
        img_pil_src = Image.open(img_path_src).convert("RGB")
        img_pil_tgt = Image.open(img_path_tgt).convert("RGB")
        img_t_src = F.to_tensor(self.T(img_pil_src))
        img_t_tgt = F.to_tensor(self.T(img_pil_tgt))
        img_t_src = F.normalize(img_t_src, mean=[0.5], std=[0.5])
        img_t_tgt = F.normalize(img_t_tgt, mean=[0.5], std=[0.5])
        return {
            "pixel_values_src": img_t_src,
            "pixel_values_tgt": img_t_tgt,
            "caption_src": self.fixed_caption_src,
            "caption_tgt": self.fixed_caption_tgt,
            "input_ids_src": self.input_ids_src,
            "input_ids_tgt": self.input_ids_tgt,
            "path_src":img_path_src,
            "path_tgt":img_path_tgt,
        }


def read_embeddings_from_h5(path):
    h5_A = os.path.join(path,"train_A.h5")
    h5_B = os.path.join(path,"train_B.h5")

    # get list of quantum embeddings from training A
    with h5py.File(h5_A, "r") as f:
        q_embs_A = list(f.keys())
        print(f"Number of quantum embeddings for A = {len(q_embs_A)}")

    # get list of quantum embeddings from training B
    with h5py.File(h5_B, "r") as f:
        q_embs_B = list(f.keys())
        print(f"Number of quantum embeddings for B = {len(q_embs_B)}")
    return q_embs_A, q_embs_B

def write_embeddings_to_csv(embsA,embsB, output_dir):
    embs_A,embs_B = embsA.copy(),embsB.copy()
    # complete by nan uf not of same size
    max_len = max(len(embs_A),len(embs_B))
    if len(embs_A)<len(embs_B):
        embs_A += [np.nan]*(max_len-len(embs_A))
    elif len(embs_A)>=len(embs_B):
        embs_B += [np.nan]*(max_len-len(embs_B))
    
    df = pd.DataFrame({"q_embs_A": embs_A, "q_embs_B": embs_B})
    df.to_csv(os.path.join(output_dir,"q_embs_used.csv"),index = False)
    print("-- embeddings saved to csv --")

def read_from_emb16(tensor_path):
    with open(tensor_path, 'rb') as f:
        q_emb = f.read()
    q_emb = np.frombuffer(q_emb, dtype=np.float32).reshape(3,16,16)
    return torch.tensor(q_emb)

def read_from_emb32(tensor_path):
    tensor = torch.load(tensor_path)
    return tensor

def image_fail(list_f, fold, path):
    img_name = os.path.basename(path)
    fail = False
    if [fold, img_name] in list_f:
        fail = True
    return fail

class UnpairedDataset_Quantum(torch.utils.data.Dataset):
    def __init__(self, dataset_folder, split, image_prep, tokenizer, q_emb_path, output_dir, annotations_path, annotations_on_image = False, q_fail = True, partial = False):
        """
        A dataset class for loading unpaired data samples from two distinct domains (source and target),
        typically used in unsupervised learning tasks like image-to-image translation.

        This dataset class also provides the quantum_embeddings using the quantum_encoder, and the data samples
        as inputs.

        The class supports loading images from specified dataset folders, applying predefined image
        preprocessing transformations, and utilizing fixed textual prompts (captions) for each domain,
        tokenized using a provided tokenizer.

        Parameters:
        - dataset_folder (str): Base directory of the dataset containing subdirectories (train_A, train_B, test_A, test_B)
        - split (str): Indicates the dataset split to use. Expected values are 'train' or 'test'.
        - image_prep (str): he image preprocessing transformation to apply to each image.
        - tokenizer: The tokenizer used for tokenizing the captions (or prompts).
        - TO DO !!! Quantum encoder
        """
        super().__init__()
        if split == "train":
            self.source_folder = os.path.join(dataset_folder, "train_A")
            self.target_folder = os.path.join(dataset_folder, "train_B")
        elif split == "test":
            self.source_folder = os.path.join(dataset_folder, "test_A")
            self.target_folder = os.path.join(dataset_folder, "test_B")
        self.tokenizer = tokenizer
        with open(os.path.join(dataset_folder, "fixed_prompt_a.txt"), "r") as f:
            self.fixed_caption_src = f.read().strip()
            self.input_ids_src = self.tokenizer(
                self.fixed_caption_src, max_length=self.tokenizer.model_max_length,
                padding="max_length", truncation=True, return_tensors="pt"
            ).input_ids

        with open(os.path.join(dataset_folder, "fixed_prompt_b.txt"), "r") as f:
            self.fixed_caption_tgt = f.read().strip()
            self.input_ids_tgt = self.tokenizer(
                self.fixed_caption_tgt, max_length=self.tokenizer.model_max_length,
                padding="max_length", truncation=True, return_tensors="pt"
            ).input_ids
        # find all images in the source and target folders with all IMG extensions
        self.l_imgs_src = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif"]:
            self.l_imgs_src.extend(glob(os.path.join(self.source_folder, ext)))
        self.l_imgs_tgt = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif"]:
            self.l_imgs_tgt.extend(glob(os.path.join(self.target_folder, ext)))
        self.T = build_transform(image_prep)

        if not annotations_on_image:
            self.q_emb_path = q_emb_path
            self.q_embs_A, self.q_embs_B = read_embeddings_from_h5(self.q_emb_path)
            # write to csv the images used for this training
            write_embeddings_to_csv(self.q_embs_A,self.q_embs_B,output_dir)
        self.annotations_on_images = annotations_on_image
        self.annotations_path = annotations_path
        self.q_fail = q_fail
        if self.q_fail:
            df = pd.read_csv("/mnt/bmw-challenge-volume/home/jupyter-pemeriau/q_embs/fails_empty.csv")
            self.list_empty = df.values.tolist()
        self.partial = partial
        
        

    def __len__(self):
        """
        Returns:
        int: The total number of items in the dataset.
        """
        if self.annotations_on_images:
            l = len(self.l_imgs_src) + len(self.l_imgs_tgt)
        else:
            l = len(self.q_embs_A) + len(self.q_embs_B)
        if self.partial:
            l = int(0.25*l)
        return l

    def __getitem__(self, index):
        """
        Fetches a pair of unaligned images from the source and target domains along with their 
        corresponding tokenized captions.

        For the source domain, if the requested index is within the range of available images,
        the specific image at that index is chosen. If the index exceeds the number of source
        images, a random source image is selected. For the target domain,
        an image is always randomly selected, irrespective of the index, to maintain the 
        unpaired nature of the dataset.

        Both images are preprocessed according to the specified image transformation `T`, and normalized.
        The fixed captions for both domains
        are included along with their tokenized forms.

        Parameters:
        - index (int): The index of the source image to retrieve.

        Returns:
        dict: A dictionary containing processed data for a single training example, with the following keys:
            - "pixel_values_src": The processed source image
            - "pixel_values_tgt": The processed target image
            - "caption_src": The fixed caption of the source domain.
            - "caption_tgt": The fixed caption of the target domain.
            - "input_ids_src": The source domain's fixed caption tokenized.
            - "input_ids_tgt": The target domain's fixed caption tokenized.
        """
        # quantum embeddings at the entry of the UNet
        if not self.annotations_on_images:
            # get the names of the images using the quantum embeddings
            if index < len(self.q_embs_A):
                src_name = self.q_embs_A[index]
            else:
                src_name = random.choice(self.q_embs_A)

            tgt_name = random.choice(self.q_embs_B)
            #print(f"src_name = {src_name} and tgt_name = {tgt_name}")
            # get images path
            img_path_src = os.path.join(self.source_folder,src_name)
            img_path_tgt = os.path.join(self.target_folder, tgt_name)

            # get quantum inputs 
            with h5py.File(os.path.join(self.q_emb_path,"train_A.h5"),"r") as f:
                if src_name in f:
                    qt_t_src = f[src_name]
                    qt_t_src = torch.tensor(qt_t_src)
                else:
                    print(f"{src_name} not found in q_embs_A")
            
            with h5py.File(os.path.join(self.q_emb_path,"train_B.h5"),"r") as f:
                if tgt_name in f:
                    qt_t_tgt = f[tgt_name]
                    qt_t_tgt = torch.tensor(qt_t_tgt)
                else:
                    print(f"{tgt_name} not found in q_embs_B")

        # quantum annotations
        else:
            if not self.q_fail:
                if index < len(self.l_imgs_src):
                    img_path_src = self.l_imgs_src[index]
                else:
                    img_path_src = random.choice(self.l_imgs_src)
                img_path_tgt = random.choice(self.l_imgs_tgt)


            # handles corrupted emb32 training annotations
            if self.q_fail:
                if index < len(self.l_imgs_src):
                    img_path_src = self.l_imgs_src[index]
                    while image_fail(self.list_empty, 'trainA', os.path.basename(img_path_src)):
                        img_path_src = random.choice(self.l_imgs_src)
                else:
                    img_path_src = random.choice(self.l_imgs_src)
                    while image_fail(self.list_empty, 'trainA', os.path.basename(img_path_src)):
                        img_path_src = random.choice(self.l_imgs_src)
                print(f"Choose {img_path_src} empty? {image_fail(self.list_empty, 'trainA', os.path.basename(img_path_src))}")
                img_path_tgt = random.choice(self.l_imgs_tgt)
                while image_fail(self.list_empty, 'trainB', os.path.basename(img_path_tgt)):
                    img_path_tgt = random.choice(self.l_imgs_tgt)
                print(f"Choose {img_path_tgt} empty? {image_fail(self.list_empty, 'trainB', os.path.basename(img_path_tgt))}")
            # find quantum annotations using their name
            q_train_A = os.path.join(self.annotations_path,"A","trainA")
            q_train_B = os.path.join(self.annotations_path,"B","trainB")

            if not self.q_fail:
                qt_t_src_path = os.path.join(q_train_A,f"{os.path.basename(img_path_src[:-4])}.emb16")
                qt_t_tgt_path = os.path.join(q_train_B,f"{os.path.basename(img_path_tgt[:-4])}.emb16")
                qt_t_src = read_from_emb16(qt_t_src_path)
                qt_t_tgt = read_from_emb16(qt_t_tgt_path)
            else:
                qt_t_src_path = os.path.join(q_train_A,f"{os.path.basename(img_path_src[:-4])}.emb32")
                qt_t_tgt_path = os.path.join(q_train_B,f"{os.path.basename(img_path_tgt[:-4])}.emb32")
                qt_t_src = read_from_emb32(qt_t_src_path)
                qt_t_tgt = read_from_emb32(qt_t_tgt_path)

            # interpolate to 128
            qt_t_src = Fu.interpolate(qt_t_src.unsqueeze(0), size=(128, 128), mode='bilinear', align_corners=False)
            qt_t_tgt = Fu.interpolate(qt_t_tgt.unsqueeze(0), size=(128, 128), mode='bilinear', align_corners=False)
            qt_t_src = qt_t_src.squeeze(0)
            qt_t_tgt = qt_t_tgt.squeeze(0)
                    
                    
        # convert to PIL Image
        img_pil_src = Image.open(img_path_src).convert("RGB")
        img_pil_tgt = Image.open(img_path_tgt).convert("RGB")
        # classical input
        img_t_src = F.to_tensor(self.T(img_pil_src))
        img_t_tgt = F.to_tensor(self.T(img_pil_tgt))
        img_t_src = F.normalize(img_t_src, mean=[0.5], std=[0.5])
        img_t_tgt = F.normalize(img_t_tgt, mean=[0.5], std=[0.5])

        if self.annotations_on_images:
            # concatenate the images with their quantum annotations
            img_t_src = torch.cat((img_t_src, qt_t_src), dim=0)
            img_t_tgt = torch.cat((img_t_tgt,qt_t_tgt), dim=0)

            assert img_t_src.shape == (6,128,128)
            assert img_t_tgt.shape == (6,128,128)

        return {
            "pixel_values_src": img_t_src,
            "pixel_values_tgt": img_t_tgt,
            "quantic_values_src": qt_t_src,
            "quantic_values_tgt": qt_t_tgt,
            "caption_src": self.fixed_caption_src,
            "caption_tgt": self.fixed_caption_tgt,
            "input_ids_src": self.input_ids_src,
            "input_ids_tgt": self.input_ids_tgt,
        }

def get_next_id(filename="id_store.txt"):
    try:
        with open(filename, "r") as f:
            last_id = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        last_id = 0

    next_id = last_id + 1

    with open(filename, "w") as f:
        f.write(str(next_id))

    return next_id

# tokenizer = AutoTokenizer.from_pretrained("stabilityai/sd-turbo", subfolder="tokenizer", revision=None, use_fast=False,)
# dataset_train = UnpairedDataset_Quantum(dataset_folder="../data/dataset_full_scale/", image_prep="resize_128", split="train", tokenizer=tokenizer, 
#                                 q_emb_path = "/home/jupyter-pemeriau/q_embs/emb_128_dims_16_16_ckpt1001", 
#                                 output_dir = "/home/jupyter-pemeriau/q_embs/emb_128_dims_16_16_ckpt1001" )

# for k in range(len(dataset_train)):
#     a = dataset_train[k]
