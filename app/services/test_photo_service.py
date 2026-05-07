"""
Unit tests for PhotoService.

Tests cover:
- EXIF extraction from photos
- GPS coordinate parsing and validation
- Photo location validation against property boundaries
- S3 upload functionality
- Thumbnail generation
"""

import io
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
from PIL.ExifTags import TAGS
from shapely.geometry import Polygon, Point

from app.services.photo_service import PhotoService, ExifData


# Test fixtures

@pytest.fixture
def photo_service():
    """Create PhotoService instance for testing."""
    return PhotoService(
        aws_access_key_id="test_key",
        aws_secret_access_key="test_secret",
        aws_bucket_name="test-bucket",
        aws_endpoint_url="http://localhost:9000"
    )


@pytest.fixture
def sample_image_bytes():
    """Create a sample image as bytes."""
    image = Image.new('RGB', (800, 600), color='red')
    img_io = io.BytesIO()
    image.save(img_io, format='JPEG')
    return img_io.getvalue()


@pytest.fixture
def sample_property_polygon():
    """Create a sample property polygon."""
    # Rectangle around coordinates in Goiás, Brazil
    return Polygon([
        (-47.9, -15.8),
        (-47.9, -15.7),
        (-47.8, -15.7),
        (-47.8, -15.8),
        (-47.9, -15.8)
    ])


# Tests for extract_exif

def test_extract_exif_no_exif_data(photo_service, sample_image_bytes):
    """Test EXIF extraction from image without EXIF data."""
    exif_data = photo_service.extract_exif(sample_image_bytes)
    
    assert isinstance(exif_data, ExifData)
    assert exif_data.gps_latitude is None
    assert exif_data.gps_longitude is None
    assert exif_data.capture_date is None
    assert exif_data.device_make is None
    assert exif_data.device_model is None


def test_extract_exif_with_gps_data(photo_service):
    """Test EXIF extraction from image with GPS data."""
    # Create image with EXIF data
    image = Image.new('RGB', (800, 600), color='blue')
    
    # Mock EXIF data with GPS coordinates
    # Note: Using the format that Pillow's getexif() returns
    from PIL.ExifTags import TAGS
    
    # Get tag IDs
    gps_info_tag = None
    make_tag = None
    model_tag = None
    datetime_tag = None
    
    for tag_id, tag_name in TAGS.items():
        if tag_name == 'GPSInfo':
            gps_info_tag = tag_id
        elif tag_name == 'Make':
            make_tag = tag_id
        elif tag_name == 'Model':
            model_tag = tag_id
        elif tag_name == 'DateTimeOriginal':
            datetime_tag = tag_id
    
    exif_dict = {
        gps_info_tag: {
            1: 'N',  # GPSLatitudeRef
            2: ((15, 1), (47, 1), (42, 1)),  # GPSLatitude: 15°47'42"
            3: 'W',  # GPSLongitudeRef
            4: ((47, 1), (52, 1), (58, 1)),  # GPSLongitude: 47°52'58"
        },
        make_tag: 'TestCamera',
        model_tag: 'TestModel',
        datetime_tag: '2024:01:15 10:30:00'
    }
    
    with patch.object(Image.Image, 'getexif', return_value=exif_dict):
        img_io = io.BytesIO()
        image.save(img_io, format='JPEG')
        photo_bytes = img_io.getvalue()
        
        exif_data = photo_service.extract_exif(photo_bytes)
        
        assert exif_data.gps_latitude is not None
        assert exif_data.gps_longitude is not None
        assert exif_data.device_make == 'TestCamera'
        assert exif_data.device_model == 'TestModel'
        assert exif_data.capture_date == datetime(2024, 1, 15, 10, 30, 0)


def test_extract_exif_invalid_photo_bytes(photo_service):
    """Test EXIF extraction with invalid photo bytes."""
    with pytest.raises(ValueError, match="Failed to extract EXIF data"):
        photo_service.extract_exif(b"invalid image data")


# Tests for GPS coordinate conversion

def test_convert_gps_coordinate_north(photo_service):
    """Test GPS coordinate conversion for northern latitude."""
    coordinate = ((15, 1), (47, 1), (42, 1))  # 15°47'42"
    ref = 'N'
    
    result = photo_service._convert_gps_coordinate(coordinate, ref)
    
    assert result is not None
    assert abs(result - 15.795) < 0.001  # 15 + 47/60 + 42/3600


