from cloudinary.uploader import upload
from PIL import Image
import io
import os

def optimize_and_upload(image_file, folder="requests"):
    """
    Optimiza y sube imagen a Cloudinary con compresión automática
    
    Args:
        image_file: Archivo de imagen (Django UploadedFile)
        folder: Carpeta en Cloudinary para organizar
    
    Returns:
        str: URL segura de la imagen en Cloudinary
    """
    try:
        # Abrir imagen original
        img = Image.open(image_file)
        
        # Redimensionar si es muy grande (máximo 1920px en el lado más largo)
        max_size = 1920
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convertir RGBA a RGB para compatibilidad
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Guardar en buffer con compresión
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        buffer.seek(0)
        
        # Subir a Cloudinary con optimizaciones
        result = upload(
            buffer,
            folder=folder,
            resource_type="image",
            format="auto",  # WebP para navegadores compatibles, JPG para otros
            quality="auto:good",  # Calidad automática balanceada
            fetch_format="auto",  # Formato según navegador
            transformation=[
                {'width': 1920, 'crop': 'limit'},  # Límite de tamaño
                {'quality': 'auto:good'},  # Calidad automática
                {'fetch_format': 'auto'}  # Formato automático
            ]
        )
        
        return result['secure_url']
    
    except Exception as e:
        # Si falla la optimización, subir imagen original
        print(f"Error optimizando imagen: {e}")
        result = upload(
            image_file,
            folder=folder,
            resource_type="image",
            quality="auto:good"
        )
        return result['secure_url']


def delete_from_cloudinary(image_url):
    """
    Elimina imagen de Cloudinary usando la URL
    """
    try:
        # Extraer public_id de la URL
        public_id = image_url.split('/')[-1].split('.')[0]
        folder = '/'.join(image_url.split('/')[7:-1])
        full_public_id = f"{folder}/{public_id}" if folder else public_id
        
        from cloudinary.uploader import destroy
        result = destroy(full_public_id)
        return result
    except Exception as e:
        print(f"Error eliminando imagen: {e}")
        return None