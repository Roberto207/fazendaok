"""
Property-based tests for photo upload validation.

**Validates: Requirements 8.1, 8.2, 8.3**

This module contains property-based tests using Hypothesis to validate
that the photo upload validation function correctly enforces:
- File extension restrictions (.jpg, .jpeg, .png, .heic - case-insensitive)
- File size limit (≤ 10 MB)
- Batch size limit (≤ 20 photos)
"""

import pytest
from hypothesis import given, strategies as st, assume

from app.services.photo_service import PhotoService, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, MAX_BATCH_SIZE


# Strategy definitions for generating test data

# Valid file extensions (case variations)
valid_extensions_strategy = st.sampled_from([
    '.jpg', '.JPG', '.Jpg',
    '.jpeg', '.JPEG', '.Jpeg',
    '.png', '.PNG', '.Png',
    '.heic', '.HEIC', '.Heic'
])

# Invalid file extensions
invalid_extensions_strategy = st.sampled_from([
    '.gif', '.bmp', '.tiff', '.webp', '.svg', '.pdf',
    '.txt', '.doc', '.mp4', '.avi', '.zip', '.exe',
    'jpg', 'jpeg', 'png',  # Missing dot
    '.jp', '.pn', '.hei',  # Truncated
    '.jpgg', '.pngg', '.heicc',  # Extra characters
    '', '.'  # Edge cases
])

# File sizes in MB
valid_file_size_strategy = st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)
invalid_file_size_strategy = st.floats(min_value=10.001, max_value=1000.0, allow_nan=False, allow_infinity=False)

# Batch sizes
valid_batch_size_strategy = st.integers(min_value=1, max_value=20)
invalid_batch_size_strategy = st.integers(min_value=21, max_value=100)


# Property Tests

@given(
    file_extension=valid_extensions_strategy,
    file_size_mb=valid_file_size_strategy,
    batch_size=valid_batch_size_strategy
)
def test_property_valid_upload_requests_accepted(file_extension, file_size_mb, batch_size):
    """
    **Property 4: Photo Upload Validation**
    **Validates: Requirements 8.1, 8.2, 8.3**
    
    Property: For any photo upload request where:
    - File extension is one of: .jpg, .jpeg, .png, .heic (case-insensitive)
    - File size is ≤ 10 MB
    - Batch size is ≤ 20 photos
    
    The validation function MUST return True.
    """
    result = PhotoService.validate_photo_upload(file_extension, file_size_mb, batch_size)
    assert result is True, (
        f"Valid upload request rejected: extension={file_extension}, "
        f"size={file_size_mb}MB, batch={batch_size}"
    )


@given(
    file_extension=invalid_extensions_strategy,
    file_size_mb=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    batch_size=st.integers(min_value=1, max_value=20)
)
def test_property_invalid_extension_rejected(file_extension, file_size_mb, batch_size):
    """
    **Property 4: Photo Upload Validation - Invalid Extension**
    **Validates: Requirement 8.1**
    
    Property: For any photo upload request with an invalid file extension
    (not .jpg, .jpeg, .png, or .heic), the validation function MUST return False,
    regardless of file size or batch size.
    """
    result = PhotoService.validate_photo_upload(file_extension, file_size_mb, batch_size)
    assert result is False, (
        f"Invalid extension accepted: extension={file_extension}, "
        f"size={file_size_mb}MB, batch={batch_size}"
    )


@given(
    file_extension=valid_extensions_strategy,
    file_size_mb=invalid_file_size_strategy,
    batch_size=st.integers(min_value=1, max_value=20)
)
def test_property_oversized_file_rejected(file_extension, file_size_mb, batch_size):
    """
    **Property 4: Photo Upload Validation - Oversized File**
    **Validates: Requirement 8.2**
    
    Property: For any photo upload request with file size > 10 MB,
    the validation function MUST return False, regardless of file extension
    or batch size.
    """
    result = PhotoService.validate_photo_upload(file_extension, file_size_mb, batch_size)
    assert result is False, (
        f"Oversized file accepted: extension={file_extension}, "
        f"size={file_size_mb}MB, batch={batch_size}"
    )


@given(
    file_extension=valid_extensions_strategy,
    file_size_mb=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    batch_size=invalid_batch_size_strategy
)
def test_property_oversized_batch_rejected(file_extension, file_size_mb, batch_size):
    """
    **Property 4: Photo Upload Validation - Oversized Batch**
    **Validates: Requirement 8.3**
    
    Property: For any photo upload request with batch size > 20 photos,
    the validation function MUST return False, regardless of file extension
    or file size.
    """
    result = PhotoService.validate_photo_upload(file_extension, file_size_mb, batch_size)
    assert result is False, (
        f"Oversized batch accepted: extension={file_extension}, "
        f"size={file_size_mb}MB, batch={batch_size}"
    )


