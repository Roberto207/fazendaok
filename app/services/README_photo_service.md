# Photo Service Documentation

## Overview

The `PhotoService` class provides comprehensive photo processing functionality for the FazendaOk platform, including:

- EXIF metadata extraction (GPS coordinates, capture date, device info)
- GPS coordinate validation against property boundaries
- Photo upload to S3-compatible storage
- Thumbnail generation

## Requirements Validated

This implementation validates the following requirements:

- **8.4**: Extract EXIF metadata including GPS coordinates, capture date, and device information
- **9.1**: Perform geospatial validation by checking if GPS coordinates fall within property polygon
- **9.2**: Mark photo validation status as "validated" or "outside_boundary"
- **9.3**: Store validation status with photo record
- **9.4**: Upload photo file to S3-compatible storage
- **9.6**: Store S3 URL in database
- **9.7**: Generate thumbnails for photo display

## Usage

### Initialization

```python
from app.services.photo_service import PhotoService

service = PhotoService(
    aws_access_key_id="your_access_key",
    aws_secret_access_key="your_secret_key",
    aws_bucket_name="fazendaok-photos",
    aws_endpoint_url="https://s3.amazonaws.com",  # Optional
    thumbnail_size=(300, 300)  # Optional, default is (300, 300)
)
```

### Extract EXIF Metadata

```python
# Read photo file
with open('photo.jpg', 'rb') as f:
    photo_bytes = f.read()

# Extract EXIF data
exif_data = service.extract_exif(photo_bytes)

print(f"GPS: {exif_data.gps_latitude}, {exif_data.gps_longitude}")
print(f"Captured: {exif_data.capture_date}")
print(f"Device: {exif_data.device_make} {exif_data.device_model}")
```

### Validate Photo Location

```python
from shapely.geometry import Polygon

# Define property boundary
property_polygon = Polygon([
    (-47.9, -15.8),
    (-47.9, -15.7),
    (-47.8, -15.7),
    (-47.8, -15.8),
    (-47.9, -15.8)
])

# Validate photo location
gps_coords = (exif_data.gps_latitude, exif_data.gps_longitude)
validation_status = service.validate_photo_location(gps_coords, property_polygon)

if validation_status == "validated":
    print("Photo is within property boundary")
else:
    print("Photo is outside property boundary")
```

### Upload to S3

```python
# Upload photo
s3_key = f"photos/{property_id}/{photo_id}.jpg"
s3_url = service.upload_to_s3(photo_bytes, s3_key)

print(f"Photo uploaded to: {s3_url}")
```

### Generate Thumbnail

```python
# Generate thumbnail
thumbnail_bytes = service.generate_thumbnail(photo_bytes)

# Upload thumbnail
thumbnail_key = f"photos/{property_id}/{photo_id}_thumb.jpg"
thumbnail_url = service.upload_to_s3(thumbnail_bytes, thumbnail_key)

print(f"Thumbnail uploaded to: {thumbnail_url}")
```

## Complete Workflow Example

```python
from app.services.photo_service import PhotoService
from shapely.geometry import Polygon

# Initialize service
service = PhotoService(
    aws_access_key_id="your_access_key",
    aws_secret_access_key="your_secret_key",
    aws_bucket_name="fazendaok-photos"
)

# Read photo
with open('property_photo.jpg', 'rb') as f:
    photo_bytes = f.read()

# Extract EXIF
exif_data = service.extract_exif(photo_bytes)

# Validate location (if GPS data exists)
if exif_data.gps_latitude and exif_data.gps_longitude:
    property_polygon = get_property_polygon_from_db(property_id)
    gps_coords = (exif_data.gps_latitude, exif_data.gps_longitude)
    validation_status = service.validate_photo_location(gps_coords, property_polygon)
else:
    validation_status = "no_gps_session_valid"

# Upload photo
photo_key = f"photos/{property_id}/{photo_id}.jpg"
photo_url = service.upload_to_s3(photo_bytes, photo_key)

# Generate and upload thumbnail
thumbnail_bytes = service.generate_thumbnail(photo_bytes)
thumbnail_key = f"photos/{property_id}/{photo_id}_thumb.jpg"
thumbnail_url = service.upload_to_s3(thumbnail_bytes, thumbnail_key)

# Store in database
save_photo_to_db(
    photo_id=photo_id,
    property_id=property_id,
    s3_url=photo_url,
    thumbnail_url=thumbnail_url,
    gps_latitude=exif_data.gps_latitude,
    gps_longitude=exif_data.gps_longitude,
    validation_status=validation_status,
    capture_date=exif_data.capture_date,
    device_make=exif_data.device_make,
    device_model=exif_data.device_model
)
```

## Error Handling

All methods raise `ValueError` with descriptive messages when errors occur:

```python
try:
    exif_data = service.extract_exif(photo_bytes)
except ValueError as e:
    print(f"Failed to extract EXIF: {e}")

try:
    validation_status = service.validate_photo_location(gps_coords, property_polygon)
except ValueError as e:
    print(f"Failed to validate location: {e}")

try:
    s3_url = service.upload_to_s3(photo_bytes, key)
except ValueError as e:
    print(f"Failed to upload to S3: {e}")

try:
    thumbnail_bytes = service.generate_thumbnail(photo_bytes)
except ValueError as e:
    print(f"Failed to generate thumbnail: {e}")
```

## GPS Coordinate Format

The service handles GPS coordinates in EXIF format (degrees, minutes, seconds) and converts them to decimal degrees:

- **Input**: `((15, 1), (47, 1), (42, 1))` with reference `'N'`
- **Output**: `15.795` (decimal degrees)

The service supports both direct numeric values and rational number tuples (numerator, denominator) as returned by Pillow's EXIF parser.

## Supported Image Formats

- JPEG
- PNG
- HEIC (if Pillow has HEIC support installed)
- Any format supported by Pillow

Thumbnails are always generated in JPEG format for consistency and file size optimization.

## Testing

Run the test suite:

```bash
pytest app/services/test_photo_service.py -v
```

The test suite includes:
- EXIF extraction tests (with and without GPS data)
- GPS coordinate conversion tests
- Photo location validation tests
- S3 upload tests (mocked)
- Thumbnail generation tests
- Full workflow integration test

## Dependencies

- `Pillow`: Image processing and EXIF extraction
- `boto3`: S3 upload functionality
- `shapely`: Geospatial operations for location validation
- `logging`: Error and info logging

## Notes

- GPS coordinates are validated to be within valid ranges: latitude [-90, 90], longitude [-180, 180]
- Thumbnails maintain aspect ratio and use LANCZOS resampling for quality
- S3 uploads include appropriate Content-Type headers
- All errors are logged with detailed context for debugging
- The service is thread-safe and can be used in async contexts (though methods are synchronous)
