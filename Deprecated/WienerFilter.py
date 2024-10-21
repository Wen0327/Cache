import cv2
import numpy as np
from tkinter import filedialog
from tkinter import Tk
import os


# Function to deblur using the Wiener filter (simplified)
def wiener_filter(img, kernel_size=7, noise_var=1):
    # Create a simple motion blur kernel (this can be adapted to the actual blur used)
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
    kernel = kernel / kernel_size

    # Apply Wiener filter separately on each channel (R, G, B)
    deblurred_img = np.zeros_like(img, dtype=np.float32)

    for i in range(3):  # Process R, G, B channels
        # Fourier transform of the image channel and the kernel
        img_fft = np.fft.fft2(img[:, :, i])
        kernel_fft = np.fft.fft2(kernel, s=img[:, :, i].shape)

        # Apply Wiener filter in the frequency domain
        kernel_fft_conj = np.conj(kernel_fft)
        deblurred_fft = (
            img_fft * kernel_fft_conj / (kernel_fft * kernel_fft_conj + noise_var)
        )

        # Inverse Fourier transform to get the deblurred image channel
        deblurred_channel = np.fft.ifft2(deblurred_fft)

        # Normalize the result to avoid dark image
        deblurred_channel = np.abs(deblurred_channel)
        deblurred_channel = cv2.normalize(
            deblurred_channel, None, 0, 255, cv2.NORM_MINMAX
        )

        deblurred_img[:, :, i] = deblurred_channel

    return deblurred_img


# Open a file dialog to select an image
def select_image():
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select an image", filetypes=[("All files", "*")]
    )
    return file_path


# Function to save the deblurred image
def save_image(image, original_image_path):
    # Get the directory and the original file name
    directory, original_file_name = os.path.split(original_image_path)

    # Create the new file name by appending '_deblurred' to the original name
    name, ext = os.path.splitext(original_file_name)
    new_file_name = f"{name}_deblurred{ext}"

    # Create the full path for the new image
    save_path = os.path.join(directory, new_file_name)

    # Save the image using OpenCV
    cv2.imwrite(save_path, np.uint8(image))

    print(f"Deblurred image saved at: {save_path}")
    return save_path


# Main function
def main():
    # Select the image file
    image_path = select_image()

    if image_path:
        # Load the image
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)

        if img is None:
            print("Error: Could not read the image.")
            return

        # Apply Wiener filter to deblur the image
        deblurred_img = wiener_filter(img)

        # Save the deblurred image
        save_path = save_image(deblurred_img, image_path)

        # Display the original and deblurred images
        cv2.imshow("Original Image", img)
        cv2.imshow("Deblurred Image", np.uint8(deblurred_img))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    else:
        print("No image selected.")


if __name__ == "__main__":
    main()