def test_convert_gps_coordinate_south(photo_service):
    """Test GPS coordinate conversion for southern latitude."""
    coordinate = ((15, 1), (47, 1), (42, 1))  # 15°47'42"
    ref = 'S'
    
    result = photo_service._convert_gps_coordinate(coordinate, ref)
    
    assert result is not None
    assert abs(result - (-15.795)) < 0.001


def test_convert_gps_coordinate_west(photo_service):
    """Test GPS coordinate conversion for western longitude."""
    coordinate = ((47, 1), (52, 1), (58, 1))  # 47°52'58"
    ref = 'W'
    
    result = photo_service._convert_gps_coordinate(coordinate, ref)
    
    assert result is not None
    assert abs(result - (-47.8828)) < 0.001


def test_convert_gps_coordinate_invalid(photo_service):
    """Test GPS coordinate conversion with invalid data."""
    assert photo_service._convert_gps_coordinate(None, 'N') is None
    assert photo_service._convert_gps_coordinate(((15, 1),), 'N') is None
    assert photo_service._convert_gps_coordinate(((15, 1), (47, 1), (42, 1)), None) is None


# Tests for validate_photo_location

def test_validate_photo_location_inside_boundary(photo_service, sample_property_polygon):
    """Test photo location validation when coordinates are inside property boundary."""
    # Coordinates inside the polygon
    gps_coords = (-15.75, -47.85)
    
    result = photo_service.validate_photo_location(gps_coords, sample_property_polygon)
    
    assert result == "validated"


def test_validate_photo_location_outside_boundary(photo_service, sample_property_polygon):
    """Test photo location validation when coordinates are outside property boundary."""
    # Coordinates outside the polygon
    gps_coords = (-15.6, -47.7)
    
    result = photo_service.validate_photo_location(gps_coords, sample_property_polygon)
    
    assert result == "outside_boundary"


def test_validate_photo_location_invalid_coordinates(photo_service, sample_property_polygon):
    """Test photo location validation with invalid coordinates."""
    # Invalid latitude
    with pytest.raises(ValueError, match="Invalid GPS coordinates"):
        photo_service.validate_photo_location((100.0, -47.85), sample_property_polygon)
    
    # Invalid longitude
    with pytest.raises(ValueError, match="Invalid GPS coordinates"):
        photo_service.validate_photo_location((-15.75, 200.0), sample_property_polygon)


def test_validate_photo_location_with_wkb_polygon(photo_service, sample_property_polygon):
    """Test photo location validation with WKB-encoded polygon."""
    from shapely import wkb
    
    # Convert polygon to WKB
    wkb_polygon = wkb.dumps(sample_property_polygon)
    
    # Coordinates inside the polygon
    gps_coords = (-15.75, -47.85)
    
    result = photo_service.validate_photo_location(gps_coords, wkb_polygon)
    
    assert result == "validated"


# Tests for upload_to_s3

@patch('boto3.client')
def test_upload_to_s3_success(mock_boto_client, photo_service, sample_image_bytes):
    """Test successful S3 upload."""
    # Mock S3 client
    mock_s3 = MagicMock()
    mock_s3.meta.endpoint_url = "http://localhost:9000"
    mock_boto_client.return_value = mock_s3
    
    # Recreate service with mocked client
    service = PhotoService(
        aws_access_key_id="test_key",
        aws_secret_access_key="test_secret",
        aws_bucket_name="test-bucket",
        aws_endpoint_url="http://localhost:9000"
    )
    
    key = "photos/test-property/test-photo.jpg"
    url = service.upload_to_s3(sample_image_bytes, key)
    
    # Verify S3 client was called
    mock_s3.put_object.assert_called_once()
    call_args = mock_s3.put_object.call_args
    assert call_args[1]['Bucket'] == 'test-bucket'
    assert call_args[1]['Key'] == key
    assert call_args[1]['ContentType'] == 'image/jpeg'
    
    # Verify URL format
    assert "test-bucket" in url
    assert key in url


@patch('boto3.client')
def test_upload_to_s3_failure(mock_boto_client, photo_service, sample_image_bytes):
    """Test S3 upload failure."""
    from botocore.exceptions import ClientError
    
    # Mock S3 client to raise error
    mock_s3 = MagicMock()
    mock_s3.put_object.side_effect = ClientError(
        {'Error': {'Code': 'NoSuchBucket', 'Message': 'Bucket does not exist'}},
        'PutObject'
    )
    mock_boto_client.return_value = mock_s3
    
    # Recreate service with mocked client
    service = PhotoService(
        aws_access_key_id="test_key",
        aws_secret_access_key="test_secret",
        aws_bucket_name="test-bucket",
        aws_endpoint_url="http://localhost:9000"
    )
    
    key = "photos/test-property/test-photo.jpg"
    
    with pytest.raises(ValueError, match="Failed to upload photo to S3"):
        service.upload_to_s3(sample_image_bytes, key)


