import os
import random
from PIL import Image
import pandas as pd
import numpy as np
import json

def pick_image_from_csv(folder_path, csv_file):
    # Read CSV with no headers
    df = pd.read_csv(os.path.join(folder_path, csv_file), header=None)
    # Assign column names manually
    df.columns = ['Name', 'Probability']
    choices = df['Name'].values
    probabilities = df['Probability'].values / np.sum(df['Probability'].values)
    return np.random.choice(choices, p=probabilities)

def pick_image_from_csv_excluding(folder_path, csv_file, exclude=set()):
    df = pd.read_csv(os.path.join(folder_path, csv_file), header=None)
    df.columns = ['Name', 'Probability']
    # Filter out excluded images
    df = df[~df['Name'].isin(exclude)]
    choices = df['Name'].values
    probabilities = df['Probability'].values / np.sum(df['Probability'].values)
    if choices.size > 0:  # Ensure there are choices left after exclusion
        return np.random.choice(choices, p=probabilities), choices
    else:
        return None, choices  # Handle case where no choices are left

def add_layer(base_img, layer_img_path):
    layer = Image.open(layer_img_path).convert("RGBA")
    base_img.paste(layer, (0, 0), layer)
    return base_img

root_dir = "/Users/oviefaruq/Library/Mobile Documents/com~apple~CloudDocs/NFTs/Art/PD5/Raw"  # Update this path to your root directory
output_dir = "/Users/oviefaruq/Library/Mobile Documents/com~apple~CloudDocs/NFTs/Art/PD5/Output"

metadata_dir = os.path.join(output_dir, "Metadata")
if not os.path.exists(metadata_dir):
    os.makedirs(metadata_dir)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

sub_dirs = [
    "Background", "Foreground", "Table", "Painting",
    "Monitors", "Degen", "Chair", "Drink", "Touch Grass"
]

for i in range(6969):  # Assuming you want to generate 10 images, corrected from 100

    attributes = []

    base_img = Image.new("RGBA", (2732, 2048))  # Assuming a standard size, adjust as needed

    background = pick_image_from_csv(os.path.join(root_dir, "Background"), "Background.csv")
    background_path = os.path.join(root_dir, "Background", background)
    base_img = add_layer(base_img, background_path)

    # Initialize foreground_img here to ensure it's available for adding layers
    foreground_img = Image.new("RGBA", (2732, 2048))

    if background == "Black.png":
        # Define exact matches for color names
        foreground_color_options = ["Aquamarine.png", "Cantaloupe.png", "Crimson.png", "Toxic.png", "Violet.png",
                                    "White.png"]
        # Patterns for other valid foregrounds
        foreground_pattern_options = ["Fuzz", "Grid", "Stripes", "Subtle"]

        # List all files in the Foreground directory
        foreground_files = os.listdir(os.path.join(root_dir, "Foreground"))

        # Filter valid foregrounds based on exact matches or starting patterns
        valid_foregrounds = [file for file in foreground_files if file in foreground_color_options or
                             any(file.startswith(pattern) for pattern in foreground_pattern_options)]

        if valid_foregrounds:
            foreground = random.choice(valid_foregrounds)
            foreground_path = os.path.join(root_dir, "Foreground", foreground)
            foreground_img = add_layer(Image.new("RGBA", base_img.size), foreground_path)
            attributes.append({"trait_type": "Foreground", "value": foreground.replace("-", " ")[:-4]})
        else:
            print("Valid foreground file not found for Black background.")


    else:
        foreground = background  # Assuming matching name logic
        foreground_path = os.path.join(root_dir, "Foreground", foreground)
        if os.path.exists(foreground_path):
            foreground_img = add_layer(Image.new("RGBA", base_img.size), foreground_path)
            attributes.append({"trait_type": "Foreground", "value": foreground.replace("-", " ")[:-4]})
        else:
            print(f"Foreground image matching {background} not found, skipping.")

    for dir_name in sub_dirs[2:]:  # Skip Background and Foreground as they are already handled
        folder_path = os.path.join(root_dir, dir_name)
        if dir_name == "Monitors":
            monitors_folder = pick_image_from_csv(folder_path, "Monitors.csv")
            monitors_path = os.path.join(folder_path, monitors_folder)
            attributes.append({"trait_type": "Monitors", "value": monitors_folder})

            # Add the Base.png image from the selected Monitors subfolder
            base_image_path = os.path.join(monitors_path, "Base.png")
            base_img = add_layer(base_img, base_image_path)
            foreground_img = add_layer(foreground_img, base_image_path)

            # Keep track of picked images for this monitor setup to avoid duplicates
            picked_images = set()

            for screen_folder in sorted(os.listdir(monitors_path)):
                if screen_folder.startswith("Screen"):
                    # Adjust the pick_image_from_csv function to return both choice and modified choices list
                    screen_img, choices = pick_image_from_csv_excluding(
                        os.path.join(monitors_path, screen_folder), f"{screen_folder}.csv", exclude=picked_images)
                    if screen_img:
                        picked_images.add(screen_img)  # Add to the list of picked images
                        attributes.append(
                            {"trait_type": f"{screen_folder}", "value": screen_img.replace("-", " ")[:-4]})
                        base_img = add_layer(base_img, os.path.join(monitors_path, screen_folder, screen_img))
                        foreground_img = add_layer(foreground_img,
                                                   os.path.join(monitors_path, screen_folder, screen_img))
        else:
            image_file = pick_image_from_csv(folder_path, f"{dir_name}.csv")
            base_img = add_layer(base_img, os.path.join(folder_path, image_file))
            foreground_img = add_layer(foreground_img, os.path.join(folder_path, image_file))
            attributes.append({"trait_type": dir_name, "value": image_file.replace("-", " ")[:-4]})

    image_name = f"professional degen #{i}"
    image_path = f"https://ipfs.io/placeholder_ipfs_link/{i}.png"  # Modify as needed

    metadata = {
        "description": "professional degen 5 is a collection of 6969 artworks created by OSF",
        "external_url": "https://osf.art",
        "attributes": attributes,
        "image": image_path,
        "name": image_name
    }

    # Save the metadata to a JSON file
    with open(os.path.join(metadata_dir, f"{i}.json"), 'w') as f:
        json.dump(metadata, f, indent=4)

    # Generate GIF
    base_img = base_img.resize((int(base_img.width / 2), int(base_img.height / 2)))
    foreground_img = foreground_img.resize((int(foreground_img.width / 2), int(foreground_img.height / 2)))
    base_img.save(os.path.join(output_dir+"/Images", f"{i}.gif"), save_all=True, append_images=[foreground_img], loop=0, duration=150)
    print(f"Saved {i}.gif and metadata.")
