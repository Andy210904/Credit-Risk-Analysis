# CSV Upload Debugging Guide

## Common Issues and Solutions

### Issue: "Field required" error for file parameter

This error occurs when the `file` field is missing from the multipart form data.

### Possible Causes:

1. **Incorrect Form Field Name**
   - The form field must be named `file`
   - Frontend code should use: `formData.append('file', fileInput)`

2. **Missing Content-Type Header**
   - Don't set Content-Type manually for file uploads
   - Let the browser set it automatically for multipart/form-data

3. **Wrong Request Method**
   - Must be POST request
   - Must use multipart/form-data encoding

### Frontend Examples:

#### JavaScript (Fetch API):
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/api/data/upload-csv', {
    method: 'POST',
    body: formData  // Don't set Content-Type header
});
```

#### JavaScript (Axios):
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

axios.post('/api/data/upload-csv', formData, {
    headers: {
        'Content-Type': 'multipart/form-data'  // Optional - axios sets this automatically
    }
});
```

#### HTML Form:
```html
<form action="/api/data/upload-csv" method="post" enctype="multipart/form-data">
    <input type="file" name="file" accept=".csv">
    <button type="submit">Upload</button>
</form>
```

### Testing Endpoints:

1. **Test Upload**: `POST /api/data/test-upload`
   - Simple endpoint to test if file is being received

2. **Flexible Upload**: `POST /api/data/upload-csv-flexible` 
   - More detailed error messages
   - Better debugging information

3. **Analyze CSV**: `POST /api/data/analyze-csv`
   - Just analyzes structure without saving

### Debugging Steps:

1. First test with: `POST /api/data/test-upload`
2. If that works, try: `POST /api/data/upload-csv-flexible`
3. Check server logs for detailed error information
4. Verify file field name is exactly 'file'
5. Ensure multipart/form-data encoding

### cURL Testing:
```bash
curl -X POST -F "file=@your_file.csv" http://localhost:8000/api/data/test-upload
```