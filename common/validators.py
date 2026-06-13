import re
from common.exceptions import (
    InvalidFileFormatError, FileSizeTooLargeError
)

class ResumeValidator:
    MAX_SIZE_BYTES = 5 * 1024 * 1024   # 5 MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    
    def validate(self, uploaded_file):
        self._validate_extension(uploaded_file.name)
        self._validate_size(uploaded_file.size)
        return True
    
    def _validate_extension(self, filename: str):
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in self.ALLOWED_EXTENSIONS:
            raise InvalidFileFormatError(
                f"File type '.{ext}' not supported. "
                f"Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
    
    def _validate_size(self, size: int):
        if size > self.MAX_SIZE_BYTES:
            raise FileSizeTooLargeError(
                f"File size {size//1024}KB exceeds 5MB limit."
            )


class CandidateValidator:
    def validate_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError(f"Invalid email address: {email}")
        return True
    
    def validate_phone(self, phone: str) -> bool:
        cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
        if not cleaned.isdigit() or not (7 <= len(cleaned) <= 15):
            raise ValueError(f"Invalid phone number: {phone}")
        return True
    
    def validate_experience(self, years) -> bool:
        try:
            y = float(years)
        except (ValueError, TypeError):
            raise ValueError("Experience must be a number.")
        if y < 0 or y > 60:
            raise ValueError("Experience must be between 0 and 60 years.")
        return True
    
    def validate_name(self, name: str) -> bool:
        if not name or len(name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters.")
        if len(name) > 200:
            raise ValueError("Name must not exceed 200 characters.")
        return True


class JobValidator:
    def validate_title(self, title: str) -> bool:
        if not title or len(title.strip()) < 3:
            raise ValueError("Job title must be at least 3 characters.")
        return True
    
    def validate_min_experience(self, value) -> bool:
        try:
            v = float(value)
        except (ValueError, TypeError):
            raise ValueError("Minimum experience must be a number.")
        if v < 0 or v > 50:
            raise ValueError("Minimum experience must be between 0 and 50.")
        return True
    
    def validate_skills_list(self, skills: list) -> bool:
        if not skills:
            raise ValueError("At least one required skill must be specified.")
        return True
