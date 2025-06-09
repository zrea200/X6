import os
from pathlib import Path
from typing import Optional
import PyPDF2
import docx
import markdown
from bs4 import BeautifulSoup

class FileProcessor:
    """文件处理器"""
    
    def extract_text(self, file_path: str) -> str:
        """从文件中提取文本内容"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_extension in ['.doc', '.docx']:
            return self._extract_from_docx(file_path)
        elif file_extension == '.txt':
            return self._extract_from_txt(file_path)
        elif file_extension == '.md':
            return self._extract_from_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """从PDF文件提取文本"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
        
        return text.strip()
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """从Word文档提取文本"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")
    
    def _extract_from_txt(self, file_path: Path) -> str:
        """从文本文件提取内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    return file.read().strip()
            except Exception as e:
                raise Exception(f"Error reading text file: {str(e)}")
        except Exception as e:
            raise Exception(f"Error extracting text from TXT: {str(e)}")
    
    def _extract_from_markdown(self, file_path: Path) -> str:
        """从Markdown文件提取文本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
            
            # 转换为HTML然后提取纯文本
            html = markdown.markdown(md_content)
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text().strip()
        except Exception as e:
            raise Exception(f"Error extracting text from Markdown: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> list:
        """将文本分块"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # 如果不是最后一块，尝试在句号或换行符处分割
            if end < len(text):
                # 向后查找句号或换行符
                for i in range(end, max(start + chunk_size // 2, end - 100), -1):
                    if text[i] in '.。\n':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
