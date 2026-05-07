"""
Photo processing service for FazendaOk Platform.

This service handles:
- EXIF metadata extraction from photos
- GPS coordinate validation against property boundaries
- Photo upload to S3-compatible storage
- Thumbnail generation
"""

import io
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import boto3
from botocore.exceptions import ClientError
from shapely.geometry import Point, Polygon
from shapely import wkb

logger = logging.getLogger(__name__)

# Constants for photo upload validation
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic'}
MAX_FILE_SIZE_MB = 10
MAX_BATCH_SIZE = 20


class ExifData:
    """Container for extracted EXIF metadata."""
    
    def __init__(
        self,
        gps_latitude: Optional[float] = None,
        gps_longitude: Optional[float] = None,
        capture_date: Optional[datetime] = None,
        device_make: Optional[str] = None,
        device_model: Optional[str] = None,
        raw_exif: Optional[Dict[str, Any]] = None
    ):
        self.gps_latitude = gps_latitude
        self.gps_longitude = gps_longitude
        self.capture_date = capture_date
        self.device_make = device_make
        self.device_model = device_model
        self.raw_exif = raw_exif or {}


class PhotoService:
    """Service for photo processing operations."""
    
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_bucket_name: str,
        aws_endpoint_url: Optional[str] = None,
        thumbnail_size: Tuple[int, int] = (300, 300)
    ):
        """
        Initialize PhotoService.
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            aws_bucket_name: S3 bucket name
            aws_endpoint_url: Optional S3 endpoint URL (for S3-compatible services)
            thumbnail_size: Thumbnail dimensions (width, height)
        """
        self.bucket_name = aws_bucket_name
        self.thumbnail_size = thumbnail_size
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=aws_endpoint_url
        )
        
        logger.info(f"PhotoService initialized with bucket: {aws_bucket_name}")
    
    @staticmethod
    def validate_photo_upload(
        file_extension: str,
        file_size_mb: float,
        batch_size: int
    ) -> bool:
        """
        Validate photo upload request against platform constraints.
        
        Args:
            file_extension: File extension (e.g., '.jpg', '.PNG', '.heic')
            file_size_mb: File size in megabytes
            batch_size: Number of photos in the upload batch
            
        Returns:
            True if all validation criteria are met, False otherwise
            
        Validation Rules:
            - File extension must be one of: .jpg, .jpeg, .png, .heic (case-insensitive)
            - File size must be ≤ 10 MB
            - Batch size must be ≤ 20 photos
        """
        # Normalize extension to lowercase for case-insensitive comparison
        normalized_extension = file_extension.lower()
        
        # Check file extension
        if normalized_extension not in ALLOWED_EXTENSIONS:
            return False
        
        # Check file size
        if file_size_mb > MAX_FILE_SIZE_MB:
            return False
        
        # Check batch size
        if batch_size > MAX_BATCH_SIZE:
            return False
        
        return True
    
    def extract_exif(self, photo_bytes: bytes) -> ExifData:
        """
        Extract EXIF metadata from photo bytes.
        
        Args:
            photo_bytes: Raw photo data as bytes
            
        Returns:
            ExifData object containing extracted metadata
            
        Raises:
            ValueError: If photo_bytes is invalid or cannot be processed
        """
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(photo_bytes))
            
            # Get EXIF data (use getexif() for Pillow 6.0+)
            exif_data = image.getexif()
            
            if not exif_data:
                logger.warning("No EXIF data found in photo")
                return ExifData()
            
            # Parse EXIF tags
            exif_dict = {}
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                exif_dict[tag_name] = value
            
            # Extract GPS coordinates
            gps_latitude, gps_longitude = self._extract_gps_coordinates(exif_dict)
            
            # Extract capture date
            capture_date = self._extract_capture_date(exif_dict)
            
            # Extract device info
            device_make = exif_dict.get('Make')
            device_model = exif_dict.get('Model')
            
            return ExifData(
                gps_latitude=gps_latitude,
                gps_longitude=gps_longitude,
                capture_date=capture_date,
                device_make=device_make,
                device_model=device_model,
                raw_exif=exif_dict
            )
            
        except Exception as e:
            logger.error(f"Error extracting EXIF data: {str(e)}")
            raise ValueError(f"Failed to extract EXIF data: {str(e)}")
    
    def _extract_gps_coordinates(self, exif_dict: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
        """
        Extract GPS coordinates from EXIF dictionary.
        
        Args:
            exif_dict: Dictionary of EXIF tags
            
        Returns:
            Tuple of (latitude, longitude) or (None, None) if not found
        """
        gps_info = exif_dict.get('GPSInfo')
        
        if not gps_info:
            return None, None
        
        try:
            # Parse GPS tags
            gps_data = {}
            for tag_id, value in gps_info.items():
                tag_name = GPSTAGS.get(tag_id, tag_id)
                gps_data[tag_name] = value
            
            # Extract latitude
            lat = self._convert_gps_coordinate(
                gps_data.get('GPSLatitude'),
                gps_data.get('GPSLatitudeRef')
            )
            
            # Extract longitude
            lon = self._convert_gps_coordinate(
                gps_data.get('GPSLongitude'),
                gps_data.get('GPSLongitudeRef')
            )
            
            if lat is not None and lon is not None:
                # Validate coordinate ranges
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return lat, lon
                else:
                    logger.warning(f"GPS coordinates out of valid range: lat={lat}, lon={lon}")
                    return None, None
            
            return None, None
            
        except Exception as e:
            logger.error(f"Error parsing GPS coordinates: {str(e)}")
            return None, None
    
    def _convert_gps_coordinate(self, coordinate: Optional[tuple], ref: Optional[str]) -> Optional[float]:
        """
        Convert GPS coordinate from degrees/minutes/seconds to decimal degrees.
        
        Args:
            coordinate: Tuple of (degrees, minutes, seconds) where each can be a number or (numerator, denominator) tuple
            ref: Reference direction ('N', 'S', 'E', 'W')
            
        Returns:
            Decimal degree value or None if conversion fails
        """
        if not coordinate or not ref:
            return None
        
        try:
            # Helper function to convert rational number to float
            def to_float(value):
                if isinstance(value, tuple) and len(value) == 2:
                    # Rational number (numerator, denominator)
                    return float(value[0]) / float(value[1])
                return float(value)
            
            # Convert to floats (handle both direct numbers and rational tuples)
            degrees = to_float(coordinate[0])
            minutes = to_float(coordinate[1])
            seconds = to_float(coordinate[2])
            
            # Calculate decimal degrees
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            # Apply direction
            if ref in ['S', 'W']:
                decimal = -decimal
            
            return decimal
            
        except (IndexError, TypeError, ValueError, ZeroDivisionError) as e:
            logger.error(f"Error converting GPS coordinate: {str(e)}")
            return None
    
    def _extract_capture_date(self, exif_dict: Dict[str, Any]) -> Optional[datetime]:
        """
        Extract capture date from EXIF dictionary.
        
        Args:
            exif_dict: Dictionary of EXIF tags
            
        Returns:
            Datetime object or None if not found
        """
        # Try different date fields
        date_fields = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
        
        for field in date_fields:
            date_str = exif_dict.get(field)
            if date_str:
                try:
                    # Parse EXIF date format: "YYYY:MM:DD HH:MM:SS"
                    return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    continue
        
        return None
    
    def validate_photo_location(
        self,
        gps_coords: Tuple[float, float],
        property_polygon: Any
    ) -> str:
        """
        Validate that GPS coordinates fall within property polygon.
        
        Args:
            gps_coords: Tuple of (latitude, longitude)
            property_polygon: Property boundary as WKB geometry or Shapely Polygon
            
        Returns:
            Validation status: "validated", "outside_boundary"
            
        Raises:
            ValueError: If inputs are invalid
        """
        try:
            latitude, longitude = gps_coords
            
            # Validate coordinate ranges
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                raise ValueError(f"Invalid GPS coordinates: lat={latitude}, lon={longitude}")
            
            # Create point from coordinates
            point = Point(longitude, latitude)  # Note: Shapely uses (lon, lat) order
            
            # Convert property_polygon to Shapely Polygon if needed
            if isinstance(property_polygon, bytes):
                # Assume WKB format from PostGIS
                polygon = wkb.loads(property_polygon)
            elif isinstance(property_polygon, str):
                # Assume WKT format
                from shapely import wkt
                polygon = wkt.loads(property_polygon)
            elif isinstance(property_polygon, Polygon):
                polygon = property_polygon
            else:
                raise ValueError(f"Unsupported property_polygon type: {type(property_polygon)}")
            
            # Check if point is within polygon
            if polygon.contains(point):
                logger.info(f"Photo location validated: ({latitude}, {longitude}) is within property boundary")
                return "validated"
            else:
                logger.warning(f"Photo location outside boundary: ({latitude}, {longitude})")
                return "outside_boundary"
                
        except Exception as e:
            logger.error(f"Error validating photo location: {str(e)}")
            raise ValueError(f"Failed to validate photo location: {str(e)}")
    
    def upload_to_s3(self, photo_bytes: bytes, key: str) -> str:
        """
        Upload photo to S3-compatible storage.
        
        Args:
            photo_bytes: Raw photo data as bytes
            key: S3 object key (path within bucket)
            
        Returns:
            S3 URL of uploaded photo
            
        Raises:
            ValueError: If upload fails
        """
        try:
            # Determine content type from image
            image = Image.open(io.BytesIO(photo_bytes))
            content_type = f"image/{image.format.lower()}" if image.format else "image/jpeg"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=photo_bytes,
                ContentType=content_type
            )
            
            # Generate URL
            url = f"{self.s3_client.meta.endpoint_url}/{self.bucket_name}/{key}" if self.s3_client.meta.endpoint_url else f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            
            logger.info(f"Photo uploaded to S3: {key}")
            return url
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise ValueError(f"Failed to upload photo to S3: {str(e)}")
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            raise ValueError(f"Failed to upload photo: {str(e)}")
    
    def generate_thumbnail(self, photo_bytes: bytes) -> bytes:
        """
        Generate thumbnail from photo bytes.
        
        Args:
            photo_bytes: Raw photo data as bytes
            
        Returns:
            Thumbnail image as bytes (JPEG format)
            
        Raises:
            ValueError: If thumbnail generation fails
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(photo_bytes))
            
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
            
            # Generate thumbnail (maintains aspect ratio)
            image.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            thumbnail_io = io.BytesIO()
            image.save(thumbnail_io, format='JPEG', quality=85, optimize=True)
            thumbnail_bytes = thumbnail_io.getvalue()
            
            logger.info(f"Thumbnail generated: {len(thumbnail_bytes)} bytes")
            return thumbnail_bytes
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            raise ValueError(f"Failed to generate thumbnail: {str(e)}")