@given(
    file_extension=st.one_of(valid_extensions_strategy, invalid_extensions_strategy),
    file_size_mb=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    batch_size=st.integers(min_value=1, max_value=100)
)
def test_property_validation_consistency(file_extension, file_size_mb, batch_size):
    """
    **Property 4: Photo Upload Validation - Consistency**
    **Validates: Requirements 8.1, 8.2, 8.3**
    
    Property: The validation function returns True if and only if ALL three
    conditions are met:
    1. File extension is valid (case-insensitive)
    2. File size ≤ 10 MB
    3. Batch size ≤ 20 photos
    
    This property verifies the logical consistency of the validation function.
    """
    result = PhotoService.validate_photo_upload(file_extension, file_size_mb, batch_size)
    
    # Determine expected result based on validation rules
    normalized_extension = file_extension.lower()
    extension_valid = normalized_extension in ALLOWED_EXTENSIONS
    size_valid = file_size_mb <= MAX_FILE_SIZE_MB
    batch_valid = batch_size <= MAX_BATCH_SIZE
    
    expected_result = extension_valid and size_valid and batch_valid
    
    assert result == expected_result, (
        f"Validation inconsistency: extension={file_extension} (valid={extension_valid}), "
        f"size={file_size_mb}MB (valid={size_valid}), batch={batch_size} (valid={batch_valid}), "
        f"expected={expected_result}, got={result}"
    )


@given(
    file_extension=valid_extensions_strategy,
    file_size_mb=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    batch_size=valid_batch_size_strategy
)
def test_property_case_insensitive_extension(file_extension, file_size_mb, batch_size):
    """
    **Property 4: Photo Upload Validation - Case Insensitivity**
    **Validates: Requirement 8.1**
    
    Property: File extension validation MUST be case-insensitive.
    For any valid extension in any case combination (.jpg, .JPG, .Jpg, etc.),
    the validation function MUST return True (assuming other criteria are met).
    """
    result = PhotoService.validate_photo_upload(file_extension, file_size_mb, batch_size)
    assert result is True, (
        f"Case-insensitive validation failed: extension={file_extension}, "
        f"size={file_size_mb}MB, batch={batch_size}"
    )


# Edge case tests using property-based testing

@given(
    file_extension=valid_extensions_strategy,
    batch_size=valid_batch_size_strategy
)
def test_property_boundary_file_size_exactly_10mb(file_extension, batch_size):
    """
    **Property 4: Photo Upload Validation - Boundary Case**
    **Validates: Requirement 8.2**
    
    Property: A file of exactly 10.0 MB MUST be accepted (boundary inclusive).
    """
    file_size_mb = 10.0
    result = PhotoService.validate_photo_upload(file_extension, file_size_mb, batch_size)
    assert result is True, (
        f"Boundary case failed: 10.0 MB file rejected with extension={file_extension}, "
        f"batch={batch_size}"
    )


@given(
    file_extension=valid_extensions_strategy,
    file_size_mb=valid_file_size_strategy
)
def test_property_boundary_batch_size_exactly_20(file_extension, file_size_mb):
    """
    **Property 4: Photo Upload Validation - Boundary Case**
    **Validates: Requirement 8.3**
    
    Property: A batch of exactly 20 photos MUST be accepted (boundary inclusive).
    """
    batch_size = 20
    result = PhotoService.validate_photo_upload(file_extension, file_size_mb, batch_size)
    assert result is True, (
        f"Boundary case failed: batch of 20 rejected with extension={file_extension}, "
        f"size={file_size_mb}MB"
    )


@given(
    file_extension=valid_extensions_strategy,
    batch_size=valid_batch_size_strategy
)
def test_property_zero_file_size_accepted(file_extension, batch_size):
    """
    **Property 4: Photo Upload Validation - Edge Case**
    **Validates: Requirement 8.2**
    
    Property: A file of 0 MB (empty file) MUST be accepted by the validation
    function (actual file content validation happens elsewhere).
    """
    file_size_mb = 0.0
    result = PhotoService.validate_photo_upload(file_extension, file_size_mb, batch_size)
    assert result is True, (
        f"Zero-size file rejected: extension={file_extension}, batch={batch_size}"
    )


@given(
    file_extension=valid_extensions_strategy,
    file_size_mb=valid_file_size_strategy
)
def test_property_single_photo_batch_accepted(file_extension, file_size_mb):
    """
    **Property 4: Photo Upload Validation - Edge Case**
    **Validates: Requirement 8.3**
    
    Property: A batch of 1 photo (minimum batch) MUST be accepted.
    """
    batch_size = 1
    result = PhotoService.validate_photo_upload(file_extension, file_size_mb, batch_size)
    assert result is True, (
        f"Single photo batch rejected: extension={file_extension}, size={file_size_mb}MB"
    )