# Tests for generate_thumbnail

def test_generate_thumbnail_success(photo_service, sample_image_bytes):
    """Test successful thumbnail generation."""
    thumbnail_bytes = photo_service.generate_thumbnail(sample_image_bytes)
    
    # Verify thumbnail is valid image
    thumbnail_image = Image.open(io.BytesIO(thumbnail_bytes))
    assert thumbnail_image.format == 'JPEG'
    
    # Verify thumbnail size
    assert thumbnail_image.width <= 300
    assert thumbnail_image.height <= 300
    
    # Verify thumbnail is smaller than original
    assert len(thumbnail_bytes) < len(sample_image_bytes)


def test_generate_thumbnail_maintains_aspect_ratio(photo_service):
    """Test that thumbnail generation maintains aspect ratio."""
    # Create wide image (2:1 aspect ratio)
    image = Image.new('RGB', (1000, 500), color='green')
    img_io = io.BytesIO()
    image.save(img_io, format='JPEG')
    photo_bytes = img_io.getvalue()
    
    thumbnail_bytes = photo_service.generate_thumbnail(photo_bytes)
    thumbnail_image = Image.open(io.BytesIO(thumbnail_bytes))
    
    # Verify aspect ratio is maintained
    aspect_ratio = thumbnail_image.width / thumbnail_image.height
    assert abs(aspect_ratio - 2.0) < 0.1


def test_generate_thumbnail_with_png(photo_service):
    """Test thumbnail generation from PNG image."""
    # Create PNG image with transparency
    image = Image.new('RGBA', (800, 600), color=(255, 0, 0, 128))
    img_io = io.BytesIO()
    image.save(img_io, format='PNG')
    photo_bytes = img_io.getvalue()
    
    thumbnail_bytes = photo_service.generate_thumbnail(photo_bytes)
    
    # Verify thumbnail is valid JPEG (converted from PNG)
    thumbnail_image = Image.open(io.BytesIO(thumbnail_bytes))
    assert thumbnail_image.format == 'JPEG'


def test_generate_thumbnail_invalid_image(photo_service):
    """Test thumbnail generation with invalid image data."""
    with pytest.raises(ValueError, match="Failed to generate thumbnail"):
        photo_service.generate_thumbnail(b"invalid image data")


# Integration-style tests

def test_full_photo_processing_workflow(photo_service, sample_property_polygon):
    """Test complete photo processing workflow."""
    # Create image with EXIF data
    image = Image.new('RGB', (1200, 900), color='blue')
    
    # Mock EXIF data
    from PIL.ExifTags import TAGS
    
    # Get tag IDs
    gps_info_tag = None
    make_tag = None
    model_tag = None
    datetime_tag = None
    
    for tag_id, tag_name in TAGS.items():
        if tag_name == 'GPSInfo':
            gps_info_tag = tag_id
        elif tag_name == 'Make':
            make_tag = tag_id
        elif tag_name == 'Model':
            model_tag = tag_id
        elif tag_name == 'DateTimeOriginal':
            datetime_tag = tag_id
    
    exif_dict = {
        gps_info_tag: {
            1: 'S',
            2: ((15, 1), (45, 1), (0, 1)),  # 15°45'0" S = -15.75
            3: 'W',
            4: ((47, 1), (51, 1), (0, 1)),  # 47°51'0" W = -47.85
        },
        make_tag: 'TestCamera',
        model_tag: 'TestModel',
        datetime_tag: '2024:01:15 14:30:00'
    }
    
    with patch.object(Image.Image, 'getexif', return_value=exif_dict):
        img_io = io.BytesIO()
        image.save(img_io, format='JPEG')
        photo_bytes = img_io.getvalue()
        
        # Extract EXIF
        exif_data = photo_service.extract_exif(photo_bytes)
        assert exif_data.gps_latitude is not None
        assert exif_data.gps_longitude is not None
        
        # Validate location
        gps_coords = (exif_data.gps_latitude, exif_data.gps_longitude)
        validation_status = photo_service.validate_photo_location(gps_coords, sample_property_polygon)
        assert validation_status == "validated"
        
        # Generate thumbnail
        thumbnail_bytes = photo_service.generate_thumbnail(photo_bytes)
        assert len(thumbnail_bytes) > 0
        assert len(thumbnail_bytes) < len(photo_bytes)
