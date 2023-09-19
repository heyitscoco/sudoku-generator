import subprocess
from pdf2image import convert_from_path


def batched(iterable, batch_size):
    i = 0
    while i < len(iterable):
        yield iterable[i: i + batch_size]
        i += batch_size


def copy_to_clipboard(data):
    subprocess.run("pbcopy", text=True, input=data)


def flatten_pdf(input_pdf_path, output_pdf_path, dpi=400, resolution=400.0):
    images = convert_from_path(input_pdf_path, dpi=dpi)
    im1 = images[0]
    images.pop(0)
    im1.save(output_pdf_path, "PDF", resolution=resolution, save_all=True, append_images=images)
