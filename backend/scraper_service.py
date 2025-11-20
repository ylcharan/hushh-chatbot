import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
import os
import mimetypes
from urllib.parse import urlparse, urljoin
import re
from datetime import datetime
import PyPDF2
import docx
import csv
import json
from io import BytesIO

class ScraperService:
    """
    Service for scraping and processing different types of content sources:
    1. Text content (direct text input)
    2. Website URLs (web scraping)
    3. Files (PDF, DOCX, TXT, CSV, JSON, etc.)
    """
    
    def __init__(self):
        """Initialize the scraper service"""
        self.supported_file_types = {
            'text': ['.txt', '.md', '.log'],
            'document': ['.pdf', '.docx', '.doc'],
            'data': ['.csv', '.json', '.xml'],
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.html', '.css']
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def process_text_content(self, text: str, title: str = None) -> Dict:
        """
        Process direct text content
        
        Args:
            text: The text content to process
            title: Optional title for the content
            
        Returns:
            Dict with processed content and metadata
        """
        if not text or not text.strip():
            raise ValueError("Text content cannot be empty")
        
        # Clean and normalize text
        cleaned_text = self._clean_text(text)
        
        # Generate title if not provided
        if not title:
            title = self._generate_title_from_text(cleaned_text)
        
        return {
            'title': title,
            'content': cleaned_text,
            'source_type': 'text',
            'source_url': None,
            'metadata': {
                'length': len(cleaned_text),
                'word_count': len(cleaned_text.split()),
                'processed_at': datetime.now().isoformat()
            }
        }
    
    def scrape_website(self, url: str, max_depth: int = 1, 
                       extract_links: bool = False) -> List[Dict]:
        """
        Scrape content from a website URL
        
        Args:
            url: The URL to scrape
            max_depth: How many levels deep to follow links (0 = only this page)
            extract_links: Whether to extract and follow internal links
            
        Returns:
            List of dicts with scraped content and metadata
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")
        
        # Validate URL
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        results = []
        visited_urls = set()
        urls_to_visit = [(url, 0)]  # (url, depth)
        
        while urls_to_visit:
            current_url, depth = urls_to_visit.pop(0)
            
            if current_url in visited_urls or depth > max_depth:
                continue
            
            visited_urls.add(current_url)
            
            try:
                # Fetch the webpage
                response = requests.get(current_url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title = self._extract_title(soup, current_url)
                
                # Extract main content
                content = self._extract_content(soup)
                
                if content:
                    results.append({
                        'title': title,
                        'content': content,
                        'source_type': 'url',
                        'source_url': current_url,
                        'metadata': {
                            'scraped_at': datetime.now().isoformat(),
                            'status_code': response.status_code,
                            'content_type': response.headers.get('content-type', ''),
                            'depth': depth
                        }
                    })
                
                # Extract links for deeper scraping
                if extract_links and depth < max_depth:
                    links = self._extract_links(soup, current_url)
                    for link in links:
                        if link not in visited_urls:
                            urls_to_visit.append((link, depth + 1))
            
            except requests.RequestException as e:
                print(f"Error scraping {current_url}: {e}")
                results.append({
                    'title': f"Error: {current_url}",
                    'content': f"Failed to scrape: {str(e)}",
                    'source_type': 'url',
                    'source_url': current_url,
                    'metadata': {
                        'error': str(e),
                        'scraped_at': datetime.now().isoformat()
                    }
                })
        
        return results
    
    def process_file(self, file_path: str = None, file_content: bytes = None, 
                    filename: str = None) -> Dict:
        """
        Process a file and extract its content
        
        Args:
            file_path: Path to the file (for local files)
            file_content: File content as bytes (for uploaded files)
            filename: Name of the file
            
        Returns:
            Dict with extracted content and metadata
        """
        if file_path:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            filename = filename or os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                file_content = f.read()
        
        if not file_content:
            raise ValueError("No file content provided")
        
        if not filename:
            raise ValueError("Filename is required")
        
        # Get file extension
        _, ext = os.path.splitext(filename.lower())
        
        # Process based on file type
        if ext in self.supported_file_types['text'] or ext in self.supported_file_types['code']:
            content = self._process_text_file(file_content)
        elif ext == '.pdf':
            content = self._process_pdf(file_content)
        elif ext in ['.docx', '.doc']:
            content = self._process_docx(file_content)
        elif ext == '.csv':
            content = self._process_csv(file_content)
        elif ext == '.json':
            content = self._process_json(file_content)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        # Generate title from filename
        title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
        
        return {
            'title': title,
            'content': content,
            'source_type': 'file',
            'source_url': None,
            'metadata': {
                'filename': filename,
                'file_type': ext,
                'file_size': len(file_content),
                'processed_at': datetime.now().isoformat()
            }
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', '', text)
        return text.strip()
    
    def _generate_title_from_text(self, text: str, max_length: int = 50) -> str:
        """Generate a title from text content"""
        # Take first sentence or first N characters
        first_sentence = text.split('.')[0]
        if len(first_sentence) > max_length:
            return first_sentence[:max_length] + "..."
        return first_sentence
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate if a string is a valid URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extract title from HTML"""
        # Try different title sources
        title = None
        
        # Try <title> tag
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        
        # Try <h1> tag
        if not title:
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text().strip()
        
        # Try og:title meta tag
        if not title:
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                title = og_title['content'].strip()
        
        # Fallback to URL
        if not title:
            title = urlparse(url).path.split('/')[-1] or urlparse(url).netloc
        
        return title
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML"""
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            script.decompose()
        
        # Try to find main content areas
        main_content = None
        
        # Try common content containers
        for selector in ['main', 'article', '[role="main"]', '.content', '#content', '.post', '.article']:
            content_elem = soup.select_one(selector)
            if content_elem:
                main_content = content_elem
                break
        
        # Fallback to body
        if not main_content:
            main_content = soup.body
        
        if not main_content:
            return ""
        
        # Extract text
        text = main_content.get_text(separator='\n', strip=True)
        
        # Clean up
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        return self._clean_text(text)
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract internal links from HTML"""
        links = set()
        base_domain = urlparse(base_url).netloc
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Only include links from the same domain
            if urlparse(absolute_url).netloc == base_domain:
                # Remove fragments and query parameters for deduplication
                clean_url = absolute_url.split('#')[0].split('?')[0]
                links.add(clean_url)
        
        return list(links)
    
    def _process_text_file(self, file_content: bytes) -> str:
        """Process text-based files"""
        try:
            # Try UTF-8 first
            text = file_content.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback to latin-1
            text = file_content.decode('latin-1', errors='ignore')
        
        return self._clean_text(text)
    
    def _process_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF files"""
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            full_text = '\n'.join(text_parts)
            return self._clean_text(full_text)
        
        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}")
    
    def _process_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX files"""
        try:
            doc_file = BytesIO(file_content)
            doc = docx.Document(doc_file)
            
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            full_text = '\n'.join(text_parts)
            return self._clean_text(full_text)
        
        except Exception as e:
            raise ValueError(f"Error processing DOCX: {str(e)}")
    
    def _process_csv(self, file_content: bytes) -> str:
        """Convert CSV to readable text"""
        try:
            text = file_content.decode('utf-8')
            csv_reader = csv.DictReader(text.splitlines())
            
            rows = list(csv_reader)
            if not rows:
                return "Empty CSV file"
            
            # Format as readable text
            text_parts = [f"CSV Data with {len(rows)} rows:\n"]
            
            for i, row in enumerate(rows[:100], 1):  # Limit to first 100 rows
                row_text = f"Row {i}: " + ", ".join([f"{k}: {v}" for k, v in row.items()])
                text_parts.append(row_text)
            
            if len(rows) > 100:
                text_parts.append(f"... and {len(rows) - 100} more rows")
            
            return '\n'.join(text_parts)
        
        except Exception as e:
            raise ValueError(f"Error processing CSV: {str(e)}")
    
    def _process_json(self, file_content: bytes) -> str:
        """Convert JSON to readable text"""
        try:
            text = file_content.decode('utf-8')
            data = json.loads(text)
            
            # Format JSON as readable text
            formatted = json.dumps(data, indent=2)
            return f"JSON Data:\n{formatted}"
        
        except Exception as e:
            raise ValueError(f"Error processing JSON: {str(e)}")
    
    def get_supported_file_types(self) -> Dict[str, List[str]]:
        """Get list of supported file types"""
        return self.supported_file_types
    
    def validate_source(self, source_type: str, source_data: str) -> Tuple[bool, str]:
        """
        Validate a source before processing
        
        Args:
            source_type: Type of source ('text', 'url', 'file')
            source_data: The source data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if source_type == 'text':
            if not source_data or not source_data.strip():
                return False, "Text content cannot be empty"
            if len(source_data) < 10:
                return False, "Text content is too short (minimum 10 characters)"
            return True, ""
        
        elif source_type == 'url':
            if not self._is_valid_url(source_data):
                return False, "Invalid URL format"
            return True, ""
        
        elif source_type == 'file':
            if not source_data:
                return False, "Filename is required"
            _, ext = os.path.splitext(source_data.lower())
            all_supported = []
            for types in self.supported_file_types.values():
                all_supported.extend(types)
            if ext not in all_supported:
                return False, f"Unsupported file type: {ext}"
            return True, ""
        
        else:
            return False, f"Unknown source type: {source_type}"

