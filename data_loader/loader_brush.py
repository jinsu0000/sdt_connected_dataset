import os
import random
import pickle
import torch
import numpy as np
from torch.utils.data import Dataset
from torchvision import transforms
from utils.util import normalize_xys_for_brush
from utils.logger import print_once


def delta_to_absolute(traj):
    abs_xy = np.cumsum(traj[:, :2], axis=0)
    rest = traj[:, 2:] if traj.shape[1] > 2 else None
    return np.concatenate([abs_xy, rest], axis=1) if rest is not None else abs_xy


class CharDict:
    def __init__(self, chars):
        self.char2id = {char: idx for idx, char in enumerate(sorted(list(chars)))}
        self.id2char = {idx: char for char, idx in self.char2id.items()}

    def find(self, char):
        return self.char2id[char]

    def get_char(self, idx):
        return self.id2char[idx]


transform_data = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize((64, 64)),
])


class BrushDataset(Dataset):
    def __init__(self, root_dir, is_train=True, split_ratio=0.8, seed=42, max_len=150, num_img=15):
        self.root_dir = os.path.join(root_dir, 'BRUSH')
        self.char_root_dir = os.path.join(self.root_dir, 'char_pickles')
        self.max_len = max_len
        self.samples = []
        self.num_img = num_img * 2 if is_train else num_img

        self.char_dict = CharDict(pickle.load(open(os.path.join(self.root_dir, 'character_dict.pkl'), 'rb')).keys())
        self.content_dict = pickle.load(open(os.path.join(self.root_dir, 'content_handwriting_img.pkl'), 'rb'))

        writer_files = [f for f in os.listdir(self.char_root_dir) if f.endswith('.pkl')]
        writer_files.sort()
        random.seed(seed)
        random.shuffle(writer_files)
        split_idx = int(len(writer_files) * split_ratio)
        writer_files = writer_files[:split_idx] if is_train else writer_files[split_idx:]

        for writer_file in writer_files:
            writer_id = os.path.splitext(writer_file)[0]
            with open(os.path.join(self.char_root_dir, writer_file), 'rb') as f:
                writer_dict = pickle.load(f)

            for char, sample_list in writer_dict.items():
                for sample in sample_list:
                    traj = sample['trajectory'].astype(np.float32)
                    traj = delta_to_absolute(traj)

                    if traj.shape[0] < 2:
                        continue
                    if np.allclose(traj[:, 0], traj[0, 0]) and np.allclose(traj[:, 1], traj[0, 1]):
                        continue

                    try:
                        traj = normalize_xys_for_brush(traj)
                    except Exception:
                        continue
                    traj[1:, :2] -= traj[:-1, :2]

                    eos_col = traj[:, 2] if traj.shape[1] >= 3 else np.zeros(traj.shape[0])
                    new_state = np.zeros((traj.shape[0], 3), dtype=np.float32)
                    new_state[:, 0] = 1
                    new_state[eos_col == 1, 0] = 0
                    new_state[eos_col == 1, 1] = 1
                    traj = np.concatenate([traj[:, :2], new_state], axis=1)

                    if char not in self.content_dict or char not in self.char_dict.char2id:
                        continue

                    content_img = self.content_dict[char]
                    content_img = transform_data(content_img)

                    self.samples.append({
                        'coords': torch.tensor(traj),
                        'char_img': content_img,
                        'writer_id': writer_id,
                        'character': char,
                    })

        print_once(f"BrushDataset Loaded {len(self.samples)} samples from {len(writer_files)} writers.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]

    def collate_fn_(self, batch_data):
        bs = len(batch_data)
        max_len = max([s['coords'].shape[0] for s in batch_data]) + 1
        output = {
            'coords': torch.zeros((bs, max_len, 5)),
            'coords_len': torch.zeros((bs,)),
            'character_id': torch.zeros((bs,), dtype=torch.long),
            'writer_id': torch.zeros((bs,)),
            'img_list': [],
            'char_img': [],
            'img_label': []
        }
        output['coords'][:, :, -1] = 1

        for i in range(bs):
            coords = batch_data[i]['coords']
            s = coords.shape[0]
            output['coords'][i, :s] = coords
            output['coords'][i, 0, :2] = 0
            output['coords'][i, :s, 2:] = coords[:, 2:]
            output['coords_len'][i] = s
            output['character_id'][i] = self.char_dict.find(batch_data[i]['character'])
            output['writer_id'][i] = 0

            all_candidates = [s for s in self.samples if s['writer_id'] == batch_data[i]['writer_id']]
            sampled_imgs = random.sample(all_candidates, min(self.num_img, len(all_candidates)))
            img_stack = torch.stack([sample['char_img'] for sample in sampled_imgs], dim=0)
            label_list = [sample['character'] for sample in sampled_imgs]

            output['img_list'].append(img_stack)
            output['img_label'].append(label_list)
            output['char_img'].append(batch_data[i]['char_img'])

        output['img_list'] = torch.stack(output['img_list'], 0)
        output['char_img'] = torch.stack(output['char_img'], 0)
        #print_once(f"BrushDataset Collated batch of size {bs} with max trajectory length {max_len}.")
        #print_once(f"BrushDataset Collated char_img shape: {output['char_img'].shape}, img_list shape: {output['img_list'].shape}")

        return output
