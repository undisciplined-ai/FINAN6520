# pdfplumber Quick Reference

## Open PDF
```python
import pdfplumber

with pdfplumber.open('path/to/file.pdf') as pdf:
    # Work with pdf object
```

## Iterate Pages
```python
for page_num, page in enumerate(pdf.pages, start=1):
    text = page.extract_text()
    # Process text
```

## Page Metadata
```python
page.width
page.height
page.page_number
```

## Text Extraction
```python
text = page.extract_text()  # Returns string
```

## Error Handling
```python
text = page.extract_text()
if text is None:
    text = ""  # Handle empty pages
```
