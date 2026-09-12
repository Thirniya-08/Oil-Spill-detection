import numpy as np
import tensorflow as tf
from PIL import Image

SAMPLE_SIZE = (256, 256)
RESULT_FILE_PATH = './result.txt' 

def dice_mc_metric(a, b):
    a = tf.unstack(a, axis=3)
    b = tf.unstack(b, axis=3)
    dice_summ = 0
    for aa, bb in zip(a, b):
        numenator = 2 * tf.math.reduce_sum(aa * bb) + 1
        denomerator = tf.math.reduce_sum(aa + bb) + 1
        dice_summ += numenator / denomerator
    return dice_summ / len(a)

def dice_mc_loss(a, b):
    return 1 - dice_mc_metric(a, b)

def dice_bce_mc_loss(a, b):
    return 0.3 * dice_mc_loss(a, b) + tf.reduce_mean(tf.keras.losses.binary_crossentropy(a, b))

model_path = "./unet_model.h5"
model = tf.keras.models.load_model(model_path, custom_objects={
    "dice_mc_loss": dice_mc_loss,
    "dice_bce_mc_loss": dice_bce_mc_loss,
    "dice_mc_metric": dice_mc_metric
})

def preprocess_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image = np.array(image)
    image = tf.image.resize(image, SAMPLE_SIZE)
    image = tf.image.convert_image_dtype(image, tf.float32)
    image = image / 255.0
    return tf.expand_dims(image, axis=0)

def generate_overlay(image, mask):
    image = image.numpy()  
    overlay = (mask > 0.5).astype(np.float32)  # Mask logic
    overlay_img = (image * 255).astype(np.uint8)
    overlay[overlay > 0] = 255  # Make mask fully white
    overlay = np.stack([overlay, overlay, overlay], axis=-1)
    blended = np.clip(overlay_img * 0.6 + overlay * 0.4, 0, 255).astype(np.uint8)
    return blended

def test_image(image_path):
    image_tensor = preprocess_image(image_path)
    prediction = model.predict(image_tensor)[0, ..., 0]
    
    mean_prediction = tf.reduce_mean(prediction)
    print("Mean prediction value:", mean_prediction.numpy())
    
    if mean_prediction >= 0.01:
        result = "Oil Spill Detected"
    else:
        result = "No Oil Spill Detected"
    print(result)

    # Write the result and mean prediction value to the text file
    with open(RESULT_FILE_PATH, 'w') as result_file:
        result_file.write(f"Result: {result}\n")

    # Optionally: generate and save overlay for visualization
    overlay = generate_overlay(image_tensor[0], prediction)
    overlay_image = Image.fromarray(overlay)
    overlay_image.save("./overlay.png")

# Run the test on 'test.jpg'
test_image("./uploads/test.jpg")
