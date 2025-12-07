"""
Image processing utilities for thumbnail generation.
"""
from io import BytesIO
from PIL import Image


def generate_thumbnail(image_data, size=(300, 300), quality=85):
    """
    Generate a thumbnail from image binary data.
    
    Args:
        image_data: Binary image data
        size: Tuple of (width, height) for thumbnail size
        quality: JPEG quality (1-100)
    
    Returns:
        Binary data of the thumbnail image
    """
    if not image_data:
        return None
    
    try:
        # Open the image from binary data
        image = Image.open(BytesIO(image_data))
        
        # Convert RGBA to RGB if necessary (for JPEG compatibility)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Create thumbnail (maintains aspect ratio)
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        output = BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        
        return output.getvalue()
    except Exception as e:
        # Log the error but don't crash
        print(f"Error generating thumbnail: {e}")
        return None


def compress_image(image_data, max_size=(1920, 1920), quality=85):
    """
    Compress and resize an image if it's too large.
    
    Args:
        image_data: Binary image data
        max_size: Maximum dimensions (width, height)
        quality: JPEG quality (1-100)
    
    Returns:
        Binary data of the compressed image
    """
    if not image_data:
        return None
    
    try:
        # Open the image from binary data
        image = Image.open(BytesIO(image_data))
        
        # Convert RGBA to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if larger than max_size
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        output = BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        
        return output.getvalue()
    except Exception as e:
        print(f"Error compressing image: {e}")
        return image_data  # Return original if compression fails
